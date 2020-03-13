#========================================================================
# TinyRV2 Instruction Type
#========================================================================
# Instruction types are similar to message types but are strictly used
# for communication within a TinyRV2-based processor. Instruction
# "messages" can be unpacked into the various fields as defined by the
# TinyRV2 ISA, as well as be constructed from specifying each field
# explicitly. The 32-bit instruction has different fields depending on
# the format of the instruction used. The following are the various
# instruction encoding formats used in the TinyRV2 ISA.
#
#  31          25 24   20 19   15 14    12 11          7 6      0
# | funct7       | rs2   | rs1   | funct3 | rd          | opcode |  R-type
# | imm[11:0]            | rs1   | funct3 | rd          | opcode |  I-type, I-imm
# | imm[11:5]    | rs2   | rs1   | funct3 | imm[4:0]    | opcode |  S-type, S-imm
# | imm[12|10:5] | rs2   | rs1   | funct3 | imm[4:1|11] | opcode |  SB-type,B-imm
# | imm[31:12]                            | rd          | opcode |  U-type, U-imm
# | imm[20|10:1|11|19:12]                 | rd          | opcode |  UJ-type,J-imm

from pymtl3 import *

#-------------------------------------------------------------------------
# TinyRV2 Instruction Fields
#-------------------------------------------------------------------------

OPCODE = slice(  0,  7 )
FUNCT3 = slice( 12, 15 )
FUNCT7 = slice( 25, 32 )

RD     = slice(  7, 12 )
RS1    = slice( 15, 20 )
RS2    = slice( 20, 25 )
SHAMT  = slice( 20, 25 )

I_IMM  = slice( 20, 32 )
CSRNUM = slice( 20, 32 )

S_IMM0 = slice(  7, 12 )
S_IMM1 = slice( 25, 32 )

B_IMM0 = slice(  8, 12 )
B_IMM1 = slice( 25, 31 )
B_IMM2 = slice(  7,  8 )
B_IMM3 = slice( 31, 32 )

U_IMM  = slice( 12, 32 )

J_IMM0 = slice( 21, 31 )
J_IMM1 = slice( 20, 21 )
J_IMM2 = slice( 12, 20 )
J_IMM3 = slice( 31, 32 )

# CUSTOM0 specific

XD     = slice( 14, 15 )
XS1    = slice( 13, 14 )
XS2    = slice( 12, 13 )

#-------------------------------------------------------------------------
# TinyRV2 Instruction Definitions
#-------------------------------------------------------------------------
NOP   = b8(0 ) # 00000000000000000000000000000000

# Load
LW    = b8(1 ) # ?????????????????010?????0000011

# Store
SW    = b8(2 ) # ?????????????????010?????0100011

# Shifts
SLL   = b8(3 ) # 0000000??????????001?????0110011
SLLI  = b8(4 ) # 0000000??????????001?????0010011
SRL   = b8(5 ) # 0000000??????????101?????0110011
SRLI  = b8(6 ) # 0000000??????????101?????0010011
SRA   = b8(7 ) # 0100000??????????101?????0110011
SRAI  = b8(8 ) # 0100000??????????101?????0010011

# Arithmetic
ADD   = b8(9 ) # 0000000??????????000?????0110011
ADDI  = b8(10) # ?????????????????000?????0010011
SUB   = b8(11) # 0100000??????????000?????0110011
LUI   = b8(12) # ?????????????????????????0110111
AUIPC = b8(13) # ?????????????????????????0010111

# Logical
XOR   = b8(14) # 0000000??????????100?????0110011
XORI  = b8(15) # ?????????????????100?????0010011
OR    = b8(16) # 0000000??????????110?????0110011
ORI   = b8(17) # ?????????????????110?????0010011
AND   = b8(18) # 0000000??????????111?????0110011
ANDI  = b8(19) # ?????????????????111?????0010011

# Compare
SLT   = b8(20) # 0000000??????????010?????0110011
SLTI  = b8(21) # ?????????????????010?????0010011
SLTU  = b8(22) # 0000000??????????011?????0110011
SLTIU = b8(23) # ?????????????????011?????0010011

# Branches
BEQ   = b8(24) # ?????????????????000?????1100011
BNE   = b8(25) # ?????????????????001?????1100011
BLT   = b8(26) # ?????????????????100?????1100011
BGE   = b8(27) # ?????????????????101?????1100011
BLTU  = b8(28) # ?????????????????110?????1100011
BGEU  = b8(29) # ?????????????????111?????1100011

# Jump & Link
JAL   = b8(30) # ?????????????????????????1101111
JALR  = b8(31) # ?????????????????000?????1100111

# Multiply
MUL   = b8(32) # 0000001??????????000?????0110011

# Privileged
CSRR  = b8(33) # ????????????00000010?????1110011
CSRW  = b8(34) # ?????????????????001000001110011

# ZERO inst
ZERO  = b8(35)

# CSRRX for accelerator
CSRRX = b8(36) # 0111111?????00000010?????1110011

#-------------------------------------------------------------------------
# TinyRV2 Instruction Disassembler
#-------------------------------------------------------------------------

inst_dict = {
  NOP   : "nop",
  LW    : "lw",
  SW    : "sw",
  SLL   : "sll",
  SLLI  : "slli",
  SRL   : "srl",
  SRLI  : "srli",
  SRA   : "sra",
  SRAI  : "srai",
  ADD   : "add",
  ADDI  : "addi",
  SUB   : "sub",
  LUI   : "lui",
  AUIPC : "auipc",
  XOR   : "xor",
  XORI  : "xori",
  OR    : "or",
  ORI   : "ori",
  AND   : "and",
  ANDI  : "andi",
  SLT   : "slt",
  SLTI  : "slti",
  SLTU  : "sltu",
  SLTIU : "sltiu",
  BEQ   : "beq",
  BNE   : "bne",
  BLT   : "blt",
  BGE   : "bge",
  BLTU  : "bltu",
  BGEU  : "bgeu",
  JAL   : "jal",
  JALR  : "jalr",
  MUL   : "mul",
  CSRR  : "csrr",
  CSRW  : "csrw",
  CSRRX : "csrrx",
  ZERO  : "????"
}

#-------------------------------------------------------------------------
# CSR registers
#-------------------------------------------------------------------------

# R/W
CSR_PROC2MNGR = b12(0x7C0)
CSR_STATS_EN  = b12(0x7C1)

# R/O
CSR_MNGR2PROC = b12(0xFC0)
CSR_NUMCORES  = b12(0xFC1)
CSR_COREID    = b12(0xF14)

#-----------------------------------------------------------------------
# DecodeInstType
#-----------------------------------------------------------------------
# TinyRV2 Instruction Type Decoder

class DecodeInstType( Component ):

  # Interface

  def construct( s ):

    s.in_ = InPort ( Bits32 )
    s.out = OutPort( Bits8 )

    @s.update
    def comb_logic():

      s.out = ZERO

      if   s.in_ == b32(0b10011):               s.out = NOP
      elif s.in_[OPCODE] == b7(0b0110011):
        if   s.in_[FUNCT7] == b7(0b0000000):
          if   s.in_[FUNCT3] == b3(0b000):     s.out = ADD
          elif s.in_[FUNCT3] == b3(0b001):     s.out = SLL
          elif s.in_[FUNCT3] == b3(0b010):     s.out = SLT
          elif s.in_[FUNCT3] == b3(0b011):     s.out = SLTU
          elif s.in_[FUNCT3] == b3(0b100):     s.out = XOR
          elif s.in_[FUNCT3] == b3(0b101):     s.out = SRL
          elif s.in_[FUNCT3] == b3(0b110):     s.out = OR
          elif s.in_[FUNCT3] == b3(0b111):     s.out = AND
        elif s.in_[FUNCT7] == b7(0b0100000):
          if   s.in_[FUNCT3] == b3(0b000):     s.out = SUB
          elif s.in_[FUNCT3] == b3(0b101):     s.out = SRA
        elif s.in_[FUNCT7] == b7(0b0000001):
          if   s.in_[FUNCT3] == b3(0b000):     s.out = MUL

      elif s.in_[OPCODE] == b7(0b0010011):
        if   s.in_[FUNCT3] == b3(0b000):       s.out = ADDI
        elif s.in_[FUNCT3] == b3(0b010):       s.out = SLTI
        elif s.in_[FUNCT3] == b3(0b011):       s.out = SLTIU
        elif s.in_[FUNCT3] == b3(0b100):       s.out = XORI
        elif s.in_[FUNCT3] == b3(0b110):       s.out = ORI
        elif s.in_[FUNCT3] == b3(0b111):       s.out = ANDI
        elif s.in_[FUNCT3] == b3(0b001):       s.out = SLLI
        elif s.in_[FUNCT3] == b3(0b101):
          if   s.in_[FUNCT7] == b7(0b0000000): s.out = SRLI
          elif s.in_[FUNCT7] == b7(0b0100000): s.out = SRAI

      elif s.in_[OPCODE] == b7(0b0100011):
        if   s.in_[FUNCT3] == b3(0b010):       s.out = SW

      elif s.in_[OPCODE] == b7(0b0000011):
        if   s.in_[FUNCT3] == b3(0b010):       s.out = LW

      elif s.in_[OPCODE] == b7(0b1100011):
        if   s.in_[FUNCT3] == b3(0b000):       s.out = BEQ
        elif s.in_[FUNCT3] == b3(0b001):       s.out = BNE
        elif s.in_[FUNCT3] == b3(0b100):       s.out = BLT
        elif s.in_[FUNCT3] == b3(0b101):       s.out = BGE
        elif s.in_[FUNCT3] == b3(0b110):       s.out = BLTU
        elif s.in_[FUNCT3] == b3(0b111):       s.out = BGEU

      elif s.in_[OPCODE] == b7(0b0110111):     s.out = LUI

      elif s.in_[OPCODE] == b7(0b0010111):     s.out = AUIPC

      elif s.in_[OPCODE] == b7(0b1101111):     s.out = JAL

      elif s.in_[OPCODE] == b7(0b1100111):     s.out = JALR

      elif s.in_[OPCODE] == b7(0b1110011):
        if   s.in_[FUNCT3] == b3(0b001):       s.out = CSRW
        elif s.in_[FUNCT3] == b3(0b010):
          if s.in_[FUNCT7] == b7(0b0111111):   s.out = CSRRX
          else:                            s.out = CSRR
