#=========================================================================
# lh
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
    lh   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    csrw proc2mngr, x2 > 0x00000304

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_ld_dest_dep_test( 5, "lh", 0x2000, 0x00000203 ),
    gen_ld_dest_dep_test( 4, "lh", 0x2004, 0x00000607 ),
    gen_ld_dest_dep_test( 3, "lh", 0x2008, 0x00000a0b ),
    gen_ld_dest_dep_test( 2, "lh", 0x200c, 0x00000e0f ),
    gen_ld_dest_dep_test( 1, "lh", 0x2010, 0x00001213 ),
    gen_ld_dest_dep_test( 0, "lh", 0x2014, 0x00001617 ),

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

    gen_ld_base_dep_test( 5, "lh", 0x2000, 0x00000203 ),
    gen_ld_base_dep_test( 4, "lh", 0x2004, 0x00000607 ),
    gen_ld_base_dep_test( 3, "lh", 0x2008, 0x00000a0b ),
    gen_ld_base_dep_test( 2, "lh", 0x200c, 0x00000e0f ),
    gen_ld_base_dep_test( 1, "lh", 0x2010, 0x00001213 ),
    gen_ld_base_dep_test( 0, "lh", 0x2014, 0x00001617 ),

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
    gen_ld_base_eq_dest_test( "lh", 0x2000, 0x00000304 ),
    gen_word_data([ 0x01020304 ])
  ]

#-------------------------------------------------------------------------
# gen_endian_test
#-------------------------------------------------------------------------

def gen_endian_test():
  return [

    gen_ld_value_test( "lh", 0, 0x2000, 0x00000304 ),
    gen_ld_value_test( "lh", 0, 0x2002, 0x00000102 ),

    gen_word_data([
      0x01020304,
    ])

  ]

#-------------------------------------------------------------------------
# gen_sext_test
#-------------------------------------------------------------------------

def gen_sext_test():
  return [

    gen_ld_value_test( "lh", 0, 0x2000, 0xffff8384 ),
    gen_ld_value_test( "lh", 0, 0x2002, 0xffff8182 ),

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

    gen_ld_value_test( "lh",   0, 0x00002000, 0x00007c7d ),
    gen_ld_value_test( "lh",   2, 0x00002000, 0x00007a7b ),
    gen_ld_value_test( "lh",   4, 0x00002000, 0x00000203 ),
    gen_ld_value_test( "lh",   6, 0x00002000, 0x00000001 ),
    gen_ld_value_test( "lh",   8, 0x00002000, 0x00000607 ),
    gen_ld_value_test( "lh",  10, 0x00002000, 0x00000405 ),

    # Test negative offsets

    gen_ld_value_test( "lh", -10, 0x00002014, 0x00000405 ),
    gen_ld_value_test( "lh",  -8, 0x00002014, 0x00000a0b ),
    gen_ld_value_test( "lh",  -6, 0x00002014, 0x00000809 ),
    gen_ld_value_test( "lh",  -4, 0x00002014, 0x00000e0f ),
    gen_ld_value_test( "lh",  -2, 0x00002014, 0x00000c0d ),
    gen_ld_value_test( "lh",   0, 0x00002014, 0x00006c6d ),

    # Test positive offset with unaligned base

    gen_ld_value_test( "lh",   1, 0x00001fff, 0x00007c7d ),
    gen_ld_value_test( "lh",   3, 0x00001fff, 0x00007a7b ),
    gen_ld_value_test( "lh",   5, 0x00001fff, 0x00000203 ),
    gen_ld_value_test( "lh",   7, 0x00001fff, 0x00000001 ),
    gen_ld_value_test( "lh",   9, 0x00001fff, 0x00000607 ),
    gen_ld_value_test( "lh",  11, 0x00001fff, 0x00000405 ),

    # Test negative offset with unaligned base

    gen_ld_value_test( "lh", -11, 0x00002015, 0x00000405 ),
    gen_ld_value_test( "lh",  -9, 0x00002015, 0x00000a0b ),
    gen_ld_value_test( "lh",  -7, 0x00002015, 0x00000809 ),
    gen_ld_value_test( "lh",  -5, 0x00002015, 0x00000e0f ),
    gen_ld_value_test( "lh",  -3, 0x00002015, 0x00000c0d ),
    gen_ld_value_test( "lh",  -1, 0x00002015, 0x00006c6d ),

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
    data.append( random.randint(0,0xffff) )

  # Generate random accesses to this data

  asm_code = []
  for i in range(100):

    a = random.randint(0,127)
    b = random.randint(0,127)

    base   = b32( 0x2000 + (2*b) )
    offset = b16( 2*(a - b) )

    # We need to carefully construct the result. We take the Python
    # reference int, convert it into a bits, sign extend it to 32 bits,
    # and then convert it back into a Python int

    result = sext( b16( data[a] ), 32 ).uint()

    asm_code.append( gen_ld_value_test( "lh", offset.int(), base.uint(), result ) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_hword_data( data ) )
  return asm_code

