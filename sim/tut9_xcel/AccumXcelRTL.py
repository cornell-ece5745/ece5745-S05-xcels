#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in AccumXcelPRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in AccumXcelVRTL).

rtl_language = 'verilog'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3        import *
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, TranslationConfigs

from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMinionIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs  import MemMasterIfcRTL, mk_mem_msg, MemMsgType

from proc.XcelMsg import XcelReqMsg, XcelRespMsg

class AccumXcelVRTL( Component, Placeholder ):

  # Constructor

  def construct( s ):

    # Interface

    s.xcel = XcelMinionIfcRTL( XcelReqMsg, XcelRespMsg )

    s.mem  = MemMasterIfcRTL( *mk_mem_msg(8,32,32) )

    from os import path
    s.config_placeholder = VerilogPlaceholderConfigs(
      # Path to the Verilog source file
      src_file = path.dirname(__file__) + '/AccumXcelVRTL.v',
      # Name of the Verilog top level module
      top_module = 'tut9_xcel_AccumXcelVRTL',
      # Port name map
      port_map = {
        'xcel.req.en'   : 'xcelreq_en',
        'xcel.req.rdy'  : 'xcelreq_rdy',
        'xcel.req.msg'  : 'xcelreq_msg',

        'xcel.resp.en'  : 'xcelresp_en',
        'xcel.resp.rdy' : 'xcelresp_rdy',
        'xcel.resp.msg' : 'xcelresp_msg',

        'mem.req.en'   : 'memreq_en',
        'mem.req.rdy'  : 'memreq_rdy',
        'mem.req.msg'  : 'memreq_msg',

        'mem.resp.en'  : 'memresp_en',
        'mem.resp.rdy' : 'memresp_rdy',
        'mem.resp.msg' : 'memresp_msg',
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
  from .AccumXcelPRTL import AccumXcelPRTL as _cls
elif rtl_language == 'verilog':
  _cls = AccumXcelVRTL
else:
  raise Exception("Invalid RTL language!")


class AccumXcelRTL( _cls ):
  def construct( s ):
    super().construct()
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = f'tut9_xcel_AccumXcelRTL',
    )

