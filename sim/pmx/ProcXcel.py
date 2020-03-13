#=========================================================================
# ProcXcel
#=========================================================================
# No caches, just processor + accelerator

from pymtl3 import *
from pymtl3.stdlib.ifcs import SendIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs import mk_mem_msg, MemMasterIfcRTL

class ProcXcel( Component ):

  #-----------------------------------------------------------------------
  # constructor
  #-----------------------------------------------------------------------

  def construct( s, proc, xcel ):

    CacheReqType, CacheRespType = mk_mem_msg( 8, 32, 32 )
    MemReqType,   MemRespType   = mk_mem_msg( 8, 32, 128 )

    # interface to outside ProcMemXcel

    s.go        = InPort ()
    s.stats_en  = OutPort()

    s.proc = proc
    s.xcel = xcel

    # More interfaces that replicates the proc interface
    s.mngr2proc = s.proc.mngr2proc.__class__( Type=Bits32 )
    s.mngr2proc //= s.proc.mngr2proc

    s.proc2mngr = s.proc.proc2mngr.__class__( Type=Bits32 )
    s.proc2mngr //= s.proc.proc2mngr

    s.imem = s.proc.imem.__class__( CacheReqType, CacheRespType )
    s.imem //= s.proc.imem

    s.dmem = s.proc.dmem.__class__( CacheReqType, CacheRespType )
    s.dmem //= s.proc.dmem

    s.xmem = s.xcel.mem.__class__( CacheReqType, CacheRespType )
    s.xmem //= s.xcel.mem

    # connect signals

    s.proc.core_id //= 0

    s.stats_en  //= s.proc.stats_en

    # xcel

    s.xcel.xcel //= s.proc.xcel

    # mem


  def line_trace( s ):
    return s.proc.line_trace() + "|" + s.xcel.line_trace()


