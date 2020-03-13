#=========================================================================
# IntMulFixedLatRTL_test
#=========================================================================

import pytest
import random

random.seed(0xdeadbeef)

from pymtl3                      import *
from pymtl3.passes               import TracingConfigs
from pymtl3.stdlib.test          import TestMasterCL, mk_test_case_table
from pymtl3.stdlib.test          import run_sim, config_model
from lab1_imul.IntMulFixedLatRTL import IntMulFixedLatRTL
from lab1_imul.IntMulMsgs        import IntMulMsgs

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, imul ):

    # Instantiate models

    s.tm   = TestMasterCL( IntMulMsgs.req, IntMulMsgs.resp )
    s.imul = imul

    # Connect

    s.tm.master //= s.imul.minion

  def done( s ):
    return s.tm.done()

  def line_trace( s ):
    return s.tm.line_trace()  + " > " + \
           s.imul.line_trace()

#-------------------------------------------------------------------------
# mk_req_msg
#-------------------------------------------------------------------------

def req( a, b ):
  return IntMulMsgs.req( a, b )

def resp( a ):
  return IntMulMsgs.resp( a )

#----------------------------------------------------------------------
# Test Case: small positive * positive
#----------------------------------------------------------------------

small_pos_pos_msgs = [
  req(  2,  3 ), resp(   6 ),
  req(  4,  5 ), resp(  20 ),
  req(  3,  4 ), resp(  12 ),
  req( 10, 13 ), resp( 130 ),
  req(  8,  7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * positive
#----------------------------------------------------------------------

small_neg_pos_msgs = [
  req(  -2,  3 ), resp(   -6 ),
  req(  -4,  5 ), resp(  -20 ),
  req(  -3,  4 ), resp(  -12 ),
  req( -10, 13 ), resp( -130 ),
  req(  -8,  7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: small positive * negative
#----------------------------------------------------------------------

small_pos_neg_msgs = [
  req(  2,  -3 ), resp(   -6 ),
  req(  4,  -5 ), resp(  -20 ),
  req(  3,  -4 ), resp(  -12 ),
  req( 10, -13 ), resp( -130 ),
  req(  8,  -7 ), resp(  -56 ),
]

#----------------------------------------------------------------------
# Test Case: small negative * negative
#----------------------------------------------------------------------

small_neg_neg_msgs = [
  req(  -2,  -3 ), resp(   6 ),
  req(  -4,  -5 ), resp(  20 ),
  req(  -3,  -4 ), resp(  12 ),
  req( -10, -13 ), resp( 130 ),
  req(  -8,  -7 ), resp(  56 ),
]

#----------------------------------------------------------------------
# Test Case: large positive * positive
#----------------------------------------------------------------------

large_pos_pos_msgs = [
  req( 0x0bcd0000, 0x0000abcd ), resp( 0x62290000 ),
  req( 0x0fff0000, 0x0000ffff ), resp( 0xf0010000 ),
  req( 0x0fff0000, 0x0fff0000 ), resp( 0x00000000 ),
  req( 0x04e5f14d, 0x7839d4fc ), resp( 0x10524bcc ),
]

#----------------------------------------------------------------------
# Test Case: large negative * negative
#----------------------------------------------------------------------

large_neg_neg_msgs = [
  req( 0x80000001, 0x80000001 ), resp( 0x00000001 ),
  req( 0x8000abcd, 0x8000ef00 ), resp( 0x20646300 ),
  req( 0x80340580, 0x8aadefc0 ), resp( 0x6fa6a000 ),
]

#----------------------------------------------------------------------
# Test Case: zeros
#----------------------------------------------------------------------

zeros_msgs = [
  req(  0,  0 ), resp(   0 ),
  req(  0,  1 ), resp(   0 ),
  req(  1,  0 ), resp(   0 ),
  req(  0, -1 ), resp(   0 ),
  req( -1,  0 ), resp(   0 ),
]
#----------------------------------------------------------------------
# Test Case: random small
#----------------------------------------------------------------------

random_small_msgs = []
for i in range(50):
  a = random.randint(0,100)
  b = random.randint(0,100)
  random_small_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: random large
#----------------------------------------------------------------------

random_large_msgs = []
for i in range(50):
  a = random.randint(0,0xffffffff)
  b = random.randint(0,0xffffffff)
  random_large_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: lomask
#----------------------------------------------------------------------

random_lomask_msgs = []
for i in range(50):

  shift_amount = random.randint(0,16)
  a = random.randint(0,0xffffffff) << shift_amount

  shift_amount = random.randint(0,16)
  b = random.randint(0,0xffffffff) << shift_amount

  random_lomask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: himask
#----------------------------------------------------------------------

random_himask_msgs = []
for i in range(50):

  shift_amount = random.randint(0,16)
  a = random.randint(0,0xffffffff) >> shift_amount

  shift_amount = random.randint(0,16)
  b = random.randint(0,0xffffffff) >> shift_amount

  random_himask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: lohimask
#----------------------------------------------------------------------

random_lohimask_msgs = []
for i in range(50):

  rshift_amount = random.randint(0,12)
  lshift_amount = random.randint(0,12)
  a = (random.randint(0,0xffffff) >> rshift_amount) << lshift_amount

  rshift_amount = random.randint(0,12)
  lshift_amount = random.randint(0,12)
  b = (random.randint(0,0xffffff) >> rshift_amount) << lshift_amount

  random_lohimask_msgs.extend([ req( a, b ), resp( a * b ) ])

#----------------------------------------------------------------------
# Test Case: sparse
#----------------------------------------------------------------------

random_sparse_msgs = []
for i in range(50):

  a = random.randint(0,0xffffffff)

  for i in range(32):
    is_masked = random.randint(0,1)
    if is_masked:
      a = a & ( (~(1 << i)) & 0xffffffff )

  b = random.randint(0,0xffffffff)

  for i in range(32):
    is_masked = random.randint(0,1)
    if is_masked:
      b = b & ( (~(1 << i)) & 0xffffffff )

  random_sparse_msgs.extend([ req( a, b ), resp( a * b ) ])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (                      "msgs                 src_delay sink_delay"),
  [ "small_pos_pos",     small_pos_pos_msgs,   0,        0          ],
  [ "small_neg_pos",     small_neg_pos_msgs,   0,        0          ],
  [ "small_pos_neg",     small_pos_neg_msgs,   0,        0          ],
  [ "small_neg_neg",     small_neg_neg_msgs,   0,        0          ],
  [ "large_pos_pos",     large_pos_pos_msgs,   0,        0          ],
  [ "large_neg_neg",     large_neg_neg_msgs,   0,        0          ],
  [ "zeros",             zeros_msgs,           0,        0          ],
  [ "random_small",      random_small_msgs,    0,        0          ],
  [ "random_large",      random_large_msgs,    0,        0          ],
  [ "random_lomask",     random_lomask_msgs,   0,        0          ],
  [ "random_himask",     random_himask_msgs,   0,        0          ],
  [ "random_lohimask",   random_lohimask_msgs, 0,        0          ],
  [ "random_sparse",     random_sparse_msgs,   0,        0          ],
  [ "random_small_3x14", random_small_msgs,    3,        14         ],
  [ "random_large_3x14", random_large_msgs,    3,        14         ],
])

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulFixedLatRTL() )

  th.set_param("top.tm.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.tm.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  config_model( th, dump_vcd, test_verilog, ['imul'] )

  run_sim( th )
