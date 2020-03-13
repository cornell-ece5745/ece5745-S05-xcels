#=========================================================================
# Integer Multiplier Fixed Latency RTL Model
#=========================================================================

from pymtl3             import *
from pymtl3.stdlib.ifcs import MinionIfcRTL
from pymtl3.stdlib.rtl  import Mux, Reg, RegEn, RegRst
from pymtl3.stdlib.rtl  import LeftLogicalShifter, RightLogicalShifter, Adder
from pymtl3.stdlib.rtl  import ZeroComparator
from pymtl3.passes.backends.verilog import TranslationConfigs

from .IntMulMsgs import IntMulMsgs

#=========================================================================
# Constants
#=========================================================================

A_MUX_SEL_NBITS      = 1
A_MUX_SEL_LSH        = 0
A_MUX_SEL_LD         = 1
A_MUX_SEL_X          = 0

B_MUX_SEL_NBITS      = 1
B_MUX_SEL_RSH        = 0
B_MUX_SEL_LD         = 1
B_MUX_SEL_X          = 0

RESULT_MUX_SEL_NBITS = 1
RESULT_MUX_SEL_ADD   = 0
RESULT_MUX_SEL_0     = 1
RESULT_MUX_SEL_X     = 0

ADD_MUX_SEL_NBITS    = 1
ADD_MUX_SEL_ADD      = 0
ADD_MUX_SEL_RESULT   = 1
ADD_MUX_SEL_X        = 0

#=========================================================================
# Integer Multiplier Fixed Latency Datapath
#=========================================================================

class IntMulFixedLatDpathRTL( Component ):

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_msg_a      = InPort ( Bits32 )
    s.req_msg_b      = InPort ( Bits32 )
    s.resp_msg       = OutPort( Bits32 )

    # Control signals (ctrl -> dpath)

    s.a_mux_sel      = InPort( mk_bits(A_MUX_SEL_NBITS) )
    s.b_mux_sel      = InPort( mk_bits(B_MUX_SEL_NBITS) )
    s.result_mux_sel = InPort( mk_bits(RESULT_MUX_SEL_NBITS) )
    s.result_reg_en  = InPort()
    s.add_mux_sel    = InPort( mk_bits(ADD_MUX_SEL_NBITS) )

    # Status signals (dpath -> ctrl)

    s.b_lsb          = OutPort()

    #---------------------------------------------------------------------
    # Struction composition
    #---------------------------------------------------------------------

    # B mux

    s.rshifter_out = Wire( Bits32 )

    s.b_mux = Mux( Bits32, 2 )(
      sel = s.b_mux_sel,
      in_ = { B_MUX_SEL_RSH: s.rshifter_out,
              B_MUX_SEL_LD : s.req_msg_b }
    )

    # B register

    s.b_reg = Reg( Bits32 )( in_ = s.b_mux.out )

    # Right shifter

    s.rshifter = RightLogicalShifter( Bits32, 4 )(
      in_   = s.b_reg.out,
      shamt = 1,
      out   = s.rshifter_out,
    )

    # A mux

    s.lshifter_out = Wire( Bits32 )

    s.a_mux = Mux( Bits32, 2 )(
      sel = s.a_mux_sel,
      in_ = { A_MUX_SEL_LSH: s.lshifter_out,
              A_MUX_SEL_LD : s.req_msg_a }
    )

    # A register

    s.a_reg = Reg( Bits32 )( in_ = s.a_mux.out )

    # Left shifter

    s.lshifter = LeftLogicalShifter( Bits32, 4 )(
      in_   = s.a_reg.out,
      shamt = 1,
      out   = s.lshifter_out,
    )

    # Result mux

    s.add_mux_out = Wire( Bits32 )

    s.result_mux = Mux( Bits32, 2 )(
      sel = s.result_mux_sel,
      in_ = { RESULT_MUX_SEL_ADD: s.add_mux_out,
              RESULT_MUX_SEL_0  : 0 }
    )

    # Result register

    s.result_reg = RegEn( Bits32 )(
      en  = s.result_reg_en,
      in_ = s.result_mux.out,
    )

    # Adder

    s.add = Adder(Bits32)(
      in0 = s.a_reg.out,
      in1 = s.result_reg.out,
    )

    # Add mux

    s.add_mux = m = Mux( Bits32, 2 )(
      sel = s.add_mux_sel,
      in_ = { ADD_MUX_SEL_ADD   : s.add.out,
              ADD_MUX_SEL_RESULT: s.result_reg.out },
      out = s.add_mux_out,
    )

    # Status signals

    s.b_lsb //= s.b_reg.out[0]

    # Connect to output port

    s.resp_msg //= s.result_reg.out

#=========================================================================
# Integer Multiplier Fixed Latency Control
#=========================================================================

class IntMulFixedLatCtrlRTL( Component ):

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.req_en         = InPort  ()
    s.req_rdy        = OutPort ()

    s.resp_en        = OutPort ()
    s.resp_rdy       = InPort  ()

    # Control signals (ctrl -> dpath)

    s.a_mux_sel      = OutPort ( mk_bits(A_MUX_SEL_NBITS) )
    s.b_mux_sel      = OutPort ( mk_bits(B_MUX_SEL_NBITS) )
    s.result_mux_sel = OutPort ( mk_bits(RESULT_MUX_SEL_NBITS) )
    s.result_reg_en  = OutPort ()
    s.add_mux_sel    = OutPort ( mk_bits(ADD_MUX_SEL_NBITS) )

    # Status signals (dpath -> ctrl)

    s.b_lsb          = InPort ()

    # State element

    s.STATE_IDLE  = b2(0)
    s.STATE_CALC  = b2(1)
    s.STATE_DONE  = b2(2)

    s.state    = Wire( Bits2 )
    s.counter  = RegRst( Bits6, reset_value = 31 )

    #---------------------------------------------------------------------
    # State transitions
    #---------------------------------------------------------------------

    @s.update_ff
    def state_transitions():

      if s.reset:
        s.state <<= s.STATE_IDLE

      # Transistions out of IDLE state

      elif s.state == s.STATE_IDLE:
        if s.req_en:
          s.state <<= s.STATE_CALC

      # Transistions out of CALC state

      if s.state == s.STATE_CALC:
        if s.counter.out == b6(0):
          s.state <<= s.STATE_DONE

      # Transistions out of DONE state

      if s.state == s.STATE_DONE:
        if s.resp_en:
          s.state <<= s.STATE_IDLE

    #---------------------------------------------------------------------
    # State outputs
    #---------------------------------------------------------------------

    s.do_sh_add = Wire()
    s.do_sh     = Wire()

    @s.update
    def state_outputs():

      # Initialize all control signals

      s.do_sh_add      = b1(0)
      s.do_sh          = b1(0)

      s.req_rdy        = b1(0)
      s.resp_en        = b1(0)

      s.a_mux_sel      = b1(0)
      s.b_mux_sel      = b1(0)
      s.result_mux_sel = b1(0)
      s.result_reg_en  = b1(0)
      s.add_mux_sel    = b1(0)

      s.counter.in_    = b6(0)

      # In IDLE state we simply wait for inputs to arrive and latch them

      if s.state == s.STATE_IDLE:

        s.req_rdy        = b1(1)
        s.resp_en        = b1(0)

        s.a_mux_sel      = b1(A_MUX_SEL_LD)
        s.b_mux_sel      = b1(B_MUX_SEL_LD)
        s.result_mux_sel = b1(RESULT_MUX_SEL_0)
        s.result_reg_en  = b1(1)
        s.add_mux_sel    = b1(ADD_MUX_SEL_X)

        s.counter.in_    = b6(31)

      # In CALC state we iteratively add/shift to caculate mult

      elif s.state == s.STATE_CALC:

        s.do_sh_add      = s.b_lsb == b1(1) # do shift and add
        s.do_sh          = s.b_lsb == b1(0) # do shift but no add

        s.req_rdy        = b1(0)
        s.resp_en        = b1(0)

        s.a_mux_sel      = b1(A_MUX_SEL_LSH)
        s.b_mux_sel      = b1(B_MUX_SEL_RSH)
        s.result_mux_sel = b1(RESULT_MUX_SEL_ADD)
        s.result_reg_en  = b1(1)
        if s.do_sh_add:
          s.add_mux_sel  = b1(ADD_MUX_SEL_ADD)
        else:
          s.add_mux_sel  = b1(ADD_MUX_SEL_RESULT)

        s.counter.in_    = s.counter.out - b6(1)

      # In DONE state we simply wait for output transition to occur

      elif s.state == s.STATE_DONE:

        s.req_rdy        = b1(0)
        s.resp_en        = s.resp_rdy

        s.a_mux_sel      = b1(A_MUX_SEL_X)
        s.b_mux_sel      = b1(B_MUX_SEL_X)
        s.result_mux_sel = b1(RESULT_MUX_SEL_X)
        s.result_reg_en  = b1(0)
        s.add_mux_sel    = b1(ADD_MUX_SEL_X)

        s.counter.in_    = b6(31)

#=========================================================================
# Integer Multiplier Fixed Latency
#=========================================================================

class IntMulFixedLatPRTL( Component ):

  # Constructor

  def construct( s ):

    # Interface

    s.minion = MinionIfcRTL( IntMulMsgs.req, IntMulMsgs.resp )

    # Instantiate datapath and control

    s.dpath = IntMulFixedLatDpathRTL()\
    (
      req_msg_a      = s.minion.req.msg.a,
      req_msg_b      = s.minion.req.msg.b,
      resp_msg       = s.minion.resp.msg,
    )

    s.ctrl = IntMulFixedLatCtrlRTL()\
    (
      req_en         = s.minion.req.en,
      req_rdy        = s.minion.req.rdy,
      resp_en        = s.minion.resp.en,
      resp_rdy       = s.minion.resp.rdy,

      a_mux_sel      = s.dpath.a_mux_sel,
      b_mux_sel      = s.dpath.b_mux_sel,
      result_mux_sel = s.dpath.result_mux_sel,
      result_reg_en  = s.dpath.result_reg_en,
      add_mux_sel    = s.dpath.add_mux_sel,
      b_lsb          = s.dpath.b_lsb,
    )

  # Line tracing

  def line_trace( s ):

    if s.ctrl.state == s.ctrl.STATE_IDLE:
      line_trace_str = "I "

    elif s.ctrl.state == s.ctrl.STATE_CALC:
      if s.ctrl.do_sh_add:
        line_trace_str = "C+"
      elif s.ctrl.do_sh:
        line_trace_str = "C "
      else:
        line_trace_str = "C?"

    elif s.ctrl.state == s.ctrl.STATE_DONE:
      line_trace_str = "D "

    return "({} {} {} {})".format(
      s.dpath.a_reg.out,
      s.dpath.b_reg.out,
      s.dpath.result_reg.out,
      line_trace_str,
    )

