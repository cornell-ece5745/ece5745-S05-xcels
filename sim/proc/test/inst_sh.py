#=========================================================================
# sh
#=========================================================================

import random

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
    sh   x2, 0(x1)
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    lw   x3, 0(x1)
    csrw proc2mngr, x3 > 0x0102beef

    .data
    .word 0x01020304
  """

#-------------------------------------------------------------------------
# gen_dest_dep_test
#-------------------------------------------------------------------------

def gen_dest_dep_test():
  return [

    gen_st_dest_dep_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_dest_dep_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_dest_dep_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_dest_dep_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_dest_dep_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_dest_dep_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

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

    gen_st_base_dep_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_base_dep_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_base_dep_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_base_dep_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_base_dep_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_base_dep_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

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

    gen_st_src_dep_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_src_dep_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_src_dep_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_src_dep_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_src_dep_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_src_dep_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

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

    gen_st_srcs_dep_test( 5, "sh", 0x30313233, 0x2000, 0x00013233 ),
    gen_st_srcs_dep_test( 4, "sh", 0x34353637, 0x2004, 0x04053637 ),
    gen_st_srcs_dep_test( 3, "sh", 0x38393a3b, 0x2008, 0x08093a3b ),
    gen_st_srcs_dep_test( 2, "sh", 0x3c3d3e3f, 0x200c, 0x0c0d3e3f ),
    gen_st_srcs_dep_test( 1, "sh", 0x40414243, 0x2010, 0x10114243 ),
    gen_st_srcs_dep_test( 0, "sh", 0x44454647, 0x2014, 0x14154647 ),

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
    gen_st_src_eq_base_test( "sh", 0x000020004, 0x00000004 ),
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

    gen_st_value_test( "sh", 0x30313233,   0, 0x00002000, 0xdead3233 ),
    gen_st_value_test( "sh", 0x34353637,   2, 0x00002000, 0x36373233 ),
    gen_st_value_test( "sh", 0x38393a3b,   4, 0x00002000, 0x00013a3b ),
    gen_st_value_test( "sh", 0x3c3d3e3f,   6, 0x00002000, 0x3e3f3a3b ),
    gen_st_value_test( "sh", 0x40414243,   8, 0x00002000, 0x04054243 ),
    gen_st_value_test( "sh", 0x44454647,  10, 0x00002000, 0x46474243 ),

    # Test negative offsets

    gen_st_value_test( "sh", 0x5c5d5e5f,   0, 0x00002014, 0xcafe5e5f ),
    gen_st_value_test( "sh", 0x58595a5b,  -2, 0x00002014, 0x5a5b0e0f ),
    gen_st_value_test( "sh", 0x54555657,  -4, 0x00002014, 0x5a5b5657 ),
    gen_st_value_test( "sh", 0x50515253,  -6, 0x00002014, 0x52530a0b ),
    gen_st_value_test( "sh", 0x4c4d4e4f,  -8, 0x00002014, 0x52534e4f ),

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

    gen_st_value_test( "sh", 0x30313233,   1, 0x00001fff, 0xdead3233 ),
    gen_st_value_test( "sh", 0x34353637,   3, 0x00001fff, 0x36373233 ),
    gen_st_value_test( "sh", 0x38393a3b,   5, 0x00001fff, 0x00013a3b ),
    gen_st_value_test( "sh", 0x3c3d3e3f,   7, 0x00001fff, 0x3e3f3a3b ),
    gen_st_value_test( "sh", 0x40414243,   9, 0x00001fff, 0x04054243 ),
    gen_st_value_test( "sh", 0x44454647,  11, 0x00001fff, 0x46474243 ),

    # Test negative offset with unaligned base

    gen_st_value_test( "sh", 0x5c5d5e5f,  -1, 0x00002015, 0xcafe5e5f ),
    gen_st_value_test( "sh", 0x58595a5b,  -3, 0x00002015, 0x5a5b0e0f ),
    gen_st_value_test( "sh", 0x54555657,  -5, 0x00002015, 0x5a5b5657 ),
    gen_st_value_test( "sh", 0x50515253,  -7, 0x00002015, 0x52530a0b ),
    gen_st_value_test( "sh", 0x4c4d4e4f,  -9, 0x00002015, 0x52534e4f ),

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

    base   = b32( 0x2000 + (2*b) )
    offset = b16( (2*(a - b)) )
    result = data[a]

    asm_code.append( gen_st_random_test( "sh", "lhu", result, offset.int(), base.uint() ) )

  # Generate some random data to initialize memory

  initial_data = []
  for i in range(128):
    initial_data.append( random.randint(0,0xff) )

  # Add the data to the end of the assembly code

  asm_code.append( gen_hword_data( initial_data ) )
  return asm_code
