#=========================================================================
# Router.py
#=========================================================================
# The Router model is a val-rdy based arbiter model that routes an incoming
# val-rdy message to an output val-rdy port bundle, given a number of
# outputs. NOTE: The message is assumed to have an opaque field and the
# router simply inspects the opaque field to route a message.

from pymtl3      import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.rtl  import BypassQueueRTL

#-------------------------------------------------------------------------
# Router
#-------------------------------------------------------------------------

class Router( Component ):

  def construct( s, MsgType, nports ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    s.in_ = RecvIfcRTL( MsgType )
    s.out = [ SendIfcRTL( MsgType ) for _ in range(nports) ]

    s.q = BypassQueueRTL( MsgType, 1 )( enq = s.in_ )

    s.out_id = Wire( mk_bits(clog2(nports)) )
    s.out_id //= s.q.deq.ret.opaque[0:clog2(nports)]

    #---------------------------------------------------------------------
    # Assign outputs
    #---------------------------------------------------------------------
    # Notice that we inspect the opaque field in the incoming message to
    # assign the correct OutValRdyBundle.

    @s.update
    def up_router_logic():
      s.q.deq.en = b1(0)
      for i in range( nports ):
        s.out[i].en  = b1(0)
        s.out[i].msg = MsgType()

      if s.out[ s.out_id ].rdy and s.q.deq.rdy:
        s.q.deq.en = b1(1)
        s.out[ s.out_id ].en  = b1(1)
        s.out[ s.out_id ].msg = s.q.deq.ret

  #-----------------------------------------------------------------------
  # line_trace
  #-----------------------------------------------------------------------

  def line_trace( s ):
    out_str = '{' + '|'.join(map(str,s.out)) + '}'
    return f"{s.in_} () {out_str}"
