#=========================================================================
# BlockingCachePRTL.py
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL, MemMinionIfcRTL
from pymtl3.stdlib.ifcs import mk_mem_msg

from .BlockingCacheCtrlPRTL  import BlockingCacheCtrlPRTL
from .BlockingCacheDpathPRTL import BlockingCacheDpathPRTL

# Note on num_banks:
# In a multi-banked cache design, cache lines are interleaved to
# different cache banks, so that consecutive cache lines correspond to a
# different bank. The following is the addressing structure in our
# four-banked data caches:
#
# +--------------------------+--------------+--------+--------+--------+
# |        22b               |     4b       |   2b   |   2b   |   2b   |
# |        tag               |   index      |bank idx| offset | subwd  |
# +--------------------------+--------------+--------+--------+--------+
#
# In this lab you don't have to consider multi-banked cache design. We
# will compose four-banked cache in lab5 multi-core lab. You can modify
# your cache to multi-banked by slightly modifying the address structure.
# For now you can simply assume num_banks == 0.

class BlockingCachePRTL( Component ):

  def construct( s, num_banks = 0 ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32 )
    MemReqType,   MemRespType   = mk_mem_msg( 8, 32, 128 )

    if num_banks <= 0:
      idx_shamt = 0
    else:
      idx_shamt = clog2( num_banks )

    # Proc <-> Cache

    s.cache = MemMinionIfcRTL( CacheReqType, CacheRespType )

    # Cache <-> Mem

    s.mem = MemMasterIfcRTL( MemReqType, MemRespType )

    s.ctrl  = BlockingCacheCtrlPRTL ( idx_shamt )(
      # Cache request
      cachereq_en  = s.cache.req.en,
      cachereq_rdy = s.cache.req.rdy,

      # Cache response
      cacheresp_en  = s.cache.resp.en,
      cacheresp_rdy = s.cache.resp.rdy,

      # Memory request
      memreq_en  = s.mem.req.en,
      memreq_rdy = s.mem.req.rdy,

      # Memory response
      memresp_en  = s.mem.resp.en,
      memresp_rdy = s.mem.resp.rdy,
    )

    s.dpath = BlockingCacheDpathPRTL( idx_shamt )(
      # Cache request
      cachereq_msg = s.cache.req.msg,

      # Cache response
      cacheresp_msg = s.cache.resp.msg,

      # Memory request
      memreq_msg = s.mem.req.msg,

      # Memory response
      memresp_msg = s.mem.resp.msg,

    )

    # control signals (ctrl->dpath)

    s.dpath.amo_sel            //= s.ctrl.amo_sel
    s.dpath.cachereq_enable    //= s.ctrl.cachereq_enable
    s.dpath.memresp_enable     //= s.ctrl.memresp_enable
    s.dpath.is_refill          //= s.ctrl.is_refill
    s.dpath.tag_array_0_wen    //= s.ctrl.tag_array_0_wen
    s.dpath.tag_array_0_ren    //= s.ctrl.tag_array_0_ren
    s.dpath.tag_array_1_wen    //= s.ctrl.tag_array_1_wen
    s.dpath.tag_array_1_ren    //= s.ctrl.tag_array_1_ren
    s.dpath.way_sel            //= s.ctrl.way_sel
    s.dpath.way_sel_current    //= s.ctrl.way_sel_current
    s.dpath.data_array_wen     //= s.ctrl.data_array_wen
    s.dpath.data_array_ren     //= s.ctrl.data_array_ren
    s.dpath.skip_read_data_reg //= s.ctrl.skip_read_data_reg

    # width of cacheline divided by number of bits per byte

    s.dpath.data_array_wben  //= s.ctrl.data_array_wben
    s.dpath.read_data_reg_en //= s.ctrl.read_data_reg_en
    s.dpath.read_tag_reg_en  //= s.ctrl.read_tag_reg_en
    s.dpath.read_byte_sel    //= s.ctrl.read_byte_sel
    s.dpath.memreq_type      //= s.ctrl.memreq_type
    s.dpath.cacheresp_type   //= s.ctrl.cacheresp_type
    s.dpath.cacheresp_hit    //= s.ctrl.cacheresp_hit

    # status signals (dpath->ctrl)

    s.ctrl.cachereq_type //= s.dpath.cachereq_type
    s.ctrl.cachereq_addr //= s.dpath.cachereq_addr
    s.ctrl.tag_match_0   //= s.dpath.tag_match_0
    s.ctrl.tag_match_1   //= s.dpath.tag_match_1

    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  def line_trace( s ):

    #: return ""

    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # LAB TASK: Create line tracing
    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    state = s.ctrl.state

    if   state == s.ctrl.STATE_IDLE:                   state_str = "(I )"
    elif state == s.ctrl.STATE_TAG_CHECK:              state_str = "(TC)"
    elif state == s.ctrl.STATE_WRITE_CACHE_RESP_HIT:   state_str = "(WR)"
    elif state == s.ctrl.STATE_WRITE_DATA_ACCESS_HIT:  state_str = "(WD)"
    elif state == s.ctrl.STATE_READ_DATA_ACCESS_MISS:  state_str = "(RD)"
    elif state == s.ctrl.STATE_WRITE_DATA_ACCESS_MISS: state_str = "(WD)"
    elif state == s.ctrl.STATE_AMO_READ_DATA_ACCESS:   state_str = "(AR)"
    elif state == s.ctrl.STATE_AMO_WRITE_DATA_ACCESS:  state_str = "(AW)"
    elif state == s.ctrl.STATE_INIT_DATA_ACCESS:       state_str = "(IN)"
    elif state == s.ctrl.STATE_REFILL_REQUEST:         state_str = "(RR)"
    elif state == s.ctrl.STATE_REFILL_WAIT:            state_str = "(RW)"
    elif state == s.ctrl.STATE_REFILL_UPDATE:          state_str = "(RU)"
    elif state == s.ctrl.STATE_EVICT_PREPARE:          state_str = "(EP)"
    elif state == s.ctrl.STATE_EVICT_REQUEST:          state_str = "(ER)"
    elif state == s.ctrl.STATE_EVICT_WAIT:             state_str = "(EW)"
    elif state == s.ctrl.STATE_WAIT_HIT:               state_str = "(W )"
    elif state == s.ctrl.STATE_WAIT_MISS:              state_str = "(W )"
    else :                                             state_str = "(? )"

    return state_str

    #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

