#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in IntMultFixedLatPRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in IntMulFixedLatVRTL).

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3 import *
from pymtl3.stdlib.ifcs   import MinionIfcRTL
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, TranslationConfigs

from .IntMulMsgs import IntMulMsgs

class IntMulFixedLatVRTL( Placeholder, Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.minion = MinionIfcRTL( IntMulMsgs.req, IntMulMsgs.resp )

    from os import path
    s.config_placeholder = VerilogPlaceholderConfigs(
      # Path to the Verilog source file
      src_file = path.dirname(__file__) + '/IntMulFixedLatVRTL.v',
      # Name of the Verilog top level module
      top_module = 'lab1_imul_IntMulFixedLatVRTL',
      # Port name map
      port_map = {
        'minion.req.en'   : 'req_en',
        'minion.req.rdy'  : 'req_rdy',
        'minion.req.msg'  : 'req_msg',

        'minion.resp.en'  : 'resp_en',
        'minion.resp.rdy' : 'resp_rdy',
        'minion.resp.msg' : 'resp_msg',
      },
    )
    s.config_verilog_import = VerilatorImportConfigs(
      # Enable native Verilog line trace through Verilator
      vl_line_trace = True,
    )

# See if the course staff want to force testing a specific RTL language
# for their own testing.

import sys
if hasattr( sys, '_called_from_test' ):
  if sys._pymtl_rtl_override:
    rtl_language = sys._pymtl_rtl_override

# Import the appropriate version based on the rtl_language variable

if rtl_language == 'pymtl':
  from .IntMulFixedLatPRTL import IntMulFixedLatPRTL as _cls
elif rtl_language == 'verilog':
  _cls = IntMulFixedLatVRTL
else:
  raise Exception("Invalid RTL language!")

class IntMulFixedLatRTL( _cls ):
  def construct( s ):
    super().construct()
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = 'lab1_imul_IntMulFixedLatRTL',
    )
