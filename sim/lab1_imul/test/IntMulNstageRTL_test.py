#=========================================================================
# IntMulNstageRTL_test
#=========================================================================

import pytest

from pymtl3                    import *
from pymtl3.stdlib.test        import run_sim, config_model
from lab1_imul.IntMulNstageRTL import IntMulNstageRTL

#-------------------------------------------------------------------------
# Reuse tests from fixed-latency RTL model
#-------------------------------------------------------------------------

from .IntMulFixedLatRTL_test import TestHarness, test_case_table

@pytest.mark.parametrize( **test_case_table )
def test_1stage( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulNstageRTL( nstages=1 ) )

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

@pytest.mark.parametrize( **test_case_table )
def test_2stage( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulNstageRTL( nstages=2 ) )

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

@pytest.mark.parametrize( **test_case_table )
def test_4stage( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulNstageRTL( nstages=4 ) )

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

@pytest.mark.parametrize( **test_case_table )
def test_8stage( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulNstageRTL( nstages=8 ) )

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
