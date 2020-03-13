#=========================================================================
# Accumulator Xcel Unit RTL Model
#=========================================================================
# Accumulates values in a vector in memory.
# Accelerator register interface:
#
#  xr0 : go/done
#  xr1 : base address of the array src
#  xr2 : size of the array
#
# Accelerator protocol involves the following steps:
#  1. Write the base address of src to xr1
#  2. Write the number of elements in the array to xr2
#  3. Tell accelerator to go by writing xr0
#  4. Wait for accelerator to finish by reading xr0, result will be sum

from pymtl3      import *

from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMinionIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs  import MemMasterIfcRTL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.rtl  import BypassQueueRTL, PipeQueueRTL, Reg

from proc.XcelMsg import *

class AccumXcelPRTL( Component ):

  # Constructor

  def construct( s ):

    MemReqMsg, MemRespMsg = mk_mem_msg( 8,32,32 )
    MEM_TYPE_READ  = b4(MemMsgType.READ)
    MEM_TYPE_WRITE = b4(MemMsgType.WRITE)

    # Interface

    s.xcel = XcelMinionIfcRTL( XcelReqMsg, XcelRespMsg )

    s.mem  = MemMasterIfcRTL( MemReqMsg, MemRespMsg )

    # Queues

    s.xcelreq_q = PipeQueueRTL( XcelReqMsg, 1 )( enq = s.xcel.req )
    s.memresp_q = PipeQueueRTL( MemRespMsg, 1 )( enq = s.mem.resp )

    # Internal state

    s.base_src      = Reg( Bits32 )
    s.size          = Reg( Bits32 )
    s.idx           = Reg( Bits32 )
    s.result        = Reg( Bits32 )

    #=====================================================================
    # State Update
    #=====================================================================

    s.STATE_XCFG    = b8(0)
    s.STATE_M_RD    = b8(1)
    s.STATE_CALC    = b8(2)

    s.state         = Wire(Bits8)
    s.go            = Wire()

    @s.update_ff
    def block0():

      if s.reset:
        s.state <<= s.STATE_XCFG
      else:
        s.state <<= s.state

        if s.state == s.STATE_XCFG:

          # ''' SECTION TASK '''''''''''''''''''''''''''''''''''''''''''''
          # Add the state transition logic for XCFG state.
          # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        elif s.state == s.STATE_M_RD:
          if s.mem.req.rdy:
            s.state <<= s.STATE_CALC

        elif s.state == s.STATE_CALC:
          if s.memresp_q.deq.rdy:
            if s.idx.out < s.size.out - b32(1):
              s.state <<= s.STATE_M_RD
            else:
              s.state <<= s.STATE_XCFG

    #=====================================================================
    # State Outputs
    #=====================================================================

    @s.update
    def block1():

      s.xcelreq_q.deq.en = b1(0)
      s.xcel.resp.en     = b1(0)
      s.mem.req.en       = b1(0)
      s.memresp_q.deq.en = b1(0)
      s.go               = b1(0)

      s.base_src.in_ = s.base_src.out
      s.size.in_     = s.size.out
      s.idx.in_      = s.idx.out
      s.result.in_   = s.result.out

      #-------------------------------------------------------------------
      # STATE: XCFG
      #-------------------------------------------------------------------
      # In this state we handle the accelerator configuration protocol,
      # where we write the base addresses, size, and then tell the
      # accelerator to start. We also handle responding when the
      # accelerator is done.

      if s.state == s.STATE_XCFG:

        if s.xcelreq_q.deq.rdy & s.xcel.resp.rdy:
          s.xcelreq_q.deq.en = b1(1)
          s.xcel.resp.en     = b1(1)

          if s.xcelreq_q.deq.ret.type_ == XCEL_TYPE_WRITE:

            if   s.xcelreq_q.deq.ret.addr == b5(0):
              s.go         = b1(1)
              s.idx.in_    = b32(0)
              s.result.in_ = b32(0)

            elif s.xcelreq_q.deq.ret.addr == b5(1):
              s.base_src.in_ = s.xcelreq_q.deq.ret.data

            elif s.xcelreq_q.deq.ret.addr == b5(2):
              s.size.in_ = s.xcelreq_q.deq.ret.data

            # Send xcel response message

            s.xcel.resp.msg = XcelRespMsg( XCEL_TYPE_WRITE, b32(0) )

          else:

            # Send xcel response message, obviously you only want to
            # send the response message when accelerator is done

            s.xcel.resp.msg = XcelRespMsg( XCEL_TYPE_READ, s.result.out )

      #-------------------------------------------------------------------
      # STATE: M_RD
      #-------------------------------------------------------------------
      # Memory read stage. Send memory request to read src[i].

      elif s.state == s.STATE_M_RD:
        if s.mem.req.rdy:
          s.mem.req.en  = b1(1)
          s.mem.req.msg = MemReqMsg( MEM_TYPE_READ, b8(0), s.base_src.out + 4*s.idx.out, b2(0), b32(0) )

      #-------------------------------------------------------------------
      # STATE: CALC
      #-------------------------------------------------------------------
      # Wait for memory response to come back, then do accumulate.

      elif s.state == s.STATE_CALC:

        if s.memresp_q.deq.rdy:
          s.memresp_q.deq.en = b1(1)
          s.result.in_ = s.result.out + s.memresp_q.deq.ret.data

          # if idx < size - 1, still not through entire vector
          if s.idx.out < s.size.out - b32(1):
            s.idx.in_ = s.idx.out + b32(1)
          else:
            s.idx.in_ = b32(0)

  # Line tracing

  def line_trace( s ):

    s.trace = ""

    state2char = {
      s.STATE_XCFG    : "X ",
      s.STATE_M_RD    : "RD",
      s.STATE_CALC    : "C ",
    }

    s.state_str = state2char[s.state]

    s.trace = "{}({} {}|{} {}){}".format(
      s.xcel.req,
      s.state_str,
      s.result.out,
      s.mem.req,
      s.mem.resp,
      s.xcel.resp
    )

    return s.trace
