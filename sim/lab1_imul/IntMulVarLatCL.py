#=========================================================================
# Integer Multiplier Variable-Lateny CL Model
# =========================================================================
# Simple CL model for a variable-latency iterative multiplier. We
# optimistically assume that the number of cycles is equal to the number
# of ones in the b operand.

from pymtl3 import *
from pymtl3.stdlib.cl   import PipeQueueCL
from pymtl3.stdlib.ifcs import MinionIfcCL
from .IntMulMsgs        import IntMulMsgs

class IntMulVarLatCL( Component ):

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
        s.counter = bin(int(msg.b)).count('1')
      elif s.counter > 0:
        s.counter -= 1
      elif s.counter == 0 and s.result is not None:
        if s.minion.resp.rdy():
          s.minion.resp( s.result )
          s.result = None

  # Line tracing

  def line_trace( s ):
    return f"({s.counter:2})"
