#=========================================================================
# 32 bits x 256 words SRAM model
#=========================================================================

from pymtl3                         import *
from pymtl3.passes.backends.verilog import TranslationConfigs
from .SramGenericPRTL               import SramGenericPRTL

class SRAM_32x256_1P( Component ):

  # Make sure widths match the .v

  def construct( s ):

    # clock (in PyMTL simulation it uses implict .clk port when
    # translated to Verilog, actual clock ports should be CE1

    s.CE1  = InPort ()          # clk
    s.WEB1 = InPort ()          # bar( write en )
    s.OEB1 = InPort ()          # bar( out en )
    s.CSB1 = InPort ()          # bar( whole SRAM en )
    s.A1   = InPort ( Bits8  )  # address
    s.I1   = InPort ( Bits32 )  # write data
    s.O1   = OutPort( Bits32 )  # read data

    # instantiate a generic sram inside

    s.sram_generic = SramGenericPRTL( 32, 256 )(
      CE1  = s.CE1,
      WEB1 = s.WEB1,
      OEB1 = s.OEB1,
      CSB1 = s.CSB1,
      A1   = s.A1,
      I1   = s.I1,
      O1   = s.O1
    )

    s.config_verilog_translate = TranslationConfigs(
      translate             = False,
      no_synthesis          = True,
    )
