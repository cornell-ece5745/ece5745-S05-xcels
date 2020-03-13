#=========================================================================
# Integer Multiplier Fixed-Lateny CL Model
#=========================================================================
# Simple CL model for a fixed-latency iterative multiplier which is
# assumed to take 35 cycles.

from pymtl3      import *
from pymtl3.stdlib.cl import PipeQueueCL
from pymtl3.stdlib.ifcs import MinionIfcCL
from .IntMulMsgs import IntMulMsgs

class IntMulFixedLatCL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.minion = MinionIfcCL( IntMulMsgs.req, IntMulMsgs.resp )

    s.req_q = PipeQueueCL(1)( enq = s.minion.req )

    # Member variables

    s.result   = None
    s.counter  = 0

    # Update block

    @s.update
    def block():
      if s.result is None and s.req_q.deq.rdy():
        msg = s.req_q.deq()
        s.result = msg.a * msg.b
        s.counter = 32
      elif s.counter > 0:
        s.counter -= 1
      elif s.counter == 0 and s.result is not None:
        if s.minion.resp.rdy():
          s.minion.resp( s.result )
          s.result = None

  # Line tracing

  def line_trace( s ):
    return f"({s.counter:2})"

