#=========================================================================
# lbu
#=========================================================================

import random

# Fix the random seed so results are reproducible
random.seed(0xdeadbeef)

from pymtl3 import *
from .inst_utils import *

#-------------------------------------------------------------------------
# gen_basic_test
#-------------------------------------------------------------------------

def gen_basic_test():
  return """
    csrr x1, mngr2proc < 0x00002000
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lbu   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000004

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_ld_dest_dep_test( 5, "lbu", 0x2000, 0x00000003 ),
    gen_ld_dest_dep_test( 4, "lbu", 0x2004, 0x00000007 ),
    gen_ld_dest_dep_test( 3, "lbu", 0x2008, 0x0000000b ),
    gen_ld_dest_dep_test( 2, "lbu", 0x200c, 0x0000000f ),
    gen_ld_dest_dep_test( 1, "lbu", 0x2010, 0x00000013 ),
    gen_ld_dest_dep_test( 0, "lbu", 0x2014, 0x00000017 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_base_dep_test
#-------------------------------------------------------------------------

def gen_base_dep_test():
  return [

    gen_ld_base_dep_test( 5, "lbu", 0x2000, 0x00000003 ),
    gen_ld_base_dep_test( 4, "lbu", 0x2004, 0x00000007 ),
    gen_ld_base_dep_test( 3, "lbu", 0x2008, 0x0000000b ),
    gen_ld_base_dep_test( 2, "lbu", 0x200c, 0x0000000f ),
    gen_ld_base_dep_test( 1, "lbu", 0x2010, 0x00000013 ),
    gen_ld_base_dep_test( 0, "lbu", 0x2014, 0x00000017 ),

    gen_word_data([
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x10111213,
      0x14151617,
    ])

  ]

#-------------------------------------------------------------------------
# gen_srcs_dest_test
#-------------------------------------------------------------------------

def gen_srcs_dest_test():
  return [
    gen_ld_base_eq_dest_test( "lbu", 0x2000, 0x00000004 ),
    gen_word_data([ 0x01020304 ])
  ]

#-------------------------------------------------------------------------
# gen_endian_test
#-------------------------------------------------------------------------

def gen_endian_test():
  return [

    gen_ld_value_test( "lbu", 0, 0x2000, 0x00000004 ),
    gen_ld_value_test( "lbu", 0, 0x2001, 0x00000003 ),
    gen_ld_value_test( "lbu", 0, 0x2002, 0x00000002 ),
    gen_ld_value_test( "lbu", 0, 0x2003, 0x00000001 ),

    gen_word_data([
      0x01020304,
    ])

  ]

#-------------------------------------------------------------------------
# gen_zext_test
#-------------------------------------------------------------------------

def gen_zext_test():
  return [

    gen_ld_value_test( "lbu", 0, 0x2000, 0x00000084 ),
    gen_ld_value_test( "lbu", 0, 0x2001, 0x00000083 ),
    gen_ld_value_test( "lbu", 0, 0x2002, 0x00000082 ),
    gen_ld_value_test( "lbu", 0, 0x2003, 0x00000081 ),

    gen_word_data([
      0x81828384,
    ])

  ]

#-------------------------------------------------------------------------
# gen_addr_test
#-------------------------------------------------------------------------

def gen_addr_test():
  return [

    # Test positive offsets

    gen_ld_value_test( "lbu",   0, 0x00002000, 0x0000007d ),
    gen_ld_value_test( "lbu",   1, 0x00002000, 0x0000007c ),
    gen_ld_value_test( "lbu",   2, 0x00002000, 0x0000007b ),
    gen_ld_value_test( "lbu",   3, 0x00002000, 0x0000007a ),
    gen_ld_value_test( "lbu",   4, 0x00002000, 0x00000003 ),
    gen_ld_value_test( "lbu",   5, 0x00002000, 0x00000002 ),

    # Test negative offsets

    gen_ld_value_test( "lbu",  -5, 0x00002014, 0x00000008 ),
    gen_ld_value_test( "lbu",  -4, 0x00002014, 0x0000000f ),
    gen_ld_value_test( "lbu",  -3, 0x00002014, 0x0000000e ),
    gen_ld_value_test( "lbu",  -2, 0x00002014, 0x0000000d ),
    gen_ld_value_test( "lbu",  -1, 0x00002014, 0x0000000c ),
    gen_ld_value_test( "lbu",   0, 0x00002014, 0x0000006d ),

    # Test positive offset with unaligned base

    gen_ld_value_test( "lbu",   1, 0x00001fff, 0x0000007d ),
    gen_ld_value_test( "lbu",   2, 0x00001fff, 0x0000007c ),
    gen_ld_value_test( "lbu",   3, 0x00001fff, 0x0000007b ),
    gen_ld_value_test( "lbu",   4, 0x00001fff, 0x0000007a ),
    gen_ld_value_test( "lbu",   5, 0x00001fff, 0x00000003 ),
    gen_ld_value_test( "lbu",   6, 0x00001fff, 0x00000002 ),

    # Test negative offset with unaligned base

    gen_ld_value_test( "lbu",  -6, 0x00002015, 0x00000008 ),
    gen_ld_value_test( "lbu",  -5, 0x00002015, 0x0000000f ),
    gen_ld_value_test( "lbu",  -4, 0x00002015, 0x0000000e ),
    gen_ld_value_test( "lbu",  -3, 0x00002015, 0x0000000d ),
    gen_ld_value_test( "lbu",  -2, 0x00002015, 0x0000000c ),
    gen_ld_value_test( "lbu",  -1, 0x00002015, 0x0000006d ),

    gen_word_data([
      0x7a7b7c7d,
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0x6a6b6c6d,
    ])

  ]

#-------------------------------------------------------------------------
# gen_random_test
#-------------------------------------------------------------------------

def gen_random_test():

  # Generate some random data

  data = []
  for i in range(128):
    data.append( random.randint(0,0xff) )

  # Generate random accesses to this data

  asm_code = []
  for i in range(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = b32( 0x2000 + b )
    offset = b16( (a - b) )
    result = data[a]

    asm_code.append( gen_ld_value_test( "lbu", offset.int(), base.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_byte_data( data ) )
  return asm_code

