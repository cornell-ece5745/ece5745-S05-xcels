#=========================================================================
# BlockingCacheRTL_test.py
#=========================================================================

from __future__ import print_function

import pytest
import random
import struct

from pymtl3      import *
from pymtl3.stdlib.test import run_sim, config_model

from cache.BlockingCacheRTL import BlockingCacheRTL
from .BlockingCacheFL_test import *

# We import tests defined in BlockingCacheFL_test.py. The idea is we can
# use the same tests for both FL and RTL model.
#
# Notice the difference between the TestHarness instances in FL and RTL.
#
# class TestHarness( Model ):
#   def __init__( s, src_msgs, sink_msgs, stall_prob, latency,
#                 src_delay, sink_delay, CacheModel, check_test, dump_vcd )
#
# The last parameter of TestHarness, check_test is whether or not we
# check the test field in the cacheresp. In FL model we don't care about
# test field and we set cehck_test to be False because FL model is just
# passing through cachereq to mem, so all cachereq sent to the FL model
# will be misses, whereas in RTL model we must set cehck_test to be True
# so that the test sink will know if we hit the cache properly.

#-------------------------------------------------------------------------
# Generic tests for both baseline and alternative design
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table_generic )
def test_generic( test_params, dump_vcd, test_verilog ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem = test_params.mem_data_func( 0 )

  # Instantiate testharness
  th = TestHarness( BlockingCacheRTL(), check_test=True )

  th.set_param("top.src.construct",
    msgs=msgs[::2],
    initial_delay=test_params.src+3,
    interval_delay=test_params.src )

  th.set_param("top.sink.construct",
    msgs=msgs[1::2],
    initial_delay=test_params.sink+3,
    interval_delay=test_params.sink )

  th.set_param("top.mem.construct",
    stall_prob=test_params.stall, latency=test_params.lat+1 )

  th.elaborate()

  # Load memory before the test
  if test_params.mem_data_func != None:
    th.load( mem[::2], mem[1::2] )

  config_model( th, dump_vcd, test_verilog, ['cache'] )

  # Run the test
  run_sim( th )

#-------------------------------------------------------------------------
# Tests only for two-way set-associative cache
#-------------------------------------------------------------------------

@pytest.mark.parametrize( **test_case_table_set_assoc )
def test_set_assoc( test_params, dump_vcd, test_verilog ):
  msgs = test_params.msg_func( 0 )
  if test_params.mem_data_func != None:
    mem  = test_params.mem_data_func( 0 )

  # Instantiate testharness
  th = TestHarness( BlockingCacheRTL(), check_test=True )

  th.set_param("top.src.construct",
    msgs=msgs[::2],
    initial_delay=test_params.src+3,
    interval_delay=test_params.src )

  th.set_param("top.sink.construct",
    msgs=msgs[1::2],
    initial_delay=test_params.sink+3,
    interval_delay=test_params.sink )

  th.set_param("top.mem.construct",
    stall_prob=test_params.stall, latency=test_params.lat+1 )

  th.elaborate()

  # Load memory before the test
  if test_params.mem_data_func != None:
    th.load( mem[::2], mem[1::2] )

  config_model( th, dump_vcd, test_verilog, ['cache'] )

  # Run the test
  run_sim( th )

