#=========================================================================
# Accumulator Xcel Unit CL Model
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

from copy import deepcopy

from pymtl3     import *

from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMinionIfcCL
from pymtl3.stdlib.ifcs.mem_ifcs  import MemMasterIfcCL, mk_mem_msg, MemMsgType
from pymtl3.stdlib.cl  import PipeQueueCL

from proc.XcelMsg import *

class AccumXcelCL( Component ):

  # Constructor

  def construct( s ):

    MemReqMsg, MemRespMsg = mk_mem_msg( 8,32,32 )

    # Interface

    s.xcel = XcelMinionIfcCL( XcelReqMsg, XcelRespMsg )

    s.mem  = MemMasterIfcCL( *mk_mem_msg(8,32,32) )

    # Components

    s.xcelreq_q = PipeQueueCL( num_entries=1 )( enq = s.xcel.req )
    s.memresp_q = PipeQueueCL( num_entries=1 )( enq = s.mem.resp )

    # Internal state

    s.base_src      = b32(0)
    s.size          = 0

    s.idx           = 0
    s.result        = 0

    # State

    s.STATE_XCFG    = 0
    s.STATE_M_RD    = 1
    s.STATE_CALC    = 2
    s.state         = s.STATE_XCFG

    # Line tracing

    s.state_str     = "  "

    # Concurrent block

    @s.update
    def block():

      #-------------------------------------------------------------------
      # STATE: XCFG
      #-------------------------------------------------------------------
      # In this state we handle the accelerator configuration protocol,
      # where we write the base addresses, size, and then tell the
      # accelerator to start. We also handle responding when the
      # accelerator is done.

      if s.state == s.STATE_XCFG:
        s.state_str = "  "
        if s.xcelreq_q.deq.rdy() and s.xcel.resp.rdy():

          xcelreq_msg = s.xcelreq_q.deq()

          if xcelreq_msg.type_ == XCEL_TYPE_WRITE:

            assert xcelreq_msg.addr in [0,1,2], \
              "Only reg writes to 0,1,2 allowed during setup!"

            if   xcelreq_msg.addr == 0:
              s.state_str = "X0"
              s.result    = 0
              s.state     = s.STATE_M_RD

            elif xcelreq_msg.addr == 1:
              s.state_str = "X1"
              s.base_src  = xcelreq_msg.data.uint()

            elif xcelreq_msg.addr == 2:
              s.state_str = "X2"
              s.size = xcelreq_msg.data.uint()

            # Send xcel response message

            s.xcel.resp( XcelRespMsg(XCEL_TYPE_WRITE, 0) )

          else:
            s.state_str = "x0"

            assert xcelreq_msg.addr == 0

            # Send xcel response message, obviously you only want to
            # send the response message when accelerator is done

            s.xcel.resp( XcelRespMsg(XCEL_TYPE_READ, s.result) )

      #-------------------------------------------------------------------
      # STATE: M_RD
      #-------------------------------------------------------------------
      # Memory read stage. Send memory request to read src[i].

      elif s.state == s.STATE_M_RD:
        s.state_str = "R "
        if s.mem.req.rdy():
          s.state_str = "R>"
          s.mem.req( MemReqMsg( MemMsgType.READ, 0, s.base_src+4*s.idx, 0 ) )
          s.state = s.STATE_CALC

      #-------------------------------------------------------------------
      # STATE: CALC
      #-------------------------------------------------------------------
      # Wait for memory response to come back, then do accumulate.

      elif s.state == s.STATE_CALC:
        s.state_str = "C "
        if s.memresp_q.deq.rdy():
          s.state_str = "C+"
          read_data = deepcopy( s.memresp_q.deq().data )
          s.result += read_data
          print(s.result)

          # if idx < size, still not through entire vector
          if s.idx < s.size:
            s.state = s.STATE_M_RD
            s.idx = s.idx + 1
          else:
            s.state = s.STATE_XCFG
            s.idx = 0

  # Line tracing

  def line_trace( s ):

    s.trace = "{}({}|{} {}){}".format(
      s.xcel.req,
      s.state_str,
      s.mem.req,
      s.mem.resp,
      s.xcel.resp
    )

    return s.trace
