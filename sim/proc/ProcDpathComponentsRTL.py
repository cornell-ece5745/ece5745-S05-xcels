#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in IntMultBasePRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in IntMulBaseVRTL).

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# PyMTL wrappers for the corresponding Verilog RTL models.

from os import path
from pymtl3 import *
from pymtl3.passes.backends.verilog import VerilogPlaceholderConfigs, TranslationConfigs

class ImmGenVRTL( Placeholder, Component ):

  # Constructor

  def construct( s ):

    s.imm_type = InPort( Bits3 )
    s.inst     = InPort( Bits32 )

    s.imm      = OutPort( Bits32 )

    # Verilog module setup

    s.config_placeholder = VerilogPlaceholderConfigs(
      src_file = path.dirname(__file__) + '/ProcDpathComponentsVRTL.v',
      top_module = 'proc_ImmGenVRTL',
      has_clk   = False,
      has_reset = False,
    )
    s.config_verilog_translate = TranslationConfigs(
      translate = False,
      explicit_module_name = 'proc_ImmGenRTL',
    )

class AluVRTL( Placeholder, Component ):

  # Constructor

  def construct( s ):

    s.in0      = InPort ( Bits32 )
    s.in1      = InPort ( Bits32 )
    s.fn       = InPort ( Bits4 )

    s.out      = OutPort( Bits32 )
    s.ops_eq   = OutPort()
    s.ops_lt   = OutPort()
    s.ops_ltu  = OutPort()

    # Verilog module setup

    s.config_placeholder = VerilogPlaceholderConfigs(
      src_file = path.dirname(__file__) + '/ProcDpathComponentsVRTL.v',
      top_module = 'proc_AluVRTL',
      has_clk   = False,
      has_reset = False,
    )
    s.config_verilog_translate = TranslationConfigs(
      translate = False,
      explicit_module_name = 'proc_AluRTL',
    )


# See if the course staff want to force testing a specific RTL language
# for their own testing.

import sys
if hasattr( sys, '_called_from_test' ):
  if sys._pymtl_rtl_override:
    rtl_language = sys._pymtl_rtl_override

# Import the appropriate version based on the rtl_language variable

if rtl_language == 'pymtl':
  from .ProcDpathComponentsPRTL import ImmGenPRTL as ImmGenRTL
  from .ProcDpathComponentsPRTL import AluPRTL    as AluRTL
elif rtl_language == 'verilog':
  ImmGenRTL = ImmGenVRTL
  AluRTL    = AluVRTL
else:
  raise Exception("Invalid RTL language!")
