#========================================================================
# lab3-mem Decoder for Write Byte Enable
#========================================================================

from pymtl3 import *

#------------------------------------------------------------------------
# Decoder for Wben
#------------------------------------------------------------------------

class DecodeWbenPRTL( Component ):

  # interface

  def construct( s, in_nbits=2, out_nbits=(1 << (2+2)) ):
    InType  = mk_bits(in_nbits)
    OutType = mk_bits(out_nbits)

    s.in_ = InPort  ( InType  )
    s.out = OutPort ( OutType )

  # Combinational logic

    @s.update
    def comb_logic():
      s.out = OutType(0)

      for i in range(out_nbits):
        if s.in_ == InType(i >> 2):
          s.out[i] = b1(1)
