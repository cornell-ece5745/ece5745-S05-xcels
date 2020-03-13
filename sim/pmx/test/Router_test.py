#=========================================================================
# Router_test.py
#=========================================================================

from pymtl3      import *
from pymtl3.stdlib.ifcs import mk_mem_msg
from pymtl3.stdlib.test import config_model
from pmx.Router import Router

#-------------------------------------------------------------------------
# test_basic_1x2
#-------------------------------------------------------------------------
# Test driver for the Router model with two inputs

def test_basic_1x2( dump_vcd, test_verilog ):

  # Instantiate and elaborate the model
  model = Router( mk_mem_msg(8,32,32)[1], 2 )

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
    model.in_.en     = in_[0]
    model.in_.msg    = in_[1]
    model.out[0].rdy = in_[2]
    model.out[1].rdy = in_[3]

    # Ensure that all combinational concurrent blocks are called

    model.eval_combinational()

    # Display line trace

    model.print_line_trace()

    # Verify reference output port
    assert model.in_.rdy    == out[0]
    assert model.out[0].en  == out[1]
    assert model.out[0].msg == out[2]
    assert model.out[1].en  == out[3]
    assert model.out[1].msg == out[4]

    # Tick simulator by one cycle

    model.tick()

  # Helper function to make messages
  def msg( type_, opaque, test, len_, data ):
    return mk_mem_msg( 8, 32, 32 )[1]( type_, opaque, test, len_, data )

  # Cycle-by-cycle tests
  #  in_      in_         out[0] out[1]  in_  out[0]     out[0]    out[1]    out[1]
  #  .en      .msg        .rdy    rdy    .rdy  .en       .msg      .en       .msg
  t([ 1, msg(0,0,0,0,4),     1,    1], [   1,   1, msg(0,0,0,0,4),  0, msg(0,0,0,0,0)] )
  t([ 1, msg(0,1,0,0,5),     1,    1], [   1,   0, msg(0,0,0,0,0),  1, msg(0,1,0,0,5)] )
  t([ 0, msg(0,1,0,0,5),     1,    1], [   1,   0, msg(0,0,0,0,0),  0, msg(0,0,0,0,0)] )
  t([ 1, msg(0,1,0,0,6),     1,    1], [   1,   0, msg(0,0,0,0,0),  1, msg(0,1,0,0,6)] )
  t([ 1, msg(0,0,0,0,7),     0,    1], [   1,   0, msg(0,0,0,0,0),  0, msg(0,0,0,0,0)] )
  t([ 0, msg(0,1,0,0,8),     0,    1], [   0,   0, msg(0,0,0,0,0),  0, msg(0,0,0,0,0)] )
  t([ 0, msg(0,1,0,0,8),     1,    1], [   0,   1, msg(0,0,0,0,7),  0, msg(0,0,0,0,0)] )
  t([ 1, msg(0,1,0,0,9),     0,    1], [   1,   0, msg(0,0,0,0,0),  1, msg(0,1,0,0,9)] )

  model.tick()
  model.tick()
  model.tick()
