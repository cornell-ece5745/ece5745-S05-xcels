#=========================================================================
# IntMulNstageStepRTL
#=========================================================================

from pymtl3     import *
from pymtl3.stdlib.rtl import Mux, LeftLogicalShifter, RightLogicalShifter, Adder

class IntMulNstageStepPRTL( Component ):

  # Constructor

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_en      = InPort  ()
    s.in_a       = InPort  (Bits32)
    s.in_b       = InPort  (Bits32)
    s.in_result  = InPort  (Bits32)

    s.out_en     = OutPort ()
    s.out_a      = OutPort (Bits32)
    s.out_b      = OutPort (Bits32)
    s.out_result = OutPort (Bits32)

    #---------------------------------------------------------------------
    # Logic
    #---------------------------------------------------------------------

    # Right shifter

    s.rshifter = RightLogicalShifter(Bits32)(
      in_   = s.in_b,
      shamt = 1,
      out   = s.out_b,
    )

    # Left shifter

    s.lshifter = LeftLogicalShifter(Bits32)(
      in_   = s.in_a,
      shamt = 1,
      out   = s.out_a,
    )

    # Adder

    s.add = Adder(Bits32)(
      in0 = s.in_a,
      in1 = s.in_result,
    )

    # Result mux

    s.result_mux = Mux(Bits32,2)(
      sel = s.in_b[0],
      in_ = { 0: s.in_result,
              1: s.add.out },
      out = s.out_result,
    )

    # Connect the valid bits

    s.in_en //= s.out_en

  # Line tracing

  def line_trace( s ):
    return "{}|{}|{}(){}|{}|{}".format(
      s.in_a,  s.in_b,  s.in_result,
      s.out_a, s.out_b, s.out_result
    )

