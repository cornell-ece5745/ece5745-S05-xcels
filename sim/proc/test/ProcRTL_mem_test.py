#=========================================================================
# ProcRTL_test.py
#=========================================================================

import pytest

from pymtl3   import *
from .harness import *
from proc.ProcRTL import ProcRTL

#-------------------------------------------------------------------------
# lw
#-------------------------------------------------------------------------

from . import inst_lw

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lw.gen_basic_test     ) ,
  asm_test( inst_lw.gen_dest_dep_test  ) ,
  asm_test( inst_lw.gen_base_dep_test  ) ,
  asm_test( inst_lw.gen_srcs_dest_test ) ,
  asm_test( inst_lw.gen_addr_test      ) ,
  asm_test( inst_lw.gen_random_test    ) ,
])
def test_lw( pytestconfig, name, test, dump_vcd, test_verilog ):
  run_test( pytestconfig, ProcRTL, test, dump_vcd, test_verilog )

def test_lw_rand_delays( pytestconfig, dump_vcd, test_verilog ):
  run_test( pytestconfig,
            ProcRTL, inst_lw.gen_random_test, dump_vcd, test_verilog,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# sw
#-------------------------------------------------------------------------

from . import inst_sw

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sw.gen_basic_test     ),

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_sw.gen_dest_dep_test  ),
  asm_test( inst_sw.gen_base_dep_test  ),
  asm_test( inst_sw.gen_src_dep_test   ),
  asm_test( inst_sw.gen_srcs_dep_test  ),
  asm_test( inst_sw.gen_srcs_dest_test ),
  asm_test( inst_sw.gen_addr_test      ),
  asm_test( inst_sw.gen_random_test    ),

  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_sw( pytestconfig, name, test, dump_vcd, test_verilog ):
  run_test( pytestconfig, ProcRTL, test, dump_vcd, test_verilog )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_sw_rand_delays( pytestconfig, dump_vcd, test_verilog ):
  run_test( pytestconfig,
            ProcRTL, inst_sw.gen_random_test, dump_vcd, test_verilog,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
