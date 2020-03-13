#=========================================================================
# ProcFL_rr_test.py
#=========================================================================

import pytest

from pymtl3  import *
from .harness import *
from proc.ProcFL import ProcFL

#-------------------------------------------------------------------------
# add
#-------------------------------------------------------------------------

from . import inst_add

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_add.gen_basic_test     ) ,
  asm_test( inst_add.gen_dest_dep_test  ) ,
  asm_test( inst_add.gen_src0_dep_test  ) ,
  asm_test( inst_add.gen_src1_dep_test  ) ,
  asm_test( inst_add.gen_srcs_dep_test  ) ,
  asm_test( inst_add.gen_srcs_dest_test ) ,
  asm_test( inst_add.gen_value_test     ) ,
  asm_test( inst_add.gen_random_test    ) ,
])
def test_add( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_add_rand_delays( pytestconfig ):
  run_test( pytestconfig, ProcFL, inst_add.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# sub
#-------------------------------------------------------------------------

from . import inst_sub

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sub.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_sub.gen_dest_dep_test  ) ,
  asm_test( inst_sub.gen_src0_dep_test  ) ,
  asm_test( inst_sub.gen_src1_dep_test  ) ,
  asm_test( inst_sub.gen_srcs_dep_test  ) ,
  asm_test( inst_sub.gen_srcs_dest_test ) ,
  asm_test( inst_sub.gen_value_test     ) ,
  asm_test( inst_sub.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_sub( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_sub_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sub.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# mul
#-------------------------------------------------------------------------

from . import inst_mul

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_mul.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_mul.gen_dest_dep_test  ) ,
  asm_test( inst_mul.gen_src0_dep_test  ) ,
  asm_test( inst_mul.gen_src1_dep_test  ) ,
  asm_test( inst_mul.gen_srcs_dep_test  ) ,
  asm_test( inst_mul.gen_srcs_dest_test ) ,
  asm_test( inst_mul.gen_value_test     ) ,
  asm_test( inst_mul.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_mul( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_mul_rand_delays( pytestconfig ):
  run_test( pytestconfig, ProcFL, inst_mul.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# and
#-------------------------------------------------------------------------

from . import inst_and

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_and.gen_basic_test     ) ,
  asm_test( inst_and.gen_dest_dep_test  ) ,
  asm_test( inst_and.gen_src0_dep_test  ) ,
  asm_test( inst_and.gen_src1_dep_test  ) ,
  asm_test( inst_and.gen_srcs_dep_test  ) ,
  asm_test( inst_and.gen_srcs_dest_test ) ,
  asm_test( inst_and.gen_value_test     ) ,
  asm_test( inst_and.gen_random_test    ) ,
])
def test_and( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_and_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_and.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# or
#-------------------------------------------------------------------------

from . import inst_or

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_or.gen_basic_test     ) ,
  asm_test( inst_or.gen_dest_dep_test  ) ,
  asm_test( inst_or.gen_src0_dep_test  ) ,
  asm_test( inst_or.gen_src1_dep_test  ) ,
  asm_test( inst_or.gen_srcs_dep_test  ) ,
  asm_test( inst_or.gen_srcs_dest_test ) ,
  asm_test( inst_or.gen_value_test     ) ,
  asm_test( inst_or.gen_random_test    ) ,
])
def test_or( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_or_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_or.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# xor
#-------------------------------------------------------------------------

from . import inst_xor

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_xor.gen_basic_test     ) ,
  asm_test( inst_xor.gen_dest_dep_test  ) ,
  asm_test( inst_xor.gen_src0_dep_test  ) ,
  asm_test( inst_xor.gen_src1_dep_test  ) ,
  asm_test( inst_xor.gen_srcs_dep_test  ) ,
  asm_test( inst_xor.gen_srcs_dest_test ) ,
  asm_test( inst_xor.gen_value_test     ) ,
  asm_test( inst_xor.gen_random_test    ) ,
])
def test_xor( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_xor_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_xor.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# slt
#-------------------------------------------------------------------------

from . import inst_slt

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_slt.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_slt.gen_dest_dep_test  ) ,
  asm_test( inst_slt.gen_src0_dep_test  ) ,
  asm_test( inst_slt.gen_src1_dep_test  ) ,
  asm_test( inst_slt.gen_srcs_dep_test  ) ,
  asm_test( inst_slt.gen_srcs_dest_test ) ,
  asm_test( inst_slt.gen_value_test     ) ,
  asm_test( inst_slt.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_slt( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_slt_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_slt.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# sltu
#-------------------------------------------------------------------------

from . import inst_sltu

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sltu.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_sltu.gen_dest_dep_test  ) ,
  asm_test( inst_sltu.gen_src0_dep_test  ) ,
  asm_test( inst_sltu.gen_src1_dep_test  ) ,
  asm_test( inst_sltu.gen_srcs_dep_test  ) ,
  asm_test( inst_sltu.gen_srcs_dest_test ) ,
  asm_test( inst_sltu.gen_value_test     ) ,
  asm_test( inst_sltu.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_sltu( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_sltu_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sltu.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# sra
#-------------------------------------------------------------------------

from . import inst_sra

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sra.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_sra.gen_dest_dep_test  ) ,
  asm_test( inst_sra.gen_src0_dep_test  ) ,
  asm_test( inst_sra.gen_src1_dep_test  ) ,
  asm_test( inst_sra.gen_srcs_dep_test  ) ,
  asm_test( inst_sra.gen_srcs_dest_test ) ,
  asm_test( inst_sra.gen_value_test     ) ,
  asm_test( inst_sra.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_sra( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_sra_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sra.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# srl
#-------------------------------------------------------------------------

from . import inst_srl

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_srl.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_srl.gen_dest_dep_test  ) ,
  asm_test( inst_srl.gen_src0_dep_test  ) ,
  asm_test( inst_srl.gen_src1_dep_test  ) ,
  asm_test( inst_srl.gen_srcs_dep_test  ) ,
  asm_test( inst_srl.gen_srcs_dest_test ) ,
  asm_test( inst_srl.gen_value_test     ) ,
  asm_test( inst_srl.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_srl( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_srl_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_srl.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
#-------------------------------------------------------------------------
# sll
#-------------------------------------------------------------------------

from . import inst_sll

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sll.gen_basic_test     ) ,

  # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''
  # Add more rows to the test case table to test more complicated
  # scenarios.
  # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  asm_test( inst_sll.gen_dest_dep_test  ) ,
  asm_test( inst_sll.gen_src0_dep_test  ) ,
  asm_test( inst_sll.gen_src1_dep_test  ) ,
  asm_test( inst_sll.gen_srcs_dep_test  ) ,
  asm_test( inst_sll.gen_srcs_dest_test ) ,
  asm_test( inst_sll.gen_value_test     ) ,
  asm_test( inst_sll.gen_random_test    ) ,
  #'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
])
def test_sll( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# random stall and delay
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

def test_sll_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sll.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\
