#=========================================================================
# IntMulScycleRTL_test
#=========================================================================

import pytest

from pymtl3                    import *
from pymtl3.stdlib.test        import run_sim, config_model
from lab1_imul.IntMulScycleRTL import IntMulScycleRTL

#-------------------------------------------------------------------------
# Reuse tests from fixed-latency RTL model
#-------------------------------------------------------------------------

from .IntMulFixedLatRTL_test import TestHarness, test_case_table

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):

  th = TestHarness( IntMulScycleRTL() )

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
