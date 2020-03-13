#=========================================================================
# VvaddXcelFL_test
#=========================================================================

import pytest
import random
import struct

random.seed(0xdeadbeef)

from pymtl3 import *
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMasterIfcCL
from pymtl3.stdlib.test import TestMasterCL, mk_test_case_table, run_sim, config_model
from pymtl3.stdlib.cl.MemoryCL import MemoryCL

from proc.XcelMsg import *

from tut9_xcel.AccumXcelFL  import AccumXcelFL

#-------------------------------------------------------------------------
# TestHarness
#-------------------------------------------------------------------------

class TestHarness( Component ):

  def construct( s, xcel ):

    s.tm   = TestMasterCL( XcelMsgs.req, XcelMsgs.resp, XcelMasterIfcCL )
    s.mem  = MemoryCL( 1 )
    s.xcel = xcel

    s.tm.master  //= s.xcel.xcel
    s.mem.ifc[0] //= s.xcel.mem

  def done( s ):
    return s.tm.done()

  def line_trace( s ):
    return "{}|{} > {}".format(
      s.tm.line_trace(), s.mem.line_trace(), s.xcel.line_trace()
    )

#-------------------------------------------------------------------------
# make messages
#-------------------------------------------------------------------------

def req( type_, raddr, data ):
  return XcelReqMsg(XCEL_TYPE_READ if type_ == 'rd' else XCEL_TYPE_WRITE, raddr, data)

def resp( type_, data ):
  return XcelRespMsg(XCEL_TYPE_READ if type_ == 'rd' else XCEL_TYPE_WRITE, data)

#-------------------------------------------------------------------------
# Xcel Protocol
#-------------------------------------------------------------------------
# These are the source sink messages we need to configure the accelerator
# and wait for it to finish. We use the same messages in all of our
# tests. The difference between the tests is the data. The variable i is used
# to offset multiple data sets in memory

def gen_xcel_protocol_msgs( size, i ):
  return [
    req( 'wr', 1, 0x1000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 2, 0x2000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 3, 0x3000 + 0x3000*i ), resp( 'wr', 0 ),
    req( 'wr', 4, size              ), resp( 'wr', 0 ),
    req( 'wr', 0, 0                 ), resp( 'wr', 0 ),
    req( 'rd', 0, 0                 ), resp( 'rd', 1 ),
  ]

def gen_xcel_protocol_msgs( size, i, ref ):
  return [
    req( 'wr', 1, 0x1000 + 0x3000*i ), resp( 'wr', 0   ),
    req( 'wr', 2, size              ), resp( 'wr', 0   ),
    req( 'wr', 0, 0                 ), resp( 'wr', 0   ),
    req( 'rd', 0, 0                 ), resp( 'rd', ref ),
  ]

#-------------------------------------------------------------------------
# Test Cases
#-------------------------------------------------------------------------

mini          = [ [ 1, 2, 3, 4 ] ]
small_data    = [ [ random.randint(0,0x0000ffff) for i in range(32) ] ]
large_data    = [ [ random.randint(0,0x00ffffff) for i in range(32) ] ]
multiple      = [ [ random.randint(0,0x00ffffff) for i in range(32) ] for j in range(8) ]

#-------------------------------------------------------------------------
# Test Case Table
#-------------------------------------------------------------------------

test_case_table = mk_test_case_table([
                         #                delays   test mem
                         #                -------- ---------
  (                      "data            src sink stall lat"),
  [ "mini",               mini,           0,  0,   0,    0   ],
  [ "mini_delay_x4",      mini,           3, 14,   0.5,  2   ],
  [ "small_data",         small_data,     0,  0,   0,    0   ],
  [ "large_data",         large_data,     0,  0,   0,    0   ],
  [ "multi_data",         multiple,       0,  0,   0,    0   ],
  [ "small_data_3x14x0",  small_data,     3, 14,   0,    0   ],
  [ "small_data_0x0x4",   small_data,     0,  0,   0.5,  4   ],
  [ "multi_data_3x14x4",  multiple,       3, 14,   0.5,  4   ],
])

#-------------------------------------------------------------------------
# run_test
#-------------------------------------------------------------------------

def run_test( xcel, test_params, dump_vcd, test_verilog=False ):

  # Convert test data into byte array

  data_src = test_params.data
  src_bytes = [0]*len(data_src)
  for i in range( len(data_src) ):
    src_bytes[i] = struct.pack("<{}I".format(len(data_src[i])),*data_src[i])

  # Protocol messages

  xcel_protocol_msgs = []
  for i in range( len(data_src) ):
    result = sum(data_src[i])
    xcel_protocol_msgs += gen_xcel_protocol_msgs( len(data_src[i]), i, result )
  xreqs  = xcel_protocol_msgs[::2]
  xresps = xcel_protocol_msgs[1::2]

  # Create test harness with protocol messagse

  th = TestHarness( xcel )

  th.set_param( "top.tm.src.construct", msgs=xcel_protocol_msgs[::2],
    initial_delay=test_params.src+3, interval_delay=test_params.src )

  th.set_param( "top.tm.sink.construct", msgs=xcel_protocol_msgs[1::2],
    initial_delay=test_params.sink+3, interval_delay=test_params.sink )

  th.set_param( "top.mem.construct",
    stall_prob=test_params.stall, latency=test_params.lat+1 )

  # Load the data into the test memory

  th.elaborate()

  # Load the data into the test memory

  for i in range( len(data_src) ):
    th.mem.write_mem( 0x1000 + 0x3000*i, src_bytes[i] )

  # Run the test

  config_model( th, dump_vcd, test_verilog, ['xcel'] )

  run_sim( th, max_cycles=20000 )

#-------------------------------------------------------------------------
# Test cases
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
  run_test( AccumXcelFL(), test_params, dump_vcd=False, test_verilog=False )

