#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in CalcShamtPRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in CalcShamtVRTL).

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3 import *
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, VerilatorImportConfigs, TranslationConfigs

class IntMulVarLatCalcShamtVRTL( Placeholder, Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.in_ = InPort  (Bits8)
    s.out = OutPort (Bits4)

    # Configurations

    from os import path
    s.config_placeholder = VerilogPlaceholderConfigs(
      # Path to the Verilog source file
      src_file = path.dirname(__file__) + '/IntMulVarLatCalcShamtVRTL.v',
      # Name of the Verilog top level module
      top_module = 'lab1_imul_IntMulVarLatCalcShamtVRTL',
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
  from .IntMulVarLatCalcShamtPRTL import IntMulVarLatCalcShamtPRTL as _cls
elif rtl_language == 'verilog':
  _cls = IntMulVarLatCalcShamtVRTL
else:
  raise Exception("Invalid RTL language!")

class IntMulVarLatCalcShamtRTL( _cls ):
  def construct( s ):
    super().construct()
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = f'lab1_imul_IntMulVarLatCalcShamtRTL',
    )

