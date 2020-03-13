#=========================================================================
# ProcCtrlPRTL.py
#=========================================================================

from pymtl3 import *
from .XcelMsg import XCEL_TYPE_READ, XCEL_TYPE_WRITE

from .TinyRV2InstPRTL import *

class ProcCtrlPRTL( Component ):

  def construct( s ):

    #---------------------------------------------------------------------
    # Interface
    #---------------------------------------------------------------------

    # imem ports

    s.imemreq_en       = OutPort()
    s.imemreq_rdy      = InPort ()

    s.imemresp_en      = OutPort()
    s.imemresp_rdy     = InPort ()

    s.imemresp_drop    = OutPort()

    # dmem ports

    s.dmemreq_en       = OutPort()
    s.dmemreq_rdy      = InPort ()
    s.dmemreq_type     = OutPort(Bits4)

    s.dmemresp_en      = OutPort()
    s.dmemresp_rdy     = InPort ()

    # mngr ports

    s.mngr2proc_en     = OutPort()
    s.mngr2proc_rdy    = InPort ()

    s.proc2mngr_en     = OutPort()
    s.proc2mngr_rdy    = InPort ()

    # Control signals (ctrl->dpath)

    s.reg_en_F         = OutPort()
    s.pc_sel_F         = OutPort(Bits2)

    s.reg_en_D         = OutPort()
    s.op1_byp_sel_D    = OutPort(Bits2)
    s.op2_byp_sel_D    = OutPort(Bits2)
    s.op1_sel_D        = OutPort()
    s.op2_sel_D        = OutPort(Bits2)
    s.csrr_sel_D       = OutPort(Bits2)
    s.imm_type_D       = OutPort(Bits3)
    s.imul_req_en_D    = OutPort()
    s.imul_req_rdy_D   = InPort ()

    s.reg_en_X         = OutPort()
    s.alu_fn_X         = OutPort(Bits4)
    s.ex_result_sel_X  = OutPort(Bits2)
    s.imul_resp_en_X   = OutPort()
    s.imul_resp_rdy_X  = InPort ()

    s.reg_en_M         = OutPort()
    s.wb_result_sel_M  = OutPort(Bits2)

    s.reg_en_W         = OutPort()
    s.rf_waddr_W       = OutPort(Bits5)
    s.rf_wen_W         = OutPort()

    # Status signals (dpath->ctrl)

    s.inst_D           = InPort (Bits32)
    s.br_cond_eq_X     = InPort ()
    s.br_cond_lt_X     = InPort ()
    s.br_cond_ltu_X    = InPort ()

    # Output val_W for counting

    s.commit_inst      = OutPort()

    s.stats_en_wen_W   = OutPort()

    #-----------------------------------------------------------------------
    # Control unit logic
    #-----------------------------------------------------------------------
    # We follow this principle to organize code for each pipeline stage in
    # the control unit.  Register enable logics should always at the
    # beginning. It followed by pipeline registers. Then logic that is not
    # dependent on stall or squash signals. Then logic that is dependent on
    # stall or squash signals. At the end there should be signals meant to
    # be passed to the next stage in the pipeline.

    #---------------------------------------------------------------------
    # Valid, stall, and squash signals
    #---------------------------------------------------------------------
    # We use valid signal to indicate if the instruction is valid.  An
    # instruction can become invalid because of being squashed or
    # stalled. Notice that invalid instructions are microarchitectural
    # events, they are different from archtectural no-ops. We must be
    # careful about control signals that might change the state of the
    # processor. We should always AND outgoing control signals with valid
    # signal.

    s.val_F = Wire()
    s.val_D = Wire()
    s.val_X = Wire()
    s.val_M = Wire()
    s.val_W = Wire()

    # Managing the stall and squash signals is one of the most important,
    # yet also one of the most complex, aspects of designing a pipelined
    # processor. We will carefully use four signals per stage to manage
    # stalling and squashing: ostall_A, osquash_A, stall_A, and squash_A.

    # We denote the stall signals _originating_ from stage A as
    # ostall_A. For example, if stage A can stall due to a pipeline
    # harzard, then ostall_A would need to factor in the stalling
    # condition for this pipeline harzard.

    s.ostall_F = Wire()  # can ostall due to imemresp_val
    s.ostall_D = Wire()  # can ostall due to mngr2proc_val or other hazards
    s.ostall_X = Wire()  # can ostall due to dmemreq_rdy
    s.ostall_M = Wire()  # can ostall due to dmemresp_val
    s.ostall_W = Wire()  # can ostall due to proc2mngr_rdy

    # The stall_A signal should be used to indicate when stage A is indeed
    # stalling. stall_A will be a function of ostall_A and all the ostall
    # signals of stages in front of it in the pipeline.

    s.stall_F = Wire()
    s.stall_D = Wire()
    s.stall_X = Wire()
    s.stall_M = Wire()
    s.stall_W = Wire()

    # We denote the squash signals _originating_ from stage A as
    # osquash_A. For example, if stage A needs to squash the stages behind
    # A in the pipeline, then osquash_A would need to factor in this
    # squash condition.

    s.osquash_D = Wire() # can osquash due to unconditional jumps
    s.osquash_X = Wire() # can osquash due to taken branches

    # The squash_A signal should be used to indicate when stage A is being
    # squashed. squash_A will _not_ be a function of osquash_A, since
    # osquash_A means to squash the stages _behind_ A in the pipeline, but
    # not to squash A itself.

    s.squash_F = Wire()
    s.squash_D = Wire()

    # Shunning: IMPORTANT (FIXME?)
    # Signals related to accelerators. I centralize it to make it easier
    # to switch between Proc and the original ProcAlt

    # ports
    s.xcelreq_en   = OutPort()
    s.xcelreq_rdy  = InPort ()
    s.xcelreq_type = OutPort()

    s.xcelresp_en   = OutPort()
    s.xcelresp_rdy  = InPort()

    # signals
    s.xcelreq_type_D  = Wire()
    s.xcelreq_type_X  = Wire()

    s.xcelreq_D     = Wire()
    s.xcelreq_X     = Wire()
    s.xcelreq_M     = Wire()
    s.ostall_xcel_X = Wire()
    s.ostall_xcel_M = Wire()

    #---------------------------------------------------------------------
    # F stage
    #---------------------------------------------------------------------

    @s.update
    def comb_reg_en_F():
      s.reg_en_F = ~s.stall_F | s.squash_F

    @s.update_ff
    def reg_F():
      if s.reset:
        s.val_F <<= b1(0)
      elif s.reg_en_F:
        s.val_F <<= b1(1)

    # forward declaration of branch/jump logic

    s.pc_redirect_D = Wire()
    s.pc_redirect_X = Wire()

    # pc sel logic

    @s.update
    def comb_PC_sel_F():
      if   s.pc_redirect_X:

        if s.br_type_X == jalr:
          s.pc_sel_F = b2(3) # jalr target from ALU
        else:
          s.pc_sel_F = b2(1) # branch target

      elif s.pc_redirect_D:
        s.pc_sel_F = b2(2) # use jal target
      else:
        s.pc_sel_F = b2(0) # use pc+4

    s.next_val_F = Wire()

    @s.update
    def comb_F():
      # ostall due to imemresp

      s.ostall_F = s.val_F & ~s.imemresp_rdy

      # stall and squash in F stage

      s.stall_F  = s.val_F & ( s.ostall_F | s.ostall_D | s.ostall_X |
                               s.ostall_M | s.ostall_W )

      s.squash_F = s.val_F & ( s.osquash_D | s.osquash_X  )

      # imem req is special, it actually be sent out _before_ the F
      # stage, we need to send memreq everytime we are getting squashed
      # because we need to redirect the PC. We also need to factor in
      # reset. When we are resetting we shouldn't send out imem req.

      s.imemreq_en  =  ~s.reset & (~s.stall_F | s.squash_F) & s.imemreq_rdy
      s.imemresp_en =  ~s.stall_F | s.squash_F

      # We drop the mem response when we are getting squashed

      s.imemresp_drop = s.squash_F

      s.next_val_F    = s.val_F & ~s.stall_F & ~s.squash_F

    #---------------------------------------------------------------------
    # D stage
    #---------------------------------------------------------------------

    @s.update
    def comb_reg_en_D():
      s.reg_en_D = ~s.stall_D | s.squash_D

    @s.update_ff
    def reg_D():
      if s.reset:
        s.val_D <<= b1(0)
      elif s.reg_en_D:
        s.val_D <<= s.next_val_F

    # Decoder, translate 32-bit instructions to symbols

    s.inst_type_decoder_D = DecodeInstType()( in_ = s.inst_D )

    # Signals generated by control signal table

    s.inst_val_D       = Wire()
    s.br_type_D        = Wire( Bits3 )
    s.jal_D            = Wire()
    s.rs1_en_D         = Wire()
    s.rs2_en_D         = Wire()
    s.alu_fn_D         = Wire( Bits4 )
    s.dmemreq_type_D   = Wire( Bits2 )
    s.wb_result_sel_D  = Wire( Bits2 )
    s.rf_wen_pending_D = Wire()
    s.rf_waddr_sel_D   = Wire( Bits3 )
    s.csrw_D           = Wire()
    s.csrr_D           = Wire()
    s.proc2mngr_D      = Wire()
    s.mngr2proc_D      = Wire()
    s.stats_en_wen_D   = Wire()
    s.ex_result_sel_D  = Wire( Bits2 )
    s.mul_D            = Wire()

    # actual waddr, selected base on rf_waddr_sel_D

    s.rf_waddr_D = Wire( Bits5 )

    # Control signal table

    # Y/N parameters

    n = b1(0)
    y = b1(1)

    # Branch type
    # I add jalr here because it is also resolved at X stage

    br_x  = b3(0) # don't care
    br_na = b3(0) # N/A, not branch
    br_ne = b3(1) # branch not equal
    br_lt = b3(2) # branch less than
    br_lu = b3(3) # branch less than, unsigned
    br_eq = b3(4) # branch equal
    br_ge = b3(5) # branch greater than or equal to
    br_gu = b3(6) # branch greater than or equal to, unsigned
    jalr  = b3(7) # branch greater than or equal to, unsigned

    # Op1 mux select

    am_x  = b1(0) # don't care
    am_rf = b1(0) # use data from RF
    am_pc = b1(1) # use PC

    # Op2 mux select

    bm_x   = b2(0) # don't care
    bm_rf  = b2(0) # use data from RF
    bm_imm = b2(1) # use imm
    bm_csr = b2(2) # use mngr2proc/numcores/coreid based on csrnum

    # IMM type

    imm_x = b3(0) # don't care
    imm_i = b3(0) # I-imm
    imm_s = b3(1) # S-imm
    imm_b = b3(2) # B-imm
    imm_u = b3(3) # U-imm
    imm_j = b3(4) # J-imm

    # ALU func

    alu_x   = b4(0)
    alu_add = b4(0)
    alu_sub = b4(1)
    alu_sll = b4(2)
    alu_or  = b4(3)
    alu_lt  = b4(4)
    alu_ltu = b4(5)
    alu_and = b4(6)
    alu_xor = b4(7)
    alu_srl = b4(9)
    alu_sra = b4(10)
    alu_cp0 = b4(11) # copy in0
    alu_cp1 = b4(12) # copy in1
    alu_adz = b4(13) # special case for JALR

    # Memory request type

    nr = b2(0)
    ld = b2(1)
    st = b2(2)

    # X stage result mux select

    xm_x = b2(0) # don't care
    xm_a = b2(0) # Arithmetic
    xm_m = b2(1) # Multiplier
    xm_p = b2(2) # Pc+4

    # Write-back mux select

    wm_x = b2(0)
    wm_a = b2(0)
    wm_m = b2(1)
    wm_c = b2(2) # xCel

    # control signal table

    # control signal table
    # csr: csrr, csrw
    # rr: add, sub, mul, and, or, xor, slt, sltu, sra, srl, sll
    # rimm: addi, andi, ori, xori, slti, sltiu, srai, srli, slli, lui, auipc
    # mem: lw, sw
    # jump: jal, jalr
    # branch: beq, bne, blt, bge, bltu, bgeu

    s.cs = Wire(Bits27)

    @s.update
    def comb_control_table_D():
      inst = s.inst_type_decoder_D.out
      #                                     br    jal op1   rs1 imm    op2    rs2 alu      dmm xres  wbmux rf      cs cs
      #                                 val type   D  muxsel en type   muxsel  en fn       typ sel   sel   wen mul rr rw
      if   inst == NOP  : s.cs = concat( y, br_na, n, am_x,  n, imm_x, bm_x,   n, alu_x,   nr, xm_x, wm_a, n,  n,  n, n )
      # xcel/csrr/csrw
      elif inst == CSRRX: s.cs = concat( y, br_na, n, am_x,  n, imm_i, bm_imm, n, alu_cp1, nr, xm_a, wm_c, y,  n,  y, n )
      elif inst == CSRR : s.cs = concat( y, br_na, n, am_x,  n, imm_i, bm_csr, n, alu_cp1, nr, xm_a, wm_a, y,  n,  y, n )
      elif inst == CSRW : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_cp0, nr, xm_a, wm_a, n,  n,  n, y )
      # reg-reg
      elif inst == ADD  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_add, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SUB  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_sub, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == MUL  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_x  , nr, xm_m, wm_a, y,  y,  n, n )
      elif inst == AND  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_and, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == OR   : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_or , nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == XOR  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_xor, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLT  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_lt , nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLTU : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_ltu, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SRA  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_sra, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SRL  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_srl, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLL  : s.cs = concat( y, br_na, n, am_rf, y, imm_x, bm_rf,  y, alu_sll, nr, xm_a, wm_a, y,  n,  n, n )
      # reg-imm
      elif inst == ADDI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_add, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == ANDI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_and, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == ORI  : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_or , nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == XORI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_xor, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLTI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_lt , nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLTIU: s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_ltu, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SRAI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_sra, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SRLI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_srl, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == SLLI : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_sll, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == LUI  : s.cs = concat( y, br_na, n, am_x,  n, imm_u, bm_imm, n, alu_cp1, nr, xm_a, wm_a, y,  n,  n, n )
      elif inst == AUIPC: s.cs = concat( y, br_na, n, am_pc, n, imm_u, bm_imm, n, alu_add, nr, xm_a, wm_a, y,  n,  n, n )
      # mem
      elif inst == LW   : s.cs = concat( y, br_na, n, am_rf, y, imm_i, bm_imm, n, alu_add, ld, xm_a, wm_m, y,  n,  n, n )
      elif inst == SW   : s.cs = concat( y, br_na, n, am_rf, y, imm_s, bm_imm, y, alu_add, st, xm_a, wm_m, n,  n,  n, n )
      # branch
      elif inst == BNE  : s.cs = concat( y, br_ne, n, am_rf, y, imm_b, bm_rf,  y, alu_x,   nr, xm_a, wm_x, n,  n,  n, n )
      elif inst == BEQ  : s.cs = concat( y, br_eq, n, am_rf, y, imm_b, bm_rf,  y, alu_x,   nr, xm_a, wm_x, n,  n,  n, n )
      elif inst == BLT  : s.cs = concat( y, br_lt, n, am_rf, y, imm_b, bm_rf,  y, alu_lt,  nr, xm_a, wm_x, n,  n,  n, n )
      elif inst == BLTU : s.cs = concat( y, br_lu, n, am_rf, y, imm_b, bm_rf,  y, alu_ltu, nr, xm_a, wm_x, n,  n,  n, n )
      elif inst == BGE  : s.cs = concat( y, br_ge, n, am_rf, y, imm_b, bm_rf,  y, alu_lt,  nr, xm_a, wm_x, n,  n,  n, n )
      elif inst == BGEU : s.cs = concat( y, br_gu, n, am_rf, y, imm_b, bm_rf,  y, alu_ltu, nr, xm_a, wm_x, n,  n,  n, n )
      # jump
      elif inst == JAL  : s.cs = concat( y, br_na, y, am_x,  n, imm_j, bm_x,   n, alu_x,   nr, xm_p, wm_a, y,  n,  n, n )
      elif inst == JALR : s.cs = concat( y, jalr , n, am_rf, y, imm_i, bm_imm, n, alu_adz, nr, xm_p, wm_a, y,  n,  n, n )
      else:               s.cs = concat( n, br_x,  n, am_x,  n, imm_x, bm_x,   n, alu_x,   nr, xm_x, wm_x, n,  n,  n, n )

      s.inst_val_D       = s.cs[26:27]
      s.br_type_D        = s.cs[23:26]
      s.jal_D            = s.cs[22:23]
      s.op1_sel_D        = s.cs[21:22]
      s.rs1_en_D         = s.cs[20:21]
      s.imm_type_D       = s.cs[17:20]
      s.op2_sel_D        = s.cs[15:17]
      s.rs2_en_D         = s.cs[14:15]
      s.alu_fn_D         = s.cs[10:14]
      s.dmemreq_type_D   = s.cs[8:10]
      s.ex_result_sel_D  = s.cs[6:8]
      s.wb_result_sel_D  = s.cs[4:6]
      s.rf_wen_pending_D = s.cs[3:4]
      s.mul_D            = s.cs[2:3]
      s.csrr_D           = s.cs[1:2]
      s.csrw_D           = s.cs[0:1]

      # setting the actual write address

      s.rf_waddr_D = s.inst_D[RD]

      # csrr/csrw logic

      s.csrr_sel_D     = b2(0)
      s.xcelreq_type_D = b1(0)
      s.xcelreq_D      = b1(0)
      s.mngr2proc_D    = b1(0)
      s.proc2mngr_D    = b1(0)
      s.stats_en_wen_D = b1(0)

      if s.csrr_D:
        if   s.inst_D[CSRNUM] == CSR_NUMCORES:
          s.csrr_sel_D = b2(1)
        elif s.inst_D[CSRNUM] == CSR_COREID:
          s.csrr_sel_D = b2(2)
        elif s.inst_D[CSRNUM] == CSR_MNGR2PROC:
          s.mngr2proc_D = b1(1)

        else:
          # FIXME
          s.xcelreq_type_D = XCEL_TYPE_READ
          s.xcelreq_D = b1(1)

      if s.csrw_D:
        if   s.inst_D[CSRNUM] == CSR_PROC2MNGR:
          s.proc2mngr_D = b1(1)
        elif s.inst_D[CSRNUM] == CSR_STATS_EN:
          s.stats_en_wen_D = b1(1)

        # In this case we handle accelerator registers requests.
        else:
          # FIXME
          s.xcelreq_type_D = XCEL_TYPE_WRITE
          s.xcelreq_D = b1(1)

    # Jump logic

    @s.update
    def comb_jump_D():
      s.pc_redirect_D = s.val_D & s.jal_D

    # forward wire declaration for hazard checking

    s.rf_waddr_X = Wire( Bits5 )
    s.rf_waddr_M = Wire( Bits5 )

    # bypassing logic

    byp_d = b2(0)
    byp_x = b2(1)
    byp_m = b2(2)
    byp_w = b2(3)

    @s.update
    def comb_bypass_D():

      s.op1_byp_sel_D = byp_d

      if s.rs1_en_D:

        if   s.val_X & ( s.inst_D[ RS1 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
                     & s.rf_wen_pending_X:    s.op1_byp_sel_D = byp_x
        elif s.val_M & ( s.inst_D[ RS1 ] == s.rf_waddr_M ) & ( s.rf_waddr_M != b5(0) ) \
                     & s.rf_wen_pending_M:    s.op1_byp_sel_D = byp_m
        elif s.val_W & ( s.inst_D[ RS1 ] == s.rf_waddr_W ) & ( s.rf_waddr_W != b5(0) ) \
                     & s.rf_wen_pending_W:    s.op1_byp_sel_D = byp_w

      s.op2_byp_sel_D = byp_d

      if s.rs2_en_D:

        if   s.val_X & ( s.inst_D[ RS2 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
                     & s.rf_wen_pending_X:    s.op2_byp_sel_D = byp_x
        elif s.val_M & ( s.inst_D[ RS2 ] == s.rf_waddr_M ) & ( s.rf_waddr_M != b5(0) ) \
                     & s.rf_wen_pending_M:    s.op2_byp_sel_D = byp_m
        elif s.val_W & ( s.inst_D[ RS2 ] == s.rf_waddr_W ) & ( s.rf_waddr_W != b5(0) ) \
                     & s.rf_wen_pending_W:    s.op2_byp_sel_D = byp_w

    # hazards checking logic
    # Although bypassing is added, we might still have RAW when there is
    # lw instruction in X stage

    # We also need to add a stall for CSRRX since the value will not be
    # returned from the accelerator until the M stage.

    s.ostall_ld_X_rs1_D    = Wire()
    s.ostall_ld_X_rs2_D    = Wire()
    s.ostall_csrrx_X_rs1_D = Wire()
    s.ostall_csrrx_X_rs2_D = Wire()

    s.ostall_hazard_D      = Wire()

    @s.update
    def comb_hazard_D():

      s.ostall_ld_X_rs1_D = s.rs1_en_D & s.val_X & s.rf_wen_pending_X \
        & ( s.inst_D[ RS1 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
        & ( s.dmemreq_type_X == ld )

      s.ostall_ld_X_rs2_D = s.rs2_en_D & s.val_X & s.rf_wen_pending_X \
        & ( s.inst_D[ RS2 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
        & ( s.dmemreq_type_X == ld )

      s.ostall_csrrx_X_rs1_D = s.rs1_en_D & s.val_X & s.rf_wen_pending_X \
        & ( s.inst_D[ RS1 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
        & s.xcelreq_X & (s.xcelreq_type_X == XCEL_TYPE_READ)

      s.ostall_csrrx_X_rs2_D = s.rs2_en_D & s.val_X & s.rf_wen_pending_X \
        & ( s.inst_D[ RS2 ] == s.rf_waddr_X ) & ( s.rf_waddr_X != b5(0) ) \
        & s.xcelreq_X & (s.xcelreq_type_X == XCEL_TYPE_READ)

      s.ostall_hazard_D = s.ostall_ld_X_rs1_D    | s.ostall_ld_X_rs2_D \
                        | s.ostall_csrrx_X_rs1_D | s.ostall_csrrx_X_rs2_D

    # ostall due to mngr2proc

    s.ostall_mngr_D = Wire()

    # ostall due to imul

    s.ostall_imul_D = Wire()

    s.next_val_D = Wire()

    @s.update
    def comb_D():

      # ostall due to mngr2proc
      s.ostall_mngr_D = s.mngr2proc_D & ~s.mngr2proc_rdy

      # ostall due to imul
      s.ostall_imul_D = s.mul_D & ~s.imul_req_rdy_D

      # put together all ostall conditions

      s.ostall_D = s.val_D & ( s.ostall_mngr_D | s.ostall_hazard_D | s.ostall_imul_D )

      # stall in D stage

      s.stall_D = s.val_D & ( s.ostall_D | s.ostall_X |
                              s.ostall_M | s.ostall_W )

      # osquash due to jumps
      # Note that, in the same combinational block, we have to calculate
      # s.stall_D first then use it in osquash_D. Several people have
      # stuck here just because they calculate osquash_D before stall_D!

      s.osquash_D = s.val_D & ~s.stall_D & s.pc_redirect_D

      # squash in D stage

      s.squash_D = s.val_D & s.osquash_X

      # mngr2proc port

      s.mngr2proc_en = s.val_D & ~s.stall_D & ~s.squash_D & s.mngr2proc_D

      # imul request valid signal

      s.imul_req_en_D = s.val_D & ~s.stall_D & ~s.squash_D & s.mul_D

      # next valid bit

      s.next_val_D = s.val_D & ~s.stall_D & ~s.squash_D

    #---------------------------------------------------------------------
    # X stage
    #---------------------------------------------------------------------

    @s.update
    def comb_reg_en_X():
      s.reg_en_X = ~s.stall_X

    s.inst_type_X      = Wire( Bits8 )
    s.rf_wen_pending_X = Wire()
    s.proc2mngr_X      = Wire()
    s.dmemreq_type_X   = Wire( Bits2 )
    s.wb_result_sel_X  = Wire( Bits2 )
    s.stats_en_wen_X   = Wire()
    s.br_type_X        = Wire( Bits3 )
    s.mul_X            = Wire()

    @s.update_ff
    def reg_X():
      if s.reset:
        s.val_X            <<= b1(0)
        s.stats_en_wen_X   <<= b1(0)
      elif s.reg_en_X:
        s.val_X            <<= s.next_val_D
        s.rf_wen_pending_X <<= s.rf_wen_pending_D
        s.inst_type_X      <<= s.inst_type_decoder_D.out
        s.alu_fn_X         <<= s.alu_fn_D
        s.rf_waddr_X       <<= s.rf_waddr_D
        s.proc2mngr_X      <<= s.proc2mngr_D
        s.dmemreq_type_X   <<= s.dmemreq_type_D
        s.wb_result_sel_X  <<= s.wb_result_sel_D
        s.stats_en_wen_X   <<= s.stats_en_wen_D
        s.br_type_X        <<= s.br_type_D
        s.mul_X            <<= s.mul_D
        s.ex_result_sel_X  <<= s.ex_result_sel_D
        s.xcelreq_X        <<= s.xcelreq_D
        s.xcelreq_type_X   <<= s.xcelreq_type_D

    # Branch logic

    @s.update
    def comb_br_X():
      s.pc_redirect_X = b1(0)

      if s.val_X:
        if   s.br_type_X == br_eq: s.pc_redirect_X = s.br_cond_eq_X
        elif s.br_type_X == br_lt: s.pc_redirect_X = s.br_cond_lt_X
        elif s.br_type_X == br_lu: s.pc_redirect_X = s.br_cond_ltu_X
        elif s.br_type_X == br_ne: s.pc_redirect_X = ~s.br_cond_eq_X
        elif s.br_type_X == br_ge: s.pc_redirect_X = ~s.br_cond_lt_X
        elif s.br_type_X == br_gu: s.pc_redirect_X = ~s.br_cond_ltu_X
        elif s.br_type_X == jalr : s.pc_redirect_X = b1(1)

    s.ostall_dmem_X = Wire()
    s.ostall_imul_X = Wire()
    s.ostall_xcel_X = Wire()
    s.next_val_X    = Wire()

    @s.update
    def comb_X():

      # ostall due to xcelreq
      s.ostall_xcel_X = s.xcelreq_X & ~s.xcelreq_rdy

      # ostall due to dmemreq
      s.ostall_dmem_X = ( s.dmemreq_type_X != nr ) & ~s.dmemreq_rdy

      # ostall due to imul
      s.ostall_imul_X = s.mul_X & ~s.imul_resp_rdy_X

      s.ostall_X = s.val_X & ( s.ostall_dmem_X | s.ostall_imul_X | s.ostall_xcel_X )

      # stall in X stage

      s.stall_X  = s.val_X & ( s.ostall_X | s.ostall_M | s.ostall_W )

      # osquash due to taken branches
      # Note that, in the same combinational block, we have to calculate
      # s.stall_X first then use it in osquash_X. Several people have
      # stuck here just because they calculate osquash_X before stall_X!

      s.osquash_X   = s.val_X & ~s.stall_X & s.pc_redirect_X

      # send dmemreq if not stalling

      s.dmemreq_en = s.val_X & ~s.stall_X & ( s.dmemreq_type_X != nr )

      # send xcelreq if not stalling

      s.xcelreq_en = s.val_X & ~s.stall_X & s.xcelreq_X
      s.xcelreq_type = s.xcelreq_type_X

      s.dmemreq_type = b4(s.dmemreq_type_X == st)  # 0-load/DC, 1-store

      # imul resp en signal

      s.imul_resp_en_X = s.val_X & ~s.stall_X & s.mul_X

      # next valid bit

      s.next_val_X = s.val_X & ~s.stall_X

    #---------------------------------------------------------------------
    # M stage
    #---------------------------------------------------------------------

    @s.update
    def comb_reg_en_M():
      s.reg_en_M = ~s.stall_M

    s.inst_type_M      = Wire(Bits8)
    s.rf_wen_pending_M = Wire()
    s.proc2mngr_M      = Wire()
    s.dmemreq_type_M   = Wire(Bits2)
    s.stats_en_wen_M   = Wire()

    @s.update_ff
    def reg_M():
      if s.reset:
        s.val_M            <<= b1(0)
        s.stats_en_wen_M   <<= b1(0)
      elif s.reg_en_M:
        s.val_M            <<= s.next_val_X
        s.rf_wen_pending_M <<= s.rf_wen_pending_X
        s.inst_type_M      <<= s.inst_type_X
        s.rf_waddr_M       <<= s.rf_waddr_X
        s.proc2mngr_M      <<= s.proc2mngr_X
        s.dmemreq_type_M   <<= s.dmemreq_type_X
        s.wb_result_sel_M  <<= s.wb_result_sel_X
        s.stats_en_wen_M   <<= s.stats_en_wen_X
        # xcel
        s.xcelreq_M        <<= s.xcelreq_X

    s.ostall_dmem_M = Wire()
    s.next_val_M    = Wire()

    @s.update
    def comb_M():

      # ostall due to xcel resp
      s.ostall_xcel_M = s.xcelreq_M & ~s.xcelresp_rdy

      # ostall due to dmem resp
      s.ostall_dmem_M = ( s.dmemreq_type_M != nr ) & ~s.dmemresp_rdy

      s.ostall_M     = s.val_M & ( s.ostall_dmem_M | s.ostall_xcel_M )

      # stall in M stage

      s.stall_M      = s.val_M & ( s.ostall_M | s.ostall_W )

      # set dmemresp en if not stalling

      s.dmemresp_en = s.val_M & ~s.stall_M & ( s.dmemreq_type_M != nr )

      # set xcelresp en if not stalling

      s.xcelresp_en = s.val_M & ~s.stall_M & s.xcelreq_M

      # next valid bit

      s.next_val_M   = s.val_M & ~s.stall_M

    #---------------------------------------------------------------------
    # W stage
    #---------------------------------------------------------------------

    @s.update
    def comb_reg_en_W():
      s.reg_en_W = ~s.stall_W

    s.inst_type_W            = Wire(Bits8)
    s.proc2mngr_W            = Wire()
    s.rf_wen_pending_W       = Wire()
    s.stats_en_wen_pending_W = Wire()

    @s.update_ff
    def reg_W():

      if s.reset:
        s.val_W                  <<= b1(0)
        s.stats_en_wen_pending_W <<= b1(0)
      elif s.reg_en_W:
        s.val_W                  <<= s.next_val_M
        s.rf_wen_pending_W       <<= s.rf_wen_pending_M
        s.inst_type_W            <<= s.inst_type_M
        s.rf_waddr_W             <<= s.rf_waddr_M
        s.proc2mngr_W            <<= s.proc2mngr_M
        s.stats_en_wen_pending_W <<= s.stats_en_wen_M

    @s.update
    def comb_W():
      # set RF write enable if valid

      s.rf_wen_W       = s.val_W & s.rf_wen_pending_W
      s.stats_en_wen_W = s.val_W & s.stats_en_wen_pending_W

      # ostall due to proc2mngr

      s.ostall_W      = s.val_W & s.proc2mngr_W & ~s.proc2mngr_rdy

      # stall in W stage

      s.stall_W       = s.val_W & s.ostall_W

      # set proc2mngr en if not stalling

      s.proc2mngr_en  = s.val_W & ~s.stall_W & s.proc2mngr_W

      s.commit_inst   = s.val_W & ~s.stall_W
