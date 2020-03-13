#=======================================================================
# DropUnit.py
#=======================================================================

from pymtl3 import *
from pymtl3.stdlib.ifcs import GetIfcRTL, GiveIfcRTL
from pymtl3.stdlib.rtl  import RegRst

# State Constants

SNOOP = b1(0)
WAIT  = b1(1)

#-------------------------------------------------------------------------
# DropUnit
#-------------------------------------------------------------------------
# Drop Unit drops a transaction between any two models connected by
# using the en-rdy handshake protocol. It receives a drop signal as an
# input and if the drop signal is high, it will drop the next message
# it sees.

class DropUnitPRTL( Component ):

  def construct( s, dtype ):

    s.drop = InPort()
    s.in_  = GetIfcRTL( dtype )
    s.out  = GiveIfcRTL( dtype )

    s.out.ret //= s.in_.ret

    s.snoop_state = Wire()

    #------------------------------------------------------------------
    # state_transitions
    #------------------------------------------------------------------

    @s.update_ff
    def state_transitions():

      if s.reset:
        s.snoop_state <<= SNOOP

      elif s.snoop_state == SNOOP:
        if s.drop & ~s.in_.rdy:
          s.snoop_state <<= WAIT

      elif s.snoop_state == WAIT:
        if s.in_.rdy:
          s.snoop_state <<= SNOOP

    #------------------------------------------------------------------
    # set_outputs
    #------------------------------------------------------------------

    @s.update
    def set_outputs():
      s.out.rdy = b1(0)
      s.in_.en  = b1(0)

      if   s.snoop_state == SNOOP:
        s.out.rdy = s.in_.rdy & ~s.drop
        s.in_.en  = s.out.en

      elif s.snoop_state == WAIT:
        s.out.rdy = b1(0)
        s.in_.en  = s.in_.rdy
