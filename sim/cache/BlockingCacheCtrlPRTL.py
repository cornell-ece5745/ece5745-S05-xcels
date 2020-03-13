#=========================================================================
# BlockingCacheCtrlPRTL.py
#=========================================================================

from pymtl3      import *
from pymtl3.stdlib.ifcs import mk_mem_msg

from pymtl3.stdlib.rtl import RegisterFile, RegEnRst
from .DecodeWbenRTL import DecodeWbenRTL

size           = 8192             # Cache size in bytes
p_opaque_nbits = 8

# local parameters not meant to be set from outside

dbw            = 32              # Short name for data bitwidth
abw            = 32              # Short name for addr bitwidth
clw            = 128             # Short name for cacheline bitwidth
nblocks        = size*8//clw      # Number of blocks in the cache
o              = p_opaque_nbits
idw            = clog2(nblocks)-1  # Short name for index width
idw_off        = idw+4

class BlockingCacheCtrlPRTL( Component ):
  def construct( s, idx_shamt = 0 ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Cache request

    s.cachereq_en        = InPort ()
    s.cachereq_rdy       = OutPort()

    # Cache response

    s.cacheresp_en       = OutPort()
    s.cacheresp_rdy      = InPort ()

    # Memory request

    s.memreq_en          = OutPort()
    s.memreq_rdy         = InPort ()

    # Memory response

    s.memresp_en         = InPort ()
    s.memresp_rdy        = OutPort()

    # control signals (ctrl->dpath)

    s.amo_sel            = OutPort( Bits2 )
    s.cachereq_enable    = OutPort()
    s.memresp_enable     = OutPort()
    s.is_refill          = OutPort()
    s.tag_array_0_wen    = OutPort()
    s.tag_array_0_ren    = OutPort()
    s.tag_array_1_wen    = OutPort()
    s.tag_array_1_ren    = OutPort()
    s.way_sel            = OutPort()
    s.way_sel_current    = OutPort()
    s.data_array_wen     = OutPort()
    s.data_array_ren     = OutPort()
    s.skip_read_data_reg = OutPort()

    # width of cacheline divided by number of bits per byte

    s.data_array_wben    = OutPort( mk_bits(clw//8/4) )
    s.read_data_reg_en   = OutPort()
    s.read_tag_reg_en    = OutPort()
    s.read_byte_sel      = OutPort( mk_bits(clog2(clw//dbw)) )
    s.memreq_type        = OutPort( Bits4 )
    s.cacheresp_type     = OutPort( Bits4 )
    s.cacheresp_hit      = OutPort()

    # status signals (dpath->ctrl)

    s.cachereq_type      = InPort ( Bits4 )
    s.cachereq_addr      = InPort ( mk_bits(abw) )
    s.tag_match_0        = InPort ()
    s.tag_match_1        = InPort ()

    #----------------------------------------------------------------------
    # State Definitions
    #----------------------------------------------------------------------

    s.STATE_IDLE                   = b5( 0 )
    s.STATE_TAG_CHECK              = b5( 1 )
    s.STATE_WRITE_CACHE_RESP_HIT   = b5( 2 )
    s.STATE_WRITE_DATA_ACCESS_HIT  = b5( 3 )
    s.STATE_READ_DATA_ACCESS_MISS  = b5( 4 )
    s.STATE_WRITE_DATA_ACCESS_MISS = b5( 5 )
    s.STATE_WAIT_HIT               = b5( 6 )
    s.STATE_WAIT_MISS              = b5( 7 )
    s.STATE_REFILL_REQUEST         = b5( 8 )
    s.STATE_REFILL_WAIT            = b5( 9 )
    s.STATE_REFILL_UPDATE          = b5( 10 )
    s.STATE_EVICT_PREPARE          = b5( 11 )
    s.STATE_EVICT_REQUEST          = b5( 12 )
    s.STATE_EVICT_WAIT             = b5( 13 )
    s.STATE_AMO_READ_DATA_ACCESS   = b5( 14 )
    s.STATE_AMO_WRITE_DATA_ACCESS  = b5( 15 )
    s.STATE_INIT_DATA_ACCESS       = b5( 16 )

    #----------------------------------------------------------------------
    # State Transitions
    #----------------------------------------------------------------------

    s.in_go     = Wire()
    s.out_go    = Wire()
    s.hit_0     = Wire()
    s.hit_1     = Wire()
    s.hit       = Wire()
    s.is_read   = Wire()
    s.is_write  = Wire()
    s.is_init   = Wire()
    s.is_amo    = Wire()
    s.read_hit  = Wire()
    s.write_hit = Wire()
    s.amo_hit   = Wire()
    s.miss_0    = Wire()
    s.miss_1    = Wire()
    s.refill    = Wire()
    s.evict     = Wire()

    @s.update
    def comb_state_transition():
      s.in_go     = s.cachereq_en
      s.out_go    = s.cacheresp_en
      s.hit_0     = s.is_valid_0 & s.tag_match_0
      s.hit_1     = s.is_valid_1 & s.tag_match_1
      s.hit       = s.hit_0 | s.hit_1
      s.is_read   = s.cachereq_type == b4(0)
      s.is_write  = s.cachereq_type == b4(1)
      s.is_init   = s.cachereq_type == b4(2)
      s.is_amo    = s.amo_sel != b2(0)
      s.read_hit  = s.is_read & s.hit
      s.write_hit = s.is_write & s.hit
      s.amo_hit   = s.is_amo & s.hit
      s.miss_0    = ~s.hit_0
      s.miss_1    = ~s.hit_1
      s.refill    = (s.miss_0 & ~s.is_dirty_0 & ~s.lru_way) | \
                    (s.miss_1 & ~s.is_dirty_1 &  s.lru_way)
      s.evict     = (s.miss_0 &  s.is_dirty_0 & ~s.lru_way) | \
                    (s.miss_1 &  s.is_dirty_1 &  s.lru_way)

    # determine amo type

    @s.update
    def comb_amo_type():
      if s.cachereq_type == b4(3): s.amo_sel = b2(1)
      if s.cachereq_type == b4(4): s.amo_sel = b2(2)
      if s.cachereq_type == b4(5): s.amo_sel = b2(3)
      else:                        s.amo_sel = b2(0)

    #----------------------------------------------------------------------
    # State
    #----------------------------------------------------------------------

    s.state      = Wire( Bits5 )
    s.next_state = Wire( Bits5 )

    @s.update_ff
    def reg_state():
      if s.reset:
        s.state <<= s.STATE_IDLE
      else:
        s.state <<= s.next_state

    @s.update
    def comb_next_state():
      s.next_state = s.state

      if s.state == s.STATE_IDLE:
        if s.in_go: s.next_state = s.STATE_TAG_CHECK

      elif s.state == s.STATE_TAG_CHECK:
        if   s.is_init                                       : s.next_state = s.STATE_INIT_DATA_ACCESS
        elif s.read_hit  &  s.cacheresp_rdy &  s.cachereq_en : s.next_state = s.STATE_TAG_CHECK
        elif s.read_hit  &  s.cacheresp_rdy & ~s.cachereq_en : s.next_state = s.STATE_IDLE
        elif s.read_hit  & ~s.cacheresp_rdy                  : s.next_state = s.STATE_WAIT_HIT
        elif s.write_hit &  s.cacheresp_rdy                  : s.next_state = s.STATE_WRITE_DATA_ACCESS_HIT
        elif s.write_hit & ~s.cacheresp_rdy                  : s.next_state = s.STATE_WRITE_CACHE_RESP_HIT
        elif s.amo_hit                                       : s.next_state = s.STATE_AMO_READ_DATA_ACCESS
        elif s.refill                                        : s.next_state = s.STATE_REFILL_REQUEST
        elif s.evict                                         : s.next_state = s.STATE_EVICT_PREPARE

      elif s.state == s.STATE_WRITE_CACHE_RESP_HIT:
        if s.cacheresp_rdy:   s.next_state = s.STATE_WRITE_DATA_ACCESS_HIT

      elif s.state == s.STATE_WRITE_DATA_ACCESS_HIT:
        if s.cachereq_en:     s.next_state = s.STATE_TAG_CHECK
        else:                 s.next_state = s.STATE_IDLE

      elif s.state == s.STATE_READ_DATA_ACCESS_MISS:
        s.next_state = s.STATE_WAIT_MISS

      elif s.state == s.STATE_WRITE_DATA_ACCESS_MISS:
        if (s.cacheresp_rdy):   s.next_state = s.STATE_IDLE
        else:                   s.next_state = s.STATE_WAIT_MISS

      elif s.state == s.STATE_INIT_DATA_ACCESS:
        s.next_state = s.STATE_WAIT_MISS

      elif s.state == s.STATE_AMO_READ_DATA_ACCESS:
        s.next_state = s.STATE_AMO_WRITE_DATA_ACCESS

      elif s.state == s.STATE_AMO_WRITE_DATA_ACCESS:
        s.next_state = s.STATE_WAIT_MISS

      elif s.state == s.STATE_REFILL_REQUEST:
        if   s.memreq_rdy : s.next_state = s.STATE_REFILL_WAIT

      elif s.state == s.STATE_REFILL_WAIT:
        if   s.memresp_en : s.next_state = s.STATE_REFILL_UPDATE

      elif s.state == s.STATE_REFILL_UPDATE:
        if   s.is_read    : s.next_state = s.STATE_READ_DATA_ACCESS_MISS
        elif s.is_write   : s.next_state = s.STATE_WRITE_DATA_ACCESS_MISS
        elif s.is_amo     : s.next_state = s.STATE_AMO_READ_DATA_ACCESS

      elif s.state == s.STATE_EVICT_PREPARE:
        s.next_state = s.STATE_EVICT_REQUEST

      elif s.state == s.STATE_EVICT_REQUEST:
        if   s.memreq_rdy : s.next_state = s.STATE_EVICT_WAIT

      elif s.state == s.STATE_EVICT_WAIT:
        if   s.memresp_en : s.next_state = s.STATE_REFILL_REQUEST

      elif s.state == s.STATE_WAIT_HIT:
        if   s.out_go     : s.next_state = s.STATE_IDLE

      elif s.state == s.STATE_WAIT_MISS:
        if   s.out_go     : s.next_state = s.STATE_IDLE

    #----------------------------------------------------------------------
    # Valid/Dirty bits record
    #----------------------------------------------------------------------

    s.cachereq_idx          = Wire( mk_bits(idw) )
    s.valid_bit_in          = Wire()
    s.valid_bits_write_en   = Wire()
    s.valid_bits_write_en_0 = Wire()
    s.valid_bits_write_en_1 = Wire()
    s.is_valid_0            = Wire()
    s.is_valid_1            = Wire()

    s.cachereq_idx //= s.cachereq_addr[4+idx_shamt:idw_off+idx_shamt]

    @s.update
    def comb_valid_bits_en():
      s.valid_bits_write_en_0 = s.valid_bits_write_en & ~s.way_sel_current
      s.valid_bits_write_en_1 = s.valid_bits_write_en &  s.way_sel_current

    s.valid_bits_0 = RegisterFile( Bits1, nregs=nblocks//2, rd_ports=1, wr_ports=1, const_zero=False )(
      raddr = { 0: s.cachereq_idx },
      rdata = { 0: s.is_valid_0 },
      wen   = { 0: s.valid_bits_write_en_0 },
      waddr = { 0: s.cachereq_idx },
      wdata = { 0: s.valid_bit_in },
    )

    s.valid_bits_1 = RegisterFile( Bits1, nregs=nblocks//2, rd_ports=1, wr_ports=1, const_zero=False )(
      raddr = { 0: s.cachereq_idx },
      rdata = { 0: s.is_valid_1 },
      wen   = { 0: s.valid_bits_write_en_1 },
      waddr = { 0: s.cachereq_idx },
      wdata = { 0: s.valid_bit_in },
    )

    s.dirty_bit_in          = Wire()
    s.dirty_bits_write_en   = Wire()
    s.dirty_bits_write_en_0 = Wire()
    s.dirty_bits_write_en_1 = Wire()
    s.is_dirty_0            = Wire()
    s.is_dirty_1            = Wire()

    @s.update
    def comb_cachereq_idx():
      s.dirty_bits_write_en_0 = s.dirty_bits_write_en & ~s.way_sel_current
      s.dirty_bits_write_en_1 = s.dirty_bits_write_en &  s.way_sel_current

    s.dirty_bits_0 = RegisterFile( Bits1, nregs=nblocks//2, rd_ports=1, wr_ports=1, const_zero=False )(
      raddr = { 0: s.cachereq_idx },
      rdata = { 0: s.is_dirty_0 },
      wen   = { 0: s.dirty_bits_write_en_0 },
      waddr = { 0: s.cachereq_idx },
      wdata = { 0: s.dirty_bit_in },
    )

    s.dirty_bits_1 = RegisterFile( Bits1, nregs=nblocks//2, rd_ports=1, wr_ports=1, const_zero=False )(
      raddr = { 0: s.cachereq_idx },
      rdata = { 0: s.is_dirty_1 },
      wen   = { 0: s.dirty_bits_write_en_1 },
      waddr = { 0: s.cachereq_idx },
      wdata = { 0: s.dirty_bit_in },
    )

    s.lru_bit_in            = Wire()
    s.lru_bits_write_en     = Wire()
    s.lru_way               = Wire()

    s.lru_bits = RegisterFile( Bits1, nregs=nblocks//2, rd_ports=1, wr_ports=1, const_zero=False )(
      raddr = { 0: s.cachereq_idx },
      rdata = { 0: s.lru_way },
      wen   = { 0: s.lru_bits_write_en },
      waddr = { 0: s.cachereq_idx },
      wdata = { 0: s.lru_bit_in },
    )

    #----------------------------------------------------------------------
    # Way selection.
    #   The way is determined in the tag check state, and is
    #   then recorded for the entire transaction
    #----------------------------------------------------------------------

    s.way_record_en = Wire()
    s.way_record_in = Wire()

    @s.update
    def comb_way_select():
      if s.hit:
        if s.hit_0:
          s.way_record_in = b1(0)
        else:
          if s.hit_1:
            s.way_record_in = b1(1)
          else:
            s.way_record_in = b1(0)
      else:
        s.way_record_in = s.lru_way

      if s.state == s.STATE_TAG_CHECK:
        s.way_sel_current = s.way_record_in
      else:
        s.way_sel_current = s.way_sel

    s.way_record = RegEnRst( Bits1, reset_value=0 )(
      en  = s.way_record_en,
      in_ = s.way_record_in,
      out = s.way_sel,
    )

    #----------------------------------------------------------------------
    # State Outputs
    #----------------------------------------------------------------------

    # General parameters
    x       = b1(0)
    y       = b1(1)
    n       = b1(0)

    # Parameters for is_refill
    r_x     = b1(0)
    r_c     = b1(0) # fill data array from _c_ache
    r_m     = b1(1) # fill data array from _m_em

    # Parameters for memreq_type_mux
    m_x     = b4(0)
    m_e     = b4(1)
    m_r     = b4(0)

    s.tag_array_wen = Wire()
    s.tag_array_ren = Wire()
    s.cacheresp_val = Wire()
    s.memreq_val = Wire()

    # Control signal bit slices

    CS_cachereq_rdy        = slice( 20, 21 )
    CS_cacheresp_val       = slice( 19, 20 )
    CS_memreq_val          = slice( 18, 19 )
    CS_memresp_rdy         = slice( 17, 18 )
    CS_cachereq_enable     = slice( 16, 17 )
    CS_memresp_enable      = slice( 15, 16 )
    CS_is_refill           = slice( 14, 15 )
    CS_read_data_reg_en    = slice( 13, 14 )
    CS_read_tag_reg_en     = slice( 12, 13 )
    CS_memreq_type         = slice( 8,  12 ) # 4 bits
    CS_valid_bit_in        = slice( 7,  8  )
    CS_valid_bits_write_en = slice( 6,  7  )
    CS_dirty_bit_in        = slice( 5,  6  )
    CS_dirty_bits_write_en = slice( 4,  5  )
    CS_lru_bits_write_en   = slice( 3,  4  )
    CS_way_record_en       = slice( 2,  3  )
    CS_cacheresp_hit       = slice( 1,  2  )
    CS_skip_read_data_reg  = slice( 0,  1  )

    s.cs = Wire( Bits21 )

    @s.update
    def comb_control_table():
      sr = s.state

      #                                                        $    $    mem mem  $    mem         read read mem  valid valid dirty dirty lru   way    $    skip
      #                                                        req  resp req resp req  resp is     data tag  req  bit   write bit   write write record resp data
      #                                                        rdy  val  val rdy  en   en   refill en   en   type in    en    in    en    en    en     hit  reg
      if   sr == s.STATE_IDLE:                   s.cs = concat( y,   n,   n,  n,   y,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_TAG_CHECK:              s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   y,   n,   m_x, x,    n,    x,    n,    y,    y,     n,   y    )
      elif sr == s.STATE_WRITE_CACHE_RESP_HIT:   s.cs = concat( n,   y,   n,  n,   n,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    y,    n,     y,   n    )
      elif sr == s.STATE_WRITE_DATA_ACCESS_HIT:  s.cs = concat( n,   n,   n,  n,   n,   n,   r_c,   n,   n,   m_x, y,    y,    y,    y,    y,    n,     y,   n    )
      elif sr == s.STATE_READ_DATA_ACCESS_MISS:  s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   y,   n,   m_x, x,    n,    x,    n,    y,    n,     n,   n    )
      elif sr == s.STATE_WRITE_DATA_ACCESS_MISS: s.cs = concat( n,   y,   n,  n,   n,   n,   r_c,   n,   n,   m_x, y,    y,    y,    y,    y,    n,     n,   n    )
      elif sr == s.STATE_INIT_DATA_ACCESS:       s.cs = concat( n,   n,   n,  n,   n,   n,   r_c,   n,   n,   m_x, y,    y,    n,    y,    y,    n,     n,   n    )
      elif sr == s.STATE_AMO_READ_DATA_ACCESS:   s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   y,   n,   m_x, x,    n,    x,    n,    y,    n,     n,   n    )
      elif sr == s.STATE_AMO_WRITE_DATA_ACCESS:  s.cs = concat( n,   n,   n,  n,   n,   n,   r_c,   n,   n,   m_x, y,    y,    y,    y,    y,    n,     n,   n    )
      elif sr == s.STATE_REFILL_REQUEST:         s.cs = concat( n,   n,   y,  n,   n,   n,   r_x,   n,   n,   m_r, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_REFILL_WAIT:            s.cs = concat( n,   n,   n,  y,   n,   y,   r_m,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_REFILL_UPDATE:          s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   n,   n,   m_x, y,    y,    n,    y,    n,    n,     n,   n    )
      elif sr == s.STATE_EVICT_PREPARE:          s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   y,   y,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_EVICT_REQUEST:          s.cs = concat( n,   n,   y,  n,   n,   n,   r_x,   n,   n,   m_e, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_EVICT_WAIT:             s.cs = concat( n,   n,   n,  y,   n,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )
      elif sr == s.STATE_WAIT_HIT:               s.cs = concat( n,   y,   n,  n,   n,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     y,   n    )
      elif sr == s.STATE_WAIT_MISS:              s.cs = concat( n,   y,   n,  n,   n,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )
      else :                                     s.cs = concat( n,   n,   n,  n,   n,   n,   r_x,   n,   n,   m_x, x,    n,    x,    n,    n,    n,     n,   n    )

      # Unpack signals

      s.cachereq_rdy        = s.cs[ CS_cachereq_rdy        ]
      s.cacheresp_val       = s.cs[ CS_cacheresp_val       ]
      s.memreq_val          = s.cs[ CS_memreq_val          ]
      s.memresp_rdy         = s.cs[ CS_memresp_rdy         ]
      s.cachereq_enable     = s.cs[ CS_cachereq_enable     ]
      s.memresp_enable      = s.cs[ CS_memresp_enable      ]
      s.is_refill           = s.cs[ CS_is_refill           ]
      s.read_data_reg_en    = s.cs[ CS_read_data_reg_en    ]
      s.read_tag_reg_en     = s.cs[ CS_read_tag_reg_en     ]
      s.memreq_type         = s.cs[ CS_memreq_type         ]
      s.valid_bit_in        = s.cs[ CS_valid_bit_in        ]
      s.valid_bits_write_en = s.cs[ CS_valid_bits_write_en ]
      s.dirty_bit_in        = s.cs[ CS_dirty_bit_in        ]
      s.dirty_bits_write_en = s.cs[ CS_dirty_bits_write_en ]
      s.lru_bits_write_en   = s.cs[ CS_lru_bits_write_en   ]
      s.way_record_en       = s.cs[ CS_way_record_en       ]
      s.cacheresp_hit       = s.cs[ CS_cacheresp_hit       ]
      s.skip_read_data_reg  = s.cs[ CS_skip_read_data_reg  ]

      s.cacheresp_en = s.cacheresp_val & s.cacheresp_rdy

      # set cacheresp_val when there is a hit for one hit latency
      if (s.read_hit | s.write_hit) and (s.state == s.STATE_TAG_CHECK):
        s.cacheresp_en  = s.cacheresp_rdy
        s.cacheresp_hit = b1(1)

        # if read hit, if can send response, immediately take new cachereq
        if s.read_hit:
          s.cachereq_rdy    = s.cacheresp_rdy
          s.cachereq_enable = s.cacheresp_rdy

      # since cacheresp already handled, can immediately take new cachereq
      elif s.state == s.STATE_WRITE_DATA_ACCESS_HIT:
        s.cachereq_rdy    = b1(1)
        s.cachereq_enable = b1(1)

      s.memreq_en = s.memreq_val & s.memreq_rdy

    # Control bits based on next state

    NS_tag_array_wen  = slice( 3, 4 )
    NS_tag_array_ren  = slice( 2, 3 )
    NS_data_array_wen = slice( 1, 2 )
    NS_data_array_ren = slice( 0, 1 )

    s.ns = Wire( Bits4 )

    @s.update
    def comb_control_table_next():

      # set enable for tag_array and data_array one cycle early (dependant on next_state)
      sn = s.next_state
      #                                                         tag   tag   data  data
      #                                                         array array array array
      #                                                         wen   ren   wen   ren
      if   sn == s.STATE_IDLE:                   s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_TAG_CHECK:              s.ns = concat( n,    y,    n,    y,   )
      elif sn == s.STATE_WRITE_CACHE_RESP_HIT:   s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_WRITE_DATA_ACCESS_HIT:  s.ns = concat( y,    n,    y,    n,   )
      elif sn == s.STATE_READ_DATA_ACCESS_MISS:  s.ns = concat( n,    n,    n,    y,   )
      elif sn == s.STATE_WRITE_DATA_ACCESS_MISS: s.ns = concat( y,    n,    y,    n,   )
      elif sn == s.STATE_INIT_DATA_ACCESS:       s.ns = concat( y,    n,    y,    n,   )
      elif sn == s.STATE_AMO_READ_DATA_ACCESS:   s.ns = concat( n,    n,    n,    y,   )
      elif sn == s.STATE_AMO_WRITE_DATA_ACCESS:  s.ns = concat( y,    n,    y,    n,   )
      elif sn == s.STATE_REFILL_REQUEST:         s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_REFILL_WAIT:            s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_REFILL_UPDATE:          s.ns = concat( y,    n,    y,    n,   )
      elif sn == s.STATE_EVICT_PREPARE:          s.ns = concat( n,    y,    n,    y,   )
      elif sn == s.STATE_EVICT_REQUEST:          s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_EVICT_WAIT:             s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_WAIT_HIT:               s.ns = concat( n,    n,    n,    n,   )
      elif sn == s.STATE_WAIT_MISS:              s.ns = concat( n,    n,    n,    n,   )
      else :                                     s.ns = concat( n,    n,    n,    n,   )

      # Unpack signals

      s.tag_array_wen  = s.ns[ NS_tag_array_wen  ]
      s.tag_array_ren  = s.ns[ NS_tag_array_ren  ]
      s.data_array_wen = s.ns[ NS_data_array_wen ]
      s.data_array_ren = s.ns[ NS_data_array_ren ]

    # lru bit determination
    @s.update
    def comb_lru_bit_in():
      s.lru_bit_in = ~s.way_sel_current

    # tag array enables
    @s.update
    def comb_tag_arry_en():
      s.tag_array_0_wen = s.tag_array_wen & ~s.way_sel_current
      s.tag_array_0_ren = s.tag_array_ren
      s.tag_array_1_wen = s.tag_array_wen &  s.way_sel_current
      s.tag_array_1_ren = s.tag_array_ren

    # Building data_array_wben
    # This is in control because we want to facilitate more complex patterns
    #   when we want to start supporting subword accesses

    s.cachereq_offset  = Wire( Bits2 )
    s.wben_decoder_out = Wire( Bits4 )

    s.cachereq_offset //= s.cachereq_addr[2:4]
    # Choose byte to read from cacheline based on what the offset was
    s.read_byte_sel   //= s.cachereq_addr[2:4]

    @s.update
    def comb_enable_writing():

      # Logic to enable writing of the entire cacheline in case of refill
      # and just one word for writes and init

      if s.is_refill: s.data_array_wben = b4(0xf)
      else          : s.data_array_wben = b4(1) << s.cachereq_offset

      # Managing the cache response type based on cache request type

    s.cacheresp_type //= s.cachereq_type

