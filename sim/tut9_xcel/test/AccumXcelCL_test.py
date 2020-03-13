#=========================================================================
# AccumXcelCL_test
#=========================================================================

import pytest

from pymtl3     import *
from tut9_xcel  import AccumXcelCL

#-------------------------------------------------------------------------
# Reuse tests from FL model
#-------------------------------------------------------------------------

from .AccumXcelFL_test import TestHarness, test_case_table, run_test

@pytest.mark.parametrize( **test_case_table )
def test( test_params ):
  run_test( AccumXcelCL(), test_params, dump_vcd=False, test_verilog=False )

