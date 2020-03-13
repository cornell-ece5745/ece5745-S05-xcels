#=========================================================================
# Integer Multiplier N-Stage Pipelined CL Model
#=========================================================================
# Simple CL model for a pipelined integer multiplier with a variable
# number of stages.

from collections import deque

from pymtl3 import *
from pymtl3.stdlib.cl   import DelayPipeCL
from pymtl3.stdlib.ifcs import MinionIfcCL
from .IntMulMsgs        import IntMulMsgs

class IntMulNstageCL( Component ):

  # Constructor

  def construct( s, nstages=2 ):

    # Interface

    s.minion = MinionIfcCL( IntMulMsgs.req, IntMulMsgs.resp )

    # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Define Nstage cycle-level model.
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # Member variables

    s.pipe = DelayPipeCL(delay=nstages)( enq=s.minion.req )

    # Concurrent block

    @s.update
    def block():
      if s.pipe.deq.rdy() and s.minion.resp.rdy():
        msg = s.pipe.deq()
        s.minion.resp( msg.a * msg.b )

    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  # Line tracing

  def line_trace( s ):

    s.trace = ""

    # ''' LAB TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Add line tracing code here.
    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    s.trace = f"({s.pipe.line_trace()})"

    # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    return s.trace

