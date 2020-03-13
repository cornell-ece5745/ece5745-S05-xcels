#=========================================================================
# NullXcelRTL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib.test import mk_test_case_table, run_sim, config_model
from pymtl3.stdlib.test import TestMasterCL

from proc.XcelMsg     import *
from proc.NullXcelRTL import NullXcelRTL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness(Component):

  def construct( s ):

    # Instantiate models

    s.tm   = TestMasterCL( XcelMsgs.req, XcelMsgs.resp )
    s.xcel = NullXcelRTL ()
    s.xcel.mem.req.rdy //= b1(0)
    s.xcel.mem.resp.en //= b1(0)

    s.tm.master //= s.xcel.xcel

  def done( s ):
    return s.tm.done()

  def line_trace( s ):
    return s.tm.line_trace()  + " > " + \
           s.xcel.line_trace()

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, raddr, data ):
  return XcelReqMsg(XCEL_TYPE_READ if type_ == 'rd' else XCEL_TYPE_WRITE, raddr, data)

def resp( type_, data ):
  return XcelRespMsg(XCEL_TYPE_READ if type_ == 'rd' else XCEL_TYPE_WRITE, data)

#-------------------------------------------------------------------------
# Test Case: basic
#-------------------------------------------------------------------------

basic_msgs = [
  req( 'wr', 0, 0xa  ), resp( 'wr', 0x0 ),
  req( 'rd', 0, 0x0  ), resp( 'rd', 0xa ),
]

#-------------------------------------------------------------------------
# Test Case: stream
#-------------------------------------------------------------------------

stream_msgs = [
  req( 'wr', 0, 0xa  ), resp( 'wr', 0x0 ),
  req( 'wr', 0, 0xb  ), resp( 'wr', 0x0 ),
  req( 'rd', 0, 0x0  ), resp( 'rd', 0xb ),
  req( 'wr', 0, 0xc  ), resp( 'wr', 0x0 ),
  req( 'wr', 0, 0xd  ), resp( 'wr', 0x0 ),
  req( 'rd', 0, 0x0  ), resp( 'rd', 0xd ),
]

#-------------------------------------------------------------------------
# Test Case: random
#-------------------------------------------------------------------------

random.seed(0xdeadbeef)
random_msgs = []
for i in range(20):
  data = random.randint(0,0xffffffff)
  random_msgs.extend([ req( 'wr', 0, data ), resp( 'wr', 0,   ) ])
  random_msgs.extend([ req( 'rd', 0, 0    ), resp( 'rd', data ) ])

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
  (              "msgs         src_delay sink_delay"),
  [ "basic_0x0",  basic_msgs,  0,        0,   ],
  [ "stream_0x0", stream_msgs, 0,        0,   ],
  [ "random_0x0", random_msgs, 0,        0,   ],
  [ "random_5x0", random_msgs, 5,        0,   ],
  [ "random_0x5", random_msgs, 0,        5,   ],
  [ "random_3x9", random_msgs, 3,        9,   ],
])

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( pytestconfig, test_params, dump_vcd, test_verilog ):
  th = TestHarness()

  th.set_param("top.tm.src.construct",
    msgs=test_params.msgs[::2],
    initial_delay=test_params.src_delay+3,
    interval_delay=test_params.src_delay )

  th.set_param("top.tm.sink.construct",
    msgs=test_params.msgs[1::2],
    initial_delay=test_params.sink_delay+3,
    interval_delay=test_params.sink_delay )

  config_model( th, dump_vcd, test_verilog, ['xcel'] )

  run_sim( th, pytestconfig=pytestconfig )
