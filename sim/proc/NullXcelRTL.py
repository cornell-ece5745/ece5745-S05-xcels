#=========================================================================
# Null Accelerator Model
#=========================================================================
# This is an empty accelerator model. It includes a single 32-bit
# register named xr0 for testing purposes. It includes a memory
# interface, but this memory interface is not used. The model is
# synthesizable and can be combined with an processor RTL model.
#
# We use a two-input normal queue to buffer up the xcelreq. This
# eliminates any combinational loops when composing the accelerator with
# the processor. We combinationally connect the en/rdy from the dequeue
# interface of the xcelreq queue to the xcelresp interface. Essentially,
# an xcelreq is buffered up and waits in the queue until the xcelresp
# interface is ready to accept it.
#
# We directly connect the data from an xcelreq to the input of the xr0
# register, and ideally we would directly connect the output of the xr0
# register to the data of an xcelresp; this would work fine because there
# is only a single accelerator register. So if we are reading or writing
# an accelerator register it must be that one. There is one catch though.
# We don't really have wildcards in our test sources, so it is easier if
# we force the xcelresp data to zero on a write. So we have a little bit
# of muxing to do this.
#
# The final part is that we need to figure out when to set the enable on
# the xr0 register. This register is enabled when the transaction at the
# head of the xcelreq queue is a write and when the xcelresp interface is
# ready.
#

from pymtl3 import *
from pymtl3.stdlib.ifcs.mem_ifcs  import MemMasterIfcRTL, mk_mem_msg
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMinionIfcRTL
from pymtl3.stdlib.rtl  import NormalQueueRTL, RegEn

from .XcelMsg import XcelReqMsg, XcelRespMsg, XCEL_TYPE_READ, XCEL_TYPE_WRITE

class NullXcelRTL( Component ):

  # Constructor

  def construct( s, nbits=32 ):
    dtype = mk_bits(nbits)

    # Interface

    s.xcel = XcelMinionIfcRTL( XcelReqMsg, XcelRespMsg )
    s.mem  = MemMasterIfcRTL( *mk_mem_msg(8,nbits,32) )

    # Queues

    s.xcelreq_q = NormalQueueRTL( XcelReqMsg, 2 )( enq = s.xcel.req )

    # Single accelerator register

    s.xr0 = RegEn( Bits32 )

    # Direct connections for xcelreq/xcelresp

    s.xr0.in_             //= s.xcelreq_q.deq.ret.data
    s.xcel.resp.msg.type_ //= s.xcelreq_q.deq.ret.type_

    # Even though memreq/memresp interface is not hooked up, we still
    # need to set the output ports correctly.

    s.mem.req.en   //= 0
    s.mem.req.msg  //= mk_mem_msg(8,nbits,32)[0]()
    s.mem.resp.rdy //= 0

    # Combinational block

    @s.update
    def block():

      # Mux to force xcelresp data to zero on a write

      if s.xcelreq_q.deq.ret.type_ == XCEL_TYPE_WRITE:
        s.xcel.resp.msg.data = dtype(0)
      else:
        s.xcel.resp.msg.data = s.xr0.out

      # Logic for register enable
      both_rdy = s.xcelreq_q.deq.rdy & s.xcel.resp.rdy

      s.xr0.en = (s.xcelreq_q.deq.ret.type_ == XCEL_TYPE_WRITE) & both_rdy

      s.xcelreq_q.deq.en = both_rdy
      s.xcel.resp.en     = both_rdy

  # Line tracing

  def line_trace( s ):
    return f"{s.xcel}"

