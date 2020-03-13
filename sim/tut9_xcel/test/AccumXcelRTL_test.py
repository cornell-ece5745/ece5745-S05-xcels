#=========================================================================
# AccumXcelRTL_test
#=========================================================================

import pytest

from pymtl3     import *
from tut9_xcel  import AccumXcelRTL

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from .AccumXcelFL_test import TestHarness, test_case_table, run_test

@pytest.mark.parametrize( **test_case_table )
def test( test_params, dump_vcd, test_verilog ):
  run_test( AccumXcelRTL(), test_params, dump_vcd, test_verilog )
