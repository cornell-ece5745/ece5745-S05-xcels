#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in IntMultNstageStepPRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in IntMulNstageStepVRTL).

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3 import *
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, VerilatorImportConfigs, TranslationConfigs
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL

class IntMulNstageStepVRTL( Placeholder, Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.in_en      = InPort  ()
    s.in_a       = InPort  (Bits32)
    s.in_b       = InPort  (Bits32)
    s.in_result  = InPort  (Bits32)

    s.out_en     = OutPort ()
    s.out_a      = OutPort (Bits32)
    s.out_b      = OutPort (Bits32)
    s.out_result = OutPort (Bits32)

    # Configurations

    from os import path
    s.config_placeholder = VerilogPlaceholderConfigs(
      # Path to the Verilog source file
      src_file = path.dirname(__file__) + '/IntMulNstageStepVRTL.v',
      # Name of the Verilog top level module
      top_module = 'lab1_imul_IntMulNstageStepVRTL',
      # Step unit does not have clk and reset pins
      has_clk   = False,
      has_reset = False,
    )

# See if the course staff want to force testing a specific RTL language
# for their own testing.

import sys
if hasattr( sys, '_called_from_test' ):
  if sys._pymtl_rtl_override:
    rtl_language = sys._pymtl_rtl_override

# Import the appropriate version based on the rtl_language variable

if rtl_language == 'pymtl':
  from .IntMulNstageStepPRTL import IntMulNstageStepPRTL as _cls
elif rtl_language == 'verilog':
  _cls = IntMulNstageStepVRTL
else:
  raise Exception("Invalid RTL language!")

class IntMulNstageStepRTL( _cls ):
  def construct( s ):
    super().construct()
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = 'lab1_imul_IntMulNstageStepRTL',
    )
