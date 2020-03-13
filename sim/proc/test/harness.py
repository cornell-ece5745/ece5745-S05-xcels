#=========================================================================
# test_harness
#=========================================================================
# Includes a test harness that composes a processor, src/sink, and test
# memory, and a run_test function.

import struct

from pymtl3 import *

from pymtl3.stdlib.ifcs import mk_mem_msg
from pymtl3.stdlib.test import TestSrcCL, TestSinkCL, config_model, run_sim
from pymtl3.stdlib.cl.MemoryCL   import MemoryCL

from proc.NullXcelRTL      import NullXcelRTL
from proc.tinyrv2_encoding import assemble

#=========================================================================
# TestHarness
#=========================================================================
# Use this with pytest parameterize so that the name of the function that
# generates the assembly test ends up as part of the actual test case
# name. Here is an example:
#
#  @pytest.mark.parametrize( "name,gen_test", [
#    asm_test( gen_basic_test  ),
#    asm_test( gen_bypass_test ),
#    asm_test( gen_value_test  ),
#  ])
#  def test( name, gen_test ):
#    run_test( ProcXFL, gen_test )
#

def asm_test( func ):
  name = func.__name__
  if name.startswith("gen_"):
    name = name[4:]
  if name.endswith("_test"):
    name = name[:-5]

  return (name,func)

#=========================================================================
# TestHarness
#=========================================================================

class TestHarness(Component):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def construct( s, proc_cls ):
    s.commit_inst = OutPort()

    s.src  = TestSrcCL ( Bits32, [] )
    s.sink = TestSinkCL( Bits32, [] )
    s.proc = proc_cls()
    s.xcel = NullXcelRTL()
    s.mem  = MemoryCL( 2 )

    s.proc.commit_inst //= s.commit_inst

    # Processor <-> Proc/Mngr
    s.src.send //= s.proc.mngr2proc
    s.proc.proc2mngr //= s.sink.recv

    # Processor <-> Memory
    s.proc.imem //= s.mem.ifc[0]
    s.proc.dmem //= s.mem.ifc[1]

    s.proc.xcel //= s.xcel.xcel

    # Starting F16 we turn core_id into input ports to
    # enable module reusability. In the past it was passed as arguments.
    s.proc.core_id //= 0

  #-----------------------------------------------------------------------
  # load
  #-----------------------------------------------------------------------

  def load( self, mem_image ):

    # Iterate over the sections

    sections = mem_image.get_sections()
    for section in sections:

      # For .mngr2proc sections, copy section into mngr2proc src

      if section.name == ".mngr2proc":
        for bits in struct.iter_unpack("<I", section.data):
          self.src.msgs.append( b32(bits[0]) )

      # For .proc2mngr sections, copy section into proc2mngr_ref src

      elif section.name == ".proc2mngr":
        for bits in struct.iter_unpack("<I", section.data):
          self.sink.msgs.append( b32(bits[0]) )

      # For all other sections, simply copy them into the memory

      else:
        start_addr = section.addr
        stop_addr  = section.addr + len(section.data)
        self.mem.mem.mem[start_addr:stop_addr] = section.data

  #-----------------------------------------------------------------------
  # cleanup
  #-----------------------------------------------------------------------

  def cleanup( s ):
    del s.mem.mem[:]

  #-----------------------------------------------------------------------
  # done
  #-----------------------------------------------------------------------

  def done( s ):
    return s.src.done() and s.sink.done()

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    return s.src.line_trace()  + " >" + \
           ("- " if s.proc.stats_en else "  ") + \
           s.proc.line_trace() + "|" + \
           s.xcel.line_trace() + "|" + \
           s.mem.line_trace()  + " > " + \
           s.sink.line_trace()

#=========================================================================
# run_test
#=========================================================================

def run_test( pytestconfig, ProcModel, gen_test,
              dump_vcd=None, test_verilog=False,
              src_delay=0, sink_delay=0, mem_stall_prob=0, mem_latency=0,
              max_cycles=10000 ):

  # Instantiate and elaborate the model

  model = TestHarness( ProcModel )

  model.set_param( "top.src.construct",
    initial_delay=src_delay+3, interval_delay=src_delay )

  model.set_param( "top.sink.construct",
    initial_delay=sink_delay+3, interval_delay=sink_delay )

  model.set_param( "top.mem.construct",
    stall_prob=mem_stall_prob, latency=mem_latency+1 )

  model.elaborate()

  mem_image = assemble( gen_test() )
  model.load( mem_image )

  config_model( model, dump_vcd, test_verilog, ['proc'] )

  run_sim( model, pytestconfig=pytestconfig, max_cycles=max_cycles )
