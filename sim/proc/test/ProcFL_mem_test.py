#=========================================================================
# ProcFL_test.py
#=========================================================================

import pytest

from pymtl3   import *
from .harness import *
from proc.ProcFL import ProcFL

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
def test_lw( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_lw_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_lw.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# lb
#-------------------------------------------------------------------------

from . import inst_lb

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lb.gen_basic_test     ) ,
  asm_test( inst_lb.gen_dest_dep_test  ) ,
  asm_test( inst_lb.gen_base_dep_test  ) ,
  asm_test( inst_lb.gen_srcs_dest_test ) ,
  asm_test( inst_lb.gen_endian_test    ) ,
  asm_test( inst_lb.gen_sext_test      ) ,
  asm_test( inst_lb.gen_addr_test      ) ,
  asm_test( inst_lb.gen_random_test    ) ,
])
def test_lb( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_lb_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_lb.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# lh
#-------------------------------------------------------------------------

from . import inst_lh

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lh.gen_basic_test     ) ,
  asm_test( inst_lh.gen_dest_dep_test  ) ,
  asm_test( inst_lh.gen_base_dep_test  ) ,
  asm_test( inst_lh.gen_srcs_dest_test ) ,
  asm_test( inst_lh.gen_endian_test    ) ,
  asm_test( inst_lh.gen_sext_test      ) ,
  asm_test( inst_lh.gen_addr_test      ) ,
  asm_test( inst_lh.gen_random_test    ) ,
])
def test_lh( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_lh_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_lh.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )
#-------------------------------------------------------------------------
# lbu
#-------------------------------------------------------------------------

from . import inst_lbu

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lbu.gen_basic_test     ) ,
  asm_test( inst_lbu.gen_dest_dep_test  ) ,
  asm_test( inst_lbu.gen_base_dep_test  ) ,
  asm_test( inst_lbu.gen_srcs_dest_test ) ,
  asm_test( inst_lbu.gen_endian_test    ) ,
  asm_test( inst_lbu.gen_zext_test      ) ,
  asm_test( inst_lbu.gen_addr_test      ) ,
  asm_test( inst_lbu.gen_random_test    ) ,
])
def test_lbu( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_lbu_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_lbu.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# lhu
#-------------------------------------------------------------------------

from . import inst_lhu

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_lhu.gen_basic_test     ) ,
  asm_test( inst_lhu.gen_dest_dep_test  ) ,
  asm_test( inst_lhu.gen_base_dep_test  ) ,
  asm_test( inst_lhu.gen_srcs_dest_test ) ,
  asm_test( inst_lhu.gen_endian_test    ) ,
  asm_test( inst_lhu.gen_zext_test      ) ,
  asm_test( inst_lhu.gen_addr_test      ) ,
  asm_test( inst_lhu.gen_random_test    ) ,
])
def test_lhu( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_lhu_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_lhu.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# sb
#-------------------------------------------------------------------------

from . import inst_sb

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sb.gen_basic_test     ),
  asm_test( inst_sb.gen_dest_dep_test  ),
  asm_test( inst_sb.gen_base_dep_test  ),
  asm_test( inst_sb.gen_src_dep_test   ),
  asm_test( inst_sb.gen_srcs_dep_test  ),
  asm_test( inst_sb.gen_srcs_dest_test ),
  asm_test( inst_sb.gen_addr1_test     ),
  asm_test( inst_sb.gen_addr2_test     ),
  asm_test( inst_sb.gen_random_test    ),
])
def test_sb( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_sb_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sb.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# sh
#-------------------------------------------------------------------------

from . import inst_sh

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sh.gen_basic_test     ),
  asm_test( inst_sh.gen_dest_dep_test  ),
  asm_test( inst_sh.gen_base_dep_test  ),
  asm_test( inst_sh.gen_src_dep_test   ),
  asm_test( inst_sh.gen_srcs_dep_test  ),
  asm_test( inst_sh.gen_srcs_dest_test ),
  asm_test( inst_sh.gen_addr1_test     ),
  asm_test( inst_sh.gen_addr2_test     ),
  asm_test( inst_sh.gen_random_test    ),
])
def test_sh( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_sh_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sh.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )

#-------------------------------------------------------------------------
# sw
#-------------------------------------------------------------------------

from . import inst_sw

@pytest.mark.parametrize( "name,test", [
  asm_test( inst_sw.gen_basic_test     ),
  asm_test( inst_sw.gen_dest_dep_test  ),
  asm_test( inst_sw.gen_base_dep_test  ),
  asm_test( inst_sw.gen_src_dep_test   ),
  asm_test( inst_sw.gen_srcs_dep_test  ),
  asm_test( inst_sw.gen_srcs_dest_test ),
  asm_test( inst_sw.gen_addr_test      ),
  asm_test( inst_sw.gen_random_test    ),
])
def test_sw( pytestconfig, name, test ):
  run_test( pytestconfig, ProcFL, test )

def test_sw_rand_delays( pytestconfig ):
  run_test( pytestconfig,
            ProcFL, inst_sw.gen_random_test,
            src_delay=3, sink_delay=5, mem_stall_prob=0.5, mem_latency=3 )
