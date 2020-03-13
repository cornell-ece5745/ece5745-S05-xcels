#=========================================================================
# Funnel.py
#=========================================================================
# The Funnel model is a val-rdy based arbiter model that selects a single
# val-rdy message source given a number of sources. NOTE: The message is
# assumed to have an opaque field.
from copy import deepcopy

from pymtl3      import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl  import BypassQueueRTL, RoundRobinArbiterEn

#-------------------------------------------------------------------------
# Funnel
#-------------------------------------------------------------------------

class Funnel( Component ):

  def construct( s, MsgType, nports ):
    DataType = mk_bits(nports)
    OpaqueType = MsgType.get_field_type( 'opaque' )

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_ = [ RecvIfcRTL( MsgType ) for _ in range(nports) ]
    s.out = SendIfcRTL( MsgType )

    s.qs = [ BypassQueueRTL( MsgType, 1 )( enq = s.in_[i] )
              for i in range(nports) ]

    #---------------------------------------------------------------------
    # Setup round robin arbiter
    #---------------------------------------------------------------------
    # Notice that we AND the output ready with each request signal, so
    # if the output port is not ready we do not make any requests to the
    # arbiter. This will prevent the arbiter priority from changing.

    s.vals    = Wire( mk_bits(nports) )
    s.arbiter = RoundRobinArbiterEn( nports )( en = 1 )

    @s.update
    def arbiter_logic():
      s.vals = DataType(0)
      s.arbiter.reqs = DataType(0)
      for i in range( nports ):
        s.qs[i].deq.en = b1(0)

      for i in range( nports ):
        s.vals[i] = s.qs[i].deq.rdy
        s.arbiter.reqs[i] = s.qs[i].deq.rdy & s.out.rdy
        s.qs[i].deq.en    = s.arbiter.grants[i]

    #---------------------------------------------------------------------
    # Assign outputs
    #---------------------------------------------------------------------

    @s.update
    def output_logic():
      s.out.en  = reduce_or( s.vals ) & s.out.rdy
      s.out.msg = MsgType()

      for i in range( nports ):
        if s.arbiter.grants[i]:
          s.out.msg        = deepcopy(s.qs[i].deq.ret)
          s.out.msg.opaque = OpaqueType(i)

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    in_str = '{' + '|'.join(map(str,s.in_)) + '}'
    return "{} ({}) {}".format( in_str, s.arbiter.line_trace(), s.out )
