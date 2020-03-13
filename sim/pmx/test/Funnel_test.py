#=========================================================================
# Funnel_test.py
#=========================================================================

from pymtl3      import *
from pymtl3.stdlib.ifcs import mk_mem_msg
from pymtl3.stdlib.test import config_model
from pmx.Funnel import Funnel

#-------------------------------------------------------------------------
# test_basic_2x1
#-------------------------------------------------------------------------
# Test driver for the Funnel model with two inputs

def test_basic_2x1( dump_vcd, test_verilog ):

  # Instantiate and elaborate the model
  model = Funnel( mk_mem_msg(8,32,32)[0], 2 )

  config_model( model, dump_vcd, test_verilog )

  model.elaborate()

  # We can call apply if we are 100% sure the top level is not tagged

  model.apply( TranslationImportPass() )

  # Create a simulator

  model.apply( SimulationPass() )

  # Reset test harness

  model.sim_reset(print_line_trace=True)

  # Helper function
  def t( in_, out ):

    # Write the input value to the input ports
    model.in_[0].en  = in_[0]
    model.in_[0].msg = in_[1]
    model.in_[1].en  = in_[2]
    model.in_[1].msg = in_[3]
    model.out.rdy    = in_[4]

    # Ensure that all combinational concurrent blocks are called

    model.eval_combinational()

    # Display line trace

    model.print_line_trace()

    # Verify reference output port
    assert model.in_[0].rdy == out[0]
    assert model.in_[1].rdy == out[1]
    assert model.out.en     == out[2]
    assert model.out.msg    == out[3]

    # Tick simulator by one cycle

    model.tick()

  # Helper function to make messages
  def msg( type_, opaque, addr, len_, data ):
    return mk_mem_msg( 8, 32, 32 )[0]( type_, opaque, addr, len_, data )

  # Cycle-by-cycle tests
  #  in_[0]    in_[0]    in_[1]    in_[1]       out   in_[0] in_[1] out        out
  #   .en      .msg       .en      .msg         rdy     .rdy   .rdy en         msg
  t([  1, msg(1,0,1,0,2),  1,   msg(1,0,2,0,7),  1], [    1,     1,  1, msg(1,0,1,0,2)] )
  t([  1, msg(1,0,1,0,3),  0,   msg(1,0,2,0,8),  1], [    1,     0,  1, msg(1,1,2,0,7)] )
  t([  0, msg(1,0,1,0,4),  1,   msg(1,0,2,0,8),  0], [    0,     1,  0, msg(0,0,0,0,0)] )
  t([  0, msg(1,0,1,0,4),  0,   msg(1,0,2,0,8),  1], [    0,     0,  1, msg(1,0,1,0,3)] )
  t([  1, msg(1,0,1,0,4),  0,   msg(1,0,2,0,9),  1], [    1,     0,  1, msg(1,1,2,0,8)] )
  t([  0, msg(1,0,1,0,5),  0,   msg(1,0,2,0,9),  1], [    0,     1,  1, msg(1,0,1,0,4)] )
  t([  1, msg(1,0,1,0,5),  0,   msg(1,0,2,0,9),  1], [    1,     1,  1, msg(1,0,1,0,5)] )

  model.tick()
  model.tick()
  model.tick()

