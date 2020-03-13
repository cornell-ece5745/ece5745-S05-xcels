#=========================================================================
# Integer Multiplier N-Stage Pipelined RTL Model
#=========================================================================

from pymtl3 import *
from pymtl3.stdlib.ifcs import MinionIfcRTL
from pymtl3.stdlib.rtl  import RegEn
from pymtl3.passes.backends.verilog import TranslationConfigs

from .IntMulMsgs import IntMulMsgs

# ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
# Import your partial product step model here. Make sure you unit test it!
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from .IntMulNstageStepRTL import IntMulNstageStepRTL

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class IntMulNstagePRTL( Component ):

  # Constructor

  def construct( s, nstages=2 ):

    # Interface

    s.minion = MinionIfcRTL( IntMulMsgs.req, IntMulMsgs.resp )

    # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Instantiate the partial product steps here. Your design should be
    # parameterized by the number of pipeline stages given by the nstages
    # parameter.
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    # We currently only support power of two number of stages

    assert nstages in [1,2,4,8,16,32]
    nsteps = 32 / nstages

    # Input registers

    s.en_reg = RegEn(Bits1)
    s.a_reg  = RegEn(Bits32)
    s.b_reg  = RegEn(Bits32)

    s.en_reg.in_ //= s.minion.req.en
    s.en_reg.en  //= s.minion.resp.rdy

    s.a_reg.in_ //= s.minion.req.msg.a
    s.a_reg.en  //= s.minion.resp.rdy

    s.b_reg.in_ //= s.minion.req.msg.b
    s.b_reg.en  //= s.minion.resp.rdy

    # Instantiate steps

    s.steps = [ IntMulNstageStepRTL() for _ in range(32) ]

    # Structural composition for first step

    s.steps[0].in_result //= 0
    s.steps[0].in_en     //= s.en_reg.out
    s.steps[0].in_a      //= s.a_reg.out
    s.steps[0].in_b      //= s.b_reg.out

    # Pipeline registers

    s.en_preg     = [ RegEn(Bits1)  for _ in range(nstages-1) ]
    s.a_preg      = [ RegEn(Bits32) for _ in range(nstages-1) ]
    s.b_preg      = [ RegEn(Bits32) for _ in range(nstages-1) ]
    s.result_preg = [ RegEn(Bits32) for _ in range(nstages-1) ]

    # Structural composition for intermediate steps

    nstage = 0
    for i in range(1,32):

      # Insert a pipeline register

      if i % nsteps == 0:

        #  print "-- pipe reg --"
        #  print "step = {}".format(i)

        s.en_preg[nstage].in_     //= s.steps[i-1].out_en
        s.a_preg[nstage].in_      //= s.steps[i-1].out_a
        s.b_preg[nstage].in_      //= s.steps[i-1].out_b
        s.result_preg[nstage].in_ //= s.steps[i-1].out_result

        s.steps[i].in_en          //= s.en_preg[nstage].out
        s.steps[i].in_a           //= s.a_preg[nstage].out
        s.steps[i].in_b           //= s.b_preg[nstage].out
        s.steps[i].in_result      //= s.result_preg[nstage].out

        s.en_preg[nstage].en      //= s.minion.resp.rdy
        s.a_preg[nstage].en       //= s.minion.resp.rdy
        s.b_preg[nstage].en       //= s.minion.resp.rdy
        s.result_preg[nstage].en  //= s.minion.resp.rdy

        nstage += 1

      # No pipeline register

      else:

        #  print "step = {}".format(i)

        s.steps[i].in_en     //= s.steps[i-1].out_en
        s.steps[i].in_a      //= s.steps[i-1].out_a
        s.steps[i].in_b      //= s.steps[i-1].out_b
        s.steps[i].in_result //= s.steps[i-1].out_result

    # Structural composition for last step

    s.minion.resp.en  //= lambda: s.steps[31].out_en & s.minion.resp.rdy
    s.minion.resp.msg //= s.steps[31].out_result

    # Wire resp rdy to req rdy

    s.minion.req.rdy //= s.minion.resp.rdy

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  # Line tracing

  def line_trace( s ):

    s.trace = ""

    # ''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Add line tracing code here.
    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

    s.trace = "{}({}{}){}".format(
      s.minion.req,
      ('*' if s.en_reg.out else ' '),
      ''.join([ ('*' if x.out else ' ') for x in s.en_preg ]),
      s.minion.resp
    )

    # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

    return s.trace

