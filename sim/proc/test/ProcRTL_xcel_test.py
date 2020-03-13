#=========================================================================
# ProcAltRTL_xcel_test.py
#=========================================================================

import pytest

from pymtl3         import *
from .harness       import *
from proc.ProcRTL  import ProcRTL

#-------------------------------------------------------------------------
# xcel
#-------------------------------------------------------------------------

from . import inst_xcel

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_xcel.gen_basic_test  ),
  asm_test( inst_xcel.gen_bypass_test ),
  asm_test( inst_xcel.gen_random_test ),
])
def test_xcel( pytestconfig, name, test, dump_vcd, test_verilog ):
  run_test( pytestconfig, ProcRTL, test, dump_vcd, test_verilog )

def test_xcel_delays( pytestconfig, dump_vcd, test_verilog ):
  run_test( pytestconfig,
            ProcRTL, inst_xcel.gen_random_test, dump_vcd, test_verilog,
            src_delay=3, sink_delay=10, mem_stall_prob=0.5, mem_latency=3 )

