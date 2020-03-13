#=========================================================================
# ProcMemXcel
#=========================================================================

from pymtl3             import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL, MemMinionIfcRTL, mk_mem_msg

from .Router  import Router
from .Funnel  import Funnel

class ProcMemXcel ( Component ):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def construct( s, proc, imem, dmem, xcel ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32 )
    MemReqType,   MemRespType   = mk_mem_msg( 8, 32, 128 )

    # interface to outside ProcMemXcel

    s.go        = InPort ()
    s.stats_en  = OutPort()
    s.mngr2proc = RecvIfcRTL( Bits32 )
    s.proc2mngr = SendIfcRTL( Bits32 )

    s.imem = MemMasterIfcRTL( MemReqType, MemRespType )
    s.dmem = MemMasterIfcRTL( MemReqType, MemRespType )

    s.proc      = proc
    s.xcel      = xcel
    s.icache    = imem
    s.dcache    = dmem

    s.funnel = Funnel( CacheReqType,  2 )(
      in_ = { 0: s.proc.dmem.req,
              1: s.xcel.mem.req  },
      out = s.dcache.cache.req,
    )

    s.router = Router( CacheRespType, 2 )(
      in_ = s.dcache.cache.resp,
      out = { 0: s.proc.dmem.resp,
              1: s.xcel.mem.resp }
    )

    # connect signals

    s.stats_en  //= s.proc.stats_en
    s.proc2mngr //= s.proc.proc2mngr
    s.mngr2proc //= s.proc.mngr2proc

    # proc

    s.proc.core_id //= 0
    s.xcel.xcel  //= s.proc.xcel
    s.icache.cache //= s.proc.imem

    # mem

    s.imem //= s.icache.mem
    s.dmem //= s.dcache.mem

  def line_trace( s ):

    return s.proc.line_trace() \
           + "[" + s.icache.line_trace() + "|"+ s.dcache.line_trace() + "]" \
           + s.xcel.line_trace()

