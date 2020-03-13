#=========================================================================
# CalcShamtPRTL
#=========================================================================
# Looking at least significant eight bits, calculate how many bits we
# want to shift.

from pymtl3 import *

class IntMulVarLatCalcShamtPRTL( Component ):

  # Constructor

  def construct( s ):

    s.in_ = InPort  (Bits8)
    s.out = OutPort (Bits4)

    @s.update
    def block():
      s.out = b4(1)

      if   s.in_ == b8(0): s.out = b4(8)
      elif s.in_[0]:       s.out = b4(1)
      elif s.in_[1]:       s.out = b4(1)
      elif s.in_[2]:       s.out = b4(2)
      elif s.in_[3]:       s.out = b4(3)
      elif s.in_[4]:       s.out = b4(4)
      elif s.in_[5]:       s.out = b4(5)
      elif s.in_[6]:       s.out = b4(6)
      elif s.in_[7]:       s.out = b4(7)

  # Line tracing

  def line_trace( s ):
    return "{}(){}".format( s.in_, s.out )

