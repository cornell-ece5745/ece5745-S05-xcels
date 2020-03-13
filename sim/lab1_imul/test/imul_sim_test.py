#=========================================================================
# imul_sim_test
#=========================================================================
# Make sure that imul-sim works.

import pytest
import os

from subprocess import check_call, CalledProcessError
from itertools  import product

impls  = [ # "cl-fixed","cl-var","cl-nstage",
           "rtl-scycle","rtl-fixed","rtl-var","rtl-nstage" ]

inputs = [ "small", "large", "lomask", "himask", "lohimask", "sparse"]

# Try all inputs on FL model, and small input on all models

test_cases = []


for impl in impls:
  test_cases.append([ impl, "small" ])

@pytest.mark.parametrize( "impl,input_", test_cases )
def test( impl, input_, test_verilog ):

  # Get path to simulator script

  test_dir = os.path.dirname( os.path.abspath( __file__ ) )
  sim_dir  = os.path.dirname( test_dir )
  sim      = sim_dir + os.path.sep + 'imul-sim'

  # Command

  cmd = [ sim, "--impl", impl, "--input", input_ ]

  # Handle test verilog

  if test_verilog:
    if impl.startswith("rtl"):
      cmd.append( "--translate" )
    else:
      pytest.skip("ignoring non-Verilog tests")

  # Display simulator command line

  print("")
  print("Simulator command line:", ' '.join(cmd))

  # Run the simulator

  try:
    check_call(cmd)
  except CalledProcessError as e:
    raise Exception( "Error running simulator!" )

