#=========================================================================
# Integer Multiplier Single-Cycle RTL Model
#=========================================================================

from pymtl3     import *
from pymtl3.stdlib.ifcs import MinionIfcRTL
from pymtl3.stdlib.rtl  import RegEn
from pymtl3.passes.backends.verilog import TranslationConfigs
from .IntMulMsgs import IntMulMsgs

class IntMulScyclePRTL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.minion = MinionIfcRTL( IntMulMsgs.req, IntMulMsgs.resp )

    # Input registers

    s.en_reg = RegEn(Bits1 )
    s.a_reg  = RegEn(Bits32)
    s.b_reg  = RegEn(Bits32)

    # Structional composition

    s.minion.req.en    //= s.en_reg.in_
    s.minion.req.msg.a //= s.a_reg.in_
    s.minion.req.msg.b //= s.b_reg.in_

    @s.update
    def comb_resp_en():
      s.minion.resp.en = s.en_reg.out & s.minion.resp.rdy

    s.minion.resp.rdy //= s.minion.req.rdy
    s.minion.resp.rdy //= s.en_reg.en
    s.minion.resp.rdy //= s.a_reg.en
    s.minion.resp.rdy //= s.b_reg.en

    # Combinational single-cycle multiplier

    s.result = Wire( Bits64 )

    @s.update
    def block():
      s.result = sext( s.a_reg.out, 64 ) * sext( s.b_reg.out, 64 )
      s.minion.resp.msg = s.result[0:32]

  # Line tracing

  def line_trace( s ):
    return f"{s.minion}"
