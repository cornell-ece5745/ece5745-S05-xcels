#=========================================================================
# ProcPRTL.py
#=========================================================================
# ProcAlt + xcelreq/resp + custom0

from pymtl3             import *
from pymtl3.stdlib.ifcs import RecvIfcRTL, SendIfcRTL
from pymtl3.stdlib.ifcs.mem_ifcs import MemMasterIfcRTL
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMasterIfcRTL
from pymtl3.stdlib.ifcs import mk_mem_msg
from pymtl3.stdlib.rtl  import BypassQueueRTL
from .tinyrv2_encoding  import disassemble_inst
from .TinyRV2InstPRTL   import inst_dict

from .ProcDpathPRTL    import ProcDpathPRTL
from .ProcCtrlPRTL     import ProcCtrlPRTL
from .DropUnitPRTL     import DropUnitPRTL

from .XcelMsg import XcelReqMsg, XcelRespMsg

class ProcPRTL( Component ):

  def construct( s, num_cores=1 ):

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

    #---------------------------------------------------------------------
    # Structural composition
    #---------------------------------------------------------------------

    # Bypass queues

    s.imemreq_q   = BypassQueueRTL( MemReqMsg, 2 )

    s.imemreq_q.deq.ret //= s.imem.req.msg

    @s.update
    def send_imemreq():
      both_rdy = s.imem.req.rdy & s.imemreq_q.deq.rdy
      s.imemreq_q.deq.en = both_rdy
      s.imem.req.en = both_rdy

    # We have to turn input receive interface into get interface

    s.imemresp_q  = BypassQueueRTL( MemRespMsg, 1 )( enq = s.imem.resp )
    s.dmemresp_q  = BypassQueueRTL( MemRespMsg, 1 )( enq = s.dmem.resp )
    s.mngr2proc_q = BypassQueueRTL( Bits32, 1 )( enq = s.mngr2proc )
    s.xcelresp_q  = BypassQueueRTL( XcelRespMsg, 1 )( enq = s.xcel.resp )

    # imem drop unit

    s.imemresp_drop_unit = DropUnitPRTL( MemRespMsg )(
      in_  = s.imemresp_q.deq,
    )

    # control logic

    s.ctrl  = ProcCtrlPRTL()(
      # imem port
      imemresp_drop = s.imemresp_drop_unit.drop,
      imemreq_en    = s.imemreq_q.enq.en,
      imemreq_rdy   = s.imemreq_q.enq.rdy,
      imemresp_en   = s.imemresp_drop_unit.out.en,
      imemresp_rdy  = s.imemresp_drop_unit.out.rdy,

      # dmem port
      dmemreq_en    = s.dmem.req.en,
      dmemreq_rdy   = s.dmem.req.rdy,
      dmemresp_en   = s.dmemresp_q.deq.en,
      dmemresp_rdy  = s.dmemresp_q.deq.rdy,

      # xcel port
      xcelreq_en    = s.xcel.req.en,
      xcelreq_rdy   = s.xcel.req.rdy,
      xcelresp_en   = s.xcelresp_q.deq.en,
      xcelresp_rdy  = s.xcelresp_q.deq.rdy,

      # proc2mngr and mngr2proc
      proc2mngr_en  = s.proc2mngr.en,
      proc2mngr_rdy = s.proc2mngr.rdy,
      mngr2proc_en  = s.mngr2proc_q.deq.en,
      mngr2proc_rdy = s.mngr2proc_q.deq.rdy,

      # commit inst for counting
      commit_inst = s.commit_inst,
    )

    # data path

    s.dpath = ProcDpathPRTL( num_cores )(
      core_id  = s.core_id,
      stats_en = s.stats_en,

      # imem ports
      imemreq_msg   = s.imemreq_q.enq.msg,
      imemresp_msg  = s.imemresp_drop_unit.out.ret,

      # dmem ports
      dmemresp_msg  = s.dmemresp_q.deq.ret,

      # xcel ports
      xcelresp_msg  = s.xcelresp_q.deq.ret,

      # mngr
      mngr2proc_data = s.mngr2proc_q.deq.ret,
      proc2mngr_data = s.proc2mngr.msg,
    )

    # Connect parameters

    s.xcel.req.msg //= lambda: XcelReqMsg( s.ctrl.xcelreq_type, s.dpath.xcelreq_addr, s.dpath.xcelreq_data )

    s.dmem.req.msg //= lambda: MemReqMsg( s.ctrl.dmemreq_type, b8(0), s.dpath.dmemreq_addr, b2(0), s.dpath.dmemreq_data )
    # Ctrl <-> Dpath

    s.ctrl.reg_en_F        //= s.dpath.reg_en_F
    s.ctrl.pc_sel_F        //= s.dpath.pc_sel_F

    s.ctrl.reg_en_D        //= s.dpath.reg_en_D
    s.ctrl.csrr_sel_D      //= s.dpath.csrr_sel_D
    s.ctrl.op1_byp_sel_D   //= s.dpath.op1_byp_sel_D
    s.ctrl.op2_byp_sel_D   //= s.dpath.op2_byp_sel_D
    s.ctrl.op1_sel_D       //= s.dpath.op1_sel_D
    s.ctrl.op2_sel_D       //= s.dpath.op2_sel_D
    s.ctrl.imm_type_D      //= s.dpath.imm_type_D
    s.ctrl.imul_req_en_D   //= s.dpath.imul_req_en_D
    s.ctrl.imul_req_rdy_D  //= s.dpath.imul_req_rdy_D

    s.ctrl.reg_en_X        //= s.dpath.reg_en_X
    s.ctrl.alu_fn_X        //= s.dpath.alu_fn_X
    s.ctrl.ex_result_sel_X //= s.dpath.ex_result_sel_X
    s.ctrl.imul_resp_en_X  //= s.dpath.imul_resp_en_X
    s.ctrl.imul_resp_rdy_X //= s.dpath.imul_resp_rdy_X

    s.ctrl.reg_en_M        //= s.dpath.reg_en_M
    s.ctrl.wb_result_sel_M //= s.dpath.wb_result_sel_M

    s.ctrl.reg_en_W        //= s.dpath.reg_en_W
    s.ctrl.rf_waddr_W      //= s.dpath.rf_waddr_W
    s.ctrl.rf_wen_W        //= s.dpath.rf_wen_W
    s.ctrl.stats_en_wen_W  //= s.dpath.stats_en_wen_W

    s.dpath.inst_D         //= s.ctrl.inst_D
    s.dpath.br_cond_eq_X   //= s.ctrl.br_cond_eq_X
    s.dpath.br_cond_lt_X   //= s.ctrl.br_cond_lt_X
    s.dpath.br_cond_ltu_X  //= s.ctrl.br_cond_ltu_X

  #-----------------------------------------------------------------------
  # Line tracing
  #-----------------------------------------------------------------------

  def line_trace( s ):
    # F stage
    if not s.ctrl.val_F:  F_str = "{:<8s}".format( ' ' )
    elif s.ctrl.squash_F: F_str = "{:<8s}".format( '~' )
    elif s.ctrl.stall_F:  F_str = "{:<8s}".format( '#' )
    else:                 F_str = "{:08x}".format( s.dpath.pc_reg_F.out.uint() )

    # D stage
    if not s.ctrl.val_D:  D_str = "{:<23s}".format( ' ' )
    elif s.ctrl.squash_D: D_str = "{:<23s}".format( '~' )
    elif s.ctrl.stall_D:  D_str = "{:<23s}".format( '#' )
    else:                 D_str = "{:<23s}".format( disassemble_inst(s.ctrl.inst_D) )

    # X stage
    if not s.ctrl.val_X:  X_str = "{:<5s}".format( ' ' )
    elif s.ctrl.stall_X:  X_str = "{:<5s}".format( '#' )
    else:                 X_str = "{:<5s}".format( inst_dict[s.ctrl.inst_type_X] )

    # M stage
    if not s.ctrl.val_M:  M_str = "{:<5s}".format( ' ' )
    elif s.ctrl.stall_M:  M_str = "{:<5s}".format( '#' )
    else:                 M_str = "{:<5s}".format( inst_dict[s.ctrl.inst_type_M] )

    # W stage
    if not s.ctrl.val_W:  W_str = "{:<5s}".format( ' ' )
    elif s.ctrl.stall_W:  W_str = "{:<5s}".format( '#' )
    else:                 W_str = "{:<5s}".format( inst_dict[s.ctrl.inst_type_W] )

    return "{}|{}|{}|{}|{}".format( F_str, D_str, X_str, M_str, W_str)
