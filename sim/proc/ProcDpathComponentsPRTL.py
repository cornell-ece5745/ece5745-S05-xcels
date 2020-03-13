#=========================================================================
# ProcDpathComponentsPRTL.py
#=========================================================================

from pymtl3            import *
from .TinyRV2InstPRTL  import *

#-------------------------------------------------------------------------
# Generate intermediate (imm) based on type
#-------------------------------------------------------------------------

class ImmGenPRTL( Component ):

  # Interface

  def construct( s ):
    dtype = mk_bits( 32 )

    s.imm_type = InPort( Bits3 )
    s.inst     = InPort( dtype )
    s.imm      = OutPort( dtype )

    @s.update
    def comb_logic():
      s.imm = dtype(0)

      # Always sext!

      if   s.imm_type == b3(0): # I-type
        s.imm = concat( sext( s.inst[ I_IMM ], 32 ) )

      elif s.imm_type == b3(1): # S-type
        s.imm = concat( sext( s.inst[ S_IMM1 ], 27 ),
                              s.inst[ S_IMM0 ] )
      elif s.imm_type == b3(2): # B-type
        s.imm = concat( sext( s.inst[ B_IMM3 ], 20 ),
                              s.inst[ B_IMM2 ],
                              s.inst[ B_IMM1 ],
                              s.inst[ B_IMM0 ],
                              b1(0) )


      elif s.imm_type == b3(3): # U-type
        s.imm = concat(       s.inst[ U_IMM ],
                              b12(0) )

      elif s.imm_type == b3(4): # J-type
        s.imm = concat( sext( s.inst[ J_IMM3 ], 12 ),
                              s.inst[ J_IMM2 ],
                              s.inst[ J_IMM1 ],
                              s.inst[ J_IMM0 ],
                              b1(0) )
  def line_trace( s ):
    return f"immT{s.imm_type}={s.imm}"


#-------------------------------------------------------------------------
# ALU
#-------------------------------------------------------------------------

class AluPRTL( Component ):

  # Interface

  def construct( s ):

    s.in0     = InPort ( Bits32 )
    s.in1     = InPort ( Bits32 )
    s.fn      = InPort ( Bits4 )

    s.out     = OutPort( Bits32 )
    s.ops_eq  = OutPort()
    s.ops_lt  = OutPort()
    s.ops_ltu = OutPort()

    # Combinational Logic

    s.tmp_a = Wire( Bits33 )
    s.tmp_b = Wire( Bits64 )

    @s.update
    def comb_logic():
      s.out = b32(0)
      s.tmp_a = b33(0)
      s.tmp_b = b64(0)

      if   s.fn == b4(0): s.out = s.in0 + s.in1         # ADD
      elif s.fn == b4(1): s.out = s.in0 - s.in1         # SUB
      elif s.fn == b4(2): s.out = s.in0 << s.in1[0:5]   # SLL
      elif s.fn == b4(3): s.out = s.in0 | s.in1         # OR

      elif s.fn == b4(4):                               # SLT
        s.tmp_a = sext( s.in0, 33 ) - sext( s.in1, 33 )
        s.out   = zext( s.tmp_a[32], 32 )

      elif s.fn == b4(5): s.out = zext(s.in0 < s.in1, 32)    # SLTU
      elif s.fn == b4(6): s.out = s.in0 & s.in1    # AND
      elif s.fn == b4(7): s.out = s.in0 ^ s.in1    # XOR
      elif s.fn == b4(8): s.out = ~( s.in0 | s.in1 )    # NOR
      elif s.fn == b4(9): s.out = s.in0 >> (s.in1[0:5]) # SRL

      elif s.fn == b4(10):                             # SRA
        s.tmp_b = sext( s.in0, 64 ) >> s.in1[0:5]
        s.out   = s.tmp_b[0:32]

      elif s.fn == b4(11): s.out = s.in0               # CP OP0
      elif s.fn == b4(12): s.out = s.in1               # CP OP1

      elif s.fn == b4(13):                             # ADDZ for clearing LSB
        s.out = (s.in0 + s.in1) & b32(0xfffffffe)

      s.ops_eq  = ( s.in0 == s.in1 )
      s.ops_lt  = s.tmp_a[32]
      s.ops_ltu = ( s.in0 < s.in1 )

  def line_trace( s ):
    return f"aluT{int(s.fn)}({s.in0},{s.in1})={s.out}," \
           f"{'eq' if s.ops_eq else 'ne'}," \
           f"{'lt' if s.ops_lt else 'ge'}," \
           f"{'ltu' if s.ops_ltu else 'geu'}"
