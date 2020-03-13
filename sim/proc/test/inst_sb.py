#=========================================================================
# sb
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
    csrr x2, mngr2proc < 0xdeadbeef
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    sb   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0x010203ef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_st_dest_dep_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_dest_dep_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_dest_dep_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_dest_dep_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_dest_dep_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_dest_dep_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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

    gen_st_base_dep_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_base_dep_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_base_dep_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_base_dep_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_base_dep_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_base_dep_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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
# gen_src_dep_test
#-------------------------------------------------------------------------

def gen_src_dep_test():
  return [

    gen_st_src_dep_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_src_dep_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_src_dep_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_src_dep_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_src_dep_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_src_dep_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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
# gen_srcs_dep_test
#-------------------------------------------------------------------------

def gen_srcs_dep_test():
  return [

    gen_st_srcs_dep_test( 5, "sb", 0x30313233, 0x2000, 0x00010233 ),
    gen_st_srcs_dep_test( 4, "sb", 0x34353637, 0x2004, 0x04050637 ),
    gen_st_srcs_dep_test( 3, "sb", 0x38393a3b, 0x2008, 0x08090a3b ),
    gen_st_srcs_dep_test( 2, "sb", 0x3c3d3e3f, 0x200c, 0x0c0d0e3f ),
    gen_st_srcs_dep_test( 1, "sb", 0x40414243, 0x2010, 0x10111243 ),
    gen_st_srcs_dep_test( 0, "sb", 0x44454647, 0x2014, 0x14151647 ),

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
    gen_st_src_eq_base_test( "sb", 0x000020004, 0x00000004 ),
    gen_word_data([
      0x01020304,
      0x05060708,
    ])
  ]

#-------------------------------------------------------------------------
# gen_addr1_test
#-------------------------------------------------------------------------
# We create two separate addr tests since each test actually changes the
# data stored in memory and we want to keep these two tests isolated.

def gen_addr1_test():
  return [

    # Test positive offsets

    gen_st_value_test( "sb", 0x30313233,   0, 0x00002000, 0xdeadbe33 ),
    gen_st_value_test( "sb", 0x34353637,   1, 0x00002000, 0xdead3733 ),
    gen_st_value_test( "sb", 0x38393a3b,   2, 0x00002000, 0xde3b3733 ),
    gen_st_value_test( "sb", 0x3c3d3e3f,   3, 0x00002000, 0x3f3b3733 ),
    gen_st_value_test( "sb", 0x40414243,   4, 0x00002000, 0x00010243 ),
    gen_st_value_test( "sb", 0x44454647,   5, 0x00002000, 0x00014743 ),

    # Test negative offsets

    gen_st_value_test( "sb", 0x5c5d5e5f,   0, 0x00002014, 0xcafeca5f ),
    gen_st_value_test( "sb", 0x58595a5b,  -1, 0x00002014, 0x5b0d0e0f ),
    gen_st_value_test( "sb", 0x54555657,  -2, 0x00002014, 0x5b570e0f ),
    gen_st_value_test( "sb", 0x50515253,  -3, 0x00002014, 0x5b57530f ),
    gen_st_value_test( "sb", 0x4c4d4e4f,  -4, 0x00002014, 0x5b57534f ),
    gen_st_value_test( "sb", 0x48494a4b,  -5, 0x00002014, 0x4b090a0b ),

    gen_word_data([
      0xdeadbeef,
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0xcafecafe,
    ])

  ]

#-------------------------------------------------------------------------
# gen_addr2_test
#-------------------------------------------------------------------------

def gen_addr2_test():
  return [

    # Test positive offset with unaligned base

    gen_st_value_test( "sb", 0x30313233,   1, 0x00001fff, 0xdeadbe33 ),
    gen_st_value_test( "sb", 0x34353637,   2, 0x00001fff, 0xdead3733 ),
    gen_st_value_test( "sb", 0x38393a3b,   3, 0x00001fff, 0xde3b3733 ),
    gen_st_value_test( "sb", 0x3c3d3e3f,   4, 0x00001fff, 0x3f3b3733 ),
    gen_st_value_test( "sb", 0x40414243,   5, 0x00001fff, 0x00010243 ),
    gen_st_value_test( "sb", 0x44454647,   6, 0x00001fff, 0x00014743 ),

    # Test negative offset with unaligned base

    gen_st_value_test( "sb", 0x5c5d5e5f,  -1, 0x00002015, 0xcafeca5f ),
    gen_st_value_test( "sb", 0x58595a5b,  -2, 0x00002015, 0x5b0d0e0f ),
    gen_st_value_test( "sb", 0x54555657,  -3, 0x00002015, 0x5b570e0f ),
    gen_st_value_test( "sb", 0x50515253,  -4, 0x00002015, 0x5b57530f ),
    gen_st_value_test( "sb", 0x4c4d4e4f,  -5, 0x00002015, 0x5b57534f ),
    gen_st_value_test( "sb", 0x48494a4b,  -6, 0x00002015, 0x4b090a0b ),

    gen_word_data([
      0xdeadbeef,
      0x00010203,
      0x04050607,
      0x08090a0b,
      0x0c0d0e0f,
      0xcafecafe,
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

    asm_code.append( gen_st_random_test( "sb", "lbu", result, offset.int(), base.uint() ) )

  # Generate some random data to initialize memory

  initial_data = []
  for i in range(128):
    initial_data.append( random.randint(0,0xff) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_byte_data( initial_data ) )
  return asm_code

