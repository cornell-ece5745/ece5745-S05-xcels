#=========================================================================
# ProcRTL_mix_test.py
#=========================================================================

import pytest

from pymtl3   import *
from .harness import *
from proc.ProcRTL import ProcRTL

#-------------------------------------------------------------------------
# jal_beq
#-------------------------------------------------------------------------

from . import inst_jal_beq

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_jal_beq.gen_basic_test     ) ,
])
def test_jal_beq( pytestconfig, name, test, dump_vcd, test_verilog ):
  run_test( pytestconfig, ProcRTL, test, dump_vcd, test_verilog )

#-------------------------------------------------------------------------
# mul_mem
#-------------------------------------------------------------------------

from . import inst_mul_mem

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_mul_mem.gen_basic_test     ) ,
  asm_test( inst_mul_mem.gen_more_test      ) ,
])
def test_mul_mem( pytestconfig, name, test, dump_vcd, test_verilog ):
  run_test( pytestconfig, ProcRTL, test, dump_vcd, test_verilog )
