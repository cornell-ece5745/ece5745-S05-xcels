#=========================================================================
# Choose PyMTL or Verilog version
#=========================================================================
# Set this variable to 'pymtl' if you are using PyMTL for your RTL design
# (i.e., your design is in IntMulAltPRTL) or set this variable to
# 'verilog' if you are using Verilog for your RTL design (i.e., your
# design is in IntMulAltVRTL).

rtl_language = 'pymtl'

#-------------------------------------------------------------------------
# Do not edit below this line
#-------------------------------------------------------------------------

# This is the PyMTL wrapper for the corresponding Verilog RTL model.

from pymtl3 import *
from pymtl3.passes.backends.verilog import \
    VerilogPlaceholderConfigs, TranslationConfigs

from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMasterIfcRTL
from pymtl3.stdlib.ifcs import mk_mem_msg

from .XcelMsg import XcelReqMsg, XcelRespMsg

class ProcVRTL( Placeholder, Component ):

  # Constructor

  def construct( s, num_cores=1 ):

    # Configurations

    MemReqMsg, MemRespMsg = mk_mem_msg( 8, 32, 32 )

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # Starting F16 we turn core_id into input ports to
    # enable module reusability. In the past it was passed as arguments.

    s.core_id   = InPort( Bits32 )

    # Proc/Mngr Interface

    s.mngr2proc = RecvIfcRTL( Bits32 )
    s.proc2mngr = SendIfcRTL( Bits32 )

    # Instruction Memory Request/Response Interface

    s.imem = MemMasterIfcRTL( MemReqMsg, MemRespMsg )

    # Data Memory Request/Response Interface

    s.dmem = MemMasterIfcRTL( MemReqMsg, MemRespMsg )

    # Accelerator Request/Response Interface

    s.xcel = XcelMasterIfcRTL( XcelReqMsg, XcelRespMsg )

    # val_W port used for counting commited insts.

    s.commit_inst = OutPort()

    # stats_en

    s.stats_en    = OutPort()

    from os import path
    s.config_placeholder = VerilogPlaceholderConfigs(
      # Path to the Verilog source file
      src_file = path.dirname(__file__) + '/ProcVRTL.v',
      # Name of the Verilog top level module
      top_module = 'proc_ProcVRTL',
      # Parameters of the Verilog module
      params = { 'p_num_cores' : num_cores },
      # Port name map
      port_map = {
        'core_id'     : 'core_id',
        'commit_inst' : 'commit_inst',
        'stats_en'    : 'stats_en',

        'imem.req.en'   : 'imemreq_en',
        'imem.req.rdy'  : 'imemreq_rdy',
        'imem.req.msg'  : 'imemreq_msg',

        'imem.resp.en'  : 'imemresp_en',
        'imem.resp.rdy' : 'imemresp_rdy',
        'imem.resp.msg' : 'imemresp_msg',

        'dmem.req.en'   : 'dmemreq_en',
        'dmem.req.rdy'  : 'dmemreq_rdy',
        'dmem.req.msg'  : 'dmemreq_msg',

        'dmem.resp.en'  : 'dmemresp_en',
        'dmem.resp.rdy' : 'dmemresp_rdy',
        'dmem.resp.msg' : 'dmemresp_msg',


        'xcel.req.en'   : 'xcelreq_en',
        'xcel.req.rdy'  : 'xcelreq_rdy',
        'xcel.req.msg'  : 'xcelreq_msg',

        'xcel.resp.en'   : 'xcelresp_en',
        'xcel.resp.rdy'  : 'xcelresp_rdy',
        'xcel.resp.msg'  : 'xcelresp_msg',

        'proc2mngr.en'   : 'proc2mngr_en',
        'proc2mngr.rdy'  : 'proc2mngr_rdy',
        'proc2mngr.msg'  : 'proc2mngr_msg',

        'mngr2proc.en'   : 'mngr2proc_en',
        'mngr2proc.rdy'  : 'mngr2proc_rdy',
        'mngr2proc.msg'  : 'mngr2proc_msg',
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
  from .ProcPRTL import ProcPRTL as _cls
elif rtl_language == 'verilog':
  _cls = ProcVRTL
else:
  raise Exception("Invalid RTL language!")

class ProcRTL( _cls ):
  def construct( s, num_cores=1 ):
    super().construct( num_cores )
    # The translated Verilog must be xRTL.v instead of xPRTL.v
    s.config_verilog_translate = TranslationConfigs(
      translate=False,
      explicit_module_name = f'proc_ProcRTL_{num_cores}core',
  )
