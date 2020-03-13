//=========================================================================
// 5-Stage Simple Pipelined Processor
//=========================================================================

`ifndef PROC_PROC_V
`define PROC_PROC_V

`include "vc/mem-msgs.v"
`include "vc/queues.v"
`include "vc/trace.v"

`include "proc/TinyRV2InstVRTL.v"
`include "proc/ProcCtrlVRTL.v"
`include "proc/ProcDpathVRTL.v"
`include "proc/DropUnitVRTL.v"
`include "proc/XcelMsg.v"

module proc_ProcVRTL
#(
  parameter p_num_cores = 1
)
(
  input  logic         clk,
  input  logic         reset,

  // core_id is an input port rather than a parameter so that
  // the module only needs to be compiled once. If it were a parameter,
  // each core would be compiled separately.
  input  logic [31:0]  core_id,

  // From mngr streaming port

  input  logic [31:0]  mngr2proc_msg,
  input  logic         mngr2proc_en,
  output logic         mngr2proc_rdy,

  // To mngr streaming port

  output logic [31:0]  proc2mngr_msg,
  output logic         proc2mngr_en,
  input  logic         proc2mngr_rdy,

  // Xcelresp port

  input  XcelRespMsg     xcelresp_msg,
  input  logic           xcelresp_en,
  output logic           xcelresp_rdy,

  // Xcelreq port

  output XcelReqMsg      xcelreq_msg,
  output logic           xcelreq_en,
  input  logic           xcelreq_rdy,

  // Instruction Memory Request Port

  output mem_req_4B_t  imemreq_msg,
  output logic         imemreq_en,
  input  logic         imemreq_rdy,

  // Instruction Memory Response Port

  input  mem_resp_4B_t imemresp_msg,
  input  logic         imemresp_en,
  output logic         imemresp_rdy,

  // Data Memory Request Port

  output mem_req_4B_t  dmemreq_msg,
  output logic         dmemreq_en,
  input  logic         dmemreq_rdy,

  // Data Memory Response Port

  input  mem_resp_4B_t dmemresp_msg,
  input  logic         dmemresp_en,
  output logic         dmemresp_rdy,

  // stats output

  output logic         commit_inst,

  output logic         stats_en

);

  //----------------------------------------------------------------------
  // data mem req/resp
  //----------------------------------------------------------------------

  // imemreq before pack

  logic [31:0] imemreq_msg_addr;

  // imemreq_enq signals after pack before bypass queue

  mem_req_4B_t imemreq_enq_msg;
  logic        imemreq_enq_en;
  logic        imemreq_enq_rdy;

  // imemreq_deq signals

  mem_req_4B_t imemreq_deq_ret;
  logic        imemreq_deq_en;
  logic        imemreq_deq_rdy;

  // imemresp after bypass queue

  mem_resp_4B_t imemresp_deq_ret;
  logic         imemresp_deq_en;
  logic         imemresp_deq_rdy;

  // dmemresp after bypass queue

  mem_resp_4B_t dmemresp_deq_ret;
  logic         dmemresp_deq_en;
  logic         dmemresp_deq_rdy;

  // mngr2proc signals after bypass queue

  logic [31:0] mngr2proc_deq_ret;
  logic        mngr2proc_deq_en;
  logic        mngr2proc_deq_rdy;

  // imemresp signals after the drop unit

  mem_resp_4B_t imemresp_msg_drop;
  logic         imemresp_en_drop;
  logic         imemresp_rdy_drop;

  // imemresp drop signal

  logic        imemresp_drop;

  // accelerator specific

  // xcelresp signals after bypass queue

  XcelRespMsg  xcelresp_deq_ret;
  logic        xcelresp_deq_en;
  logic        xcelresp_deq_rdy;

//''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''
// Connect components
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  // control signals (ctrl->dpath)

  logic        reg_en_F;
  logic [1:0]  pc_sel_F;

  logic        reg_en_D;
  logic [1:0]  op1_byp_sel_D;
  logic [1:0]  op2_byp_sel_D;
  logic        op1_sel_D;
  logic [1:0]  op2_sel_D;
  logic [1:0]  csrr_sel_D;
  logic [2:0]  imm_type_D;
  logic        imul_req_en_D;

  logic        reg_en_X;
  logic [3:0]  alu_fn_X;
  logic [1:0]  ex_result_sel_X;
  logic        imul_resp_en_X;

  logic        reg_en_M;
  logic [1:0]  wb_result_sel_M;

  logic        reg_en_W;
  logic [4:0]  rf_waddr_W;
  logic        rf_wen_W;
  logic        stats_en_wen_W;

  // status signals (dpath->ctrl)

  logic [31:0] inst_D;
  logic        imul_req_rdy_D;
  logic        imul_resp_rdy_X;

  logic        br_cond_eq_X;
  logic        br_cond_lt_X;
  logic        br_cond_ltu_X;

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  //----------------------------------------------------------------------
  // Pack Memory Request Messages
  //----------------------------------------------------------------------

  assign imemreq_enq_msg.type_  = `VC_MEM_REQ_MSG_TYPE_READ;
  assign imemreq_enq_msg.opaque = 8'b0;
  assign imemreq_enq_msg.addr   = imemreq_msg_addr;
  assign imemreq_enq_msg.len    = 2'd0;
  assign imemreq_enq_msg.data   = 32'bx;

  //----------------------------------------------------------------------
  // Imem Drop Unit
  //----------------------------------------------------------------------

  vc_DropUnit #($bits(mem_resp_4B_t)) imem_drop_unit
  (
    .clk      (clk),
    .reset    (reset),

    .drop     (imemresp_drop),

    .in_msg   (imemresp_msg),
    .in_en    (imemresp_en),
    .in_rdy   (imemresp_rdy),

    .out_msg  (imemresp_msg_drop),
    .out_en   (imemresp_en_drop),
    .out_rdy  (imemresp_rdy_drop)
  );


//''' LAB TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''
// Add components
//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

  //----------------------------------------------------------------------
  // Control Unit
  //----------------------------------------------------------------------

  proc_ProcCtrlVRTL ctrl
  (
    .clk                    (clk),
    .reset                  (reset),

    // Instruction Memory Port

    .imemreq_en             (imemreq_enq_en),
    .imemreq_rdy            (imemreq_enq_rdy),
    .imemresp_en            (imemresp_deq_en),
    .imemresp_rdy           (imemresp_deq_rdy),

    // Drop signal

    .imemresp_drop          (imemresp_drop),

    // Data Memory Port

    .dmemreq_en             (dmemreq_en),
    .dmemreq_rdy            (dmemreq_rdy),
    .dmemreq_msg_type       (dmemreq_msg.type_),
    .dmemresp_en            (dmemresp_deq_en),
    .dmemresp_rdy           (dmemresp_deq_rdy),

    // mngr communication ports

    .mngr2proc_en           (mngr2proc_deq_en),
    .mngr2proc_rdy          (mngr2proc_deq_rdy),
    .proc2mngr_en           (proc2mngr_en),
    .proc2mngr_rdy          (proc2mngr_rdy),

    // xcel ports

    .xcelreq_en             (xcelreq_en),
    .xcelreq_rdy            (xcelreq_rdy),
    .xcelreq_msg_type       (xcelreq_msg.type_),

    .xcelresp_en            (xcelresp_deq_en),
    .xcelresp_rdy           (xcelresp_deq_rdy),

    // control signals (ctrl->dpath)

    .reg_en_F               (reg_en_F),
    .pc_sel_F               (pc_sel_F),

    .reg_en_D               (reg_en_D),
    .op1_byp_sel_D          (op1_byp_sel_D),
    .op2_byp_sel_D          (op2_byp_sel_D),
    .op1_sel_D              (op1_sel_D),
    .op2_sel_D              (op2_sel_D),
    .csrr_sel_D             (csrr_sel_D),
    .imm_type_D             (imm_type_D),
    .imul_req_en_D          (imul_req_en_D),

    .reg_en_X               (reg_en_X),
    .alu_fn_X               (alu_fn_X),
    .ex_result_sel_X        (ex_result_sel_X),
    .imul_resp_en_X         (imul_resp_en_X),

    .reg_en_M               (reg_en_M),
    .wb_result_sel_M        (wb_result_sel_M),

    .reg_en_W               (reg_en_W),
    .rf_waddr_W             (rf_waddr_W),
    .rf_wen_W               (rf_wen_W),
    .stats_en_wen_W         (stats_en_wen_W),

    // status signals (dpath->ctrl)

    .inst_D                 (inst_D),
    .imul_req_rdy_D         (imul_req_rdy_D),

    .imul_resp_rdy_X        (imul_resp_rdy_X),
    .br_cond_eq_X           (br_cond_eq_X),
    .br_cond_lt_X           (br_cond_lt_X),
    .br_cond_ltu_X          (br_cond_ltu_X),

    .commit_inst            (commit_inst)
  );

//''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

  //----------------------------------------------------------------------
  // Bypass Queue
  //----------------------------------------------------------------------

  logic [1:0] imemreq_q_num_free_entries;

  vc_Queue#(`VC_QUEUE_BYPASS,$bits(mem_req_4B_t),2) imemreq_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(imemreq_q_num_free_entries),
    .enq_en  (imemreq_enq_en),
    .enq_rdy (imemreq_enq_rdy),
    .enq_msg (imemreq_enq_msg),
    .deq_en  (imemreq_deq_en),
    .deq_rdy (imemreq_deq_rdy),
    .deq_ret (imemreq_deq_ret)
  );

  assign imemreq_deq_en = imemreq_deq_rdy && imemreq_rdy;
  assign imemreq_en     = imemreq_deq_rdy && imemreq_rdy;
  assign imemreq_msg    = imemreq_deq_ret;

  logic imemresp_q_num_free_entries;

  vc_Queue#(`VC_QUEUE_BYPASS,$bits(mem_resp_4B_t),1) imemresp_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(imemresp_q_num_free_entries),
    .enq_en  (imemresp_en_drop),
    .enq_rdy (imemresp_rdy_drop),
    .enq_msg (imemresp_msg_drop),
    .deq_en  (imemresp_deq_en),
    .deq_rdy (imemresp_deq_rdy),
    .deq_ret (imemresp_deq_ret)
  );

  logic dmemresp_q_num_free_entries;

  vc_Queue#(`VC_QUEUE_BYPASS,$bits(mem_resp_4B_t),1) dmemresp_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(dmemresp_q_num_free_entries),
    .enq_en  (dmemresp_en),
    .enq_rdy (dmemresp_rdy),
    .enq_msg (dmemresp_msg),
    .deq_en  (dmemresp_deq_en),
    .deq_rdy (dmemresp_deq_rdy),
    .deq_ret (dmemresp_deq_ret)
  );

  logic mngr2proc_q_num_free_entries;

  vc_Queue#(`VC_QUEUE_BYPASS,32,1) mngr2proc_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(mngr2proc_q_num_free_entries),
    .enq_en  (mngr2proc_en),
    .enq_rdy (mngr2proc_rdy),
    .enq_msg (mngr2proc_msg),
    .deq_en  (mngr2proc_deq_en),
    .deq_rdy (mngr2proc_deq_rdy),
    .deq_ret (mngr2proc_deq_ret)
  );


  // xcel

  logic xcelresp_q_num_free_entries;

  vc_Queue#(`VC_QUEUE_BYPASS,$bits(xcelresp_msg),1) xcelresp_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(xcelresp_q_num_free_entries),
    .enq_en  (xcelresp_en),
    .enq_rdy (xcelresp_rdy),
    .enq_msg (xcelresp_msg),
    .deq_en  (xcelresp_deq_en),
    .deq_rdy (xcelresp_deq_rdy),
    .deq_ret (xcelresp_deq_ret)
  );

  //----------------------------------------------------------------------
  // Datapath
  //----------------------------------------------------------------------

  proc_ProcDpathVRTL
  #(
    .p_num_cores             (p_num_cores)
  )
  dpath
  (
    .clk                     (clk),
    .reset                   (reset),

    // core id
    .core_id                 (core_id),

    // Instruction Memory Port

    .imemreq_msg_addr        (imemreq_msg_addr),
    .imemresp_msg            (imemresp_deq_ret),

    // Data Memory Port

    .dmemreq_msg_addr        (dmemreq_msg.addr),
    .dmemreq_msg_data        (dmemreq_msg.data),
    .dmemresp_msg_data       (dmemresp_deq_ret.data),

    // mngr communication ports

    .mngr2proc_data          (mngr2proc_deq_ret),
    .proc2mngr_data          (proc2mngr_msg),

    // xcel ports

    .xcelreq_msg_data        (xcelreq_msg.data),
    .xcelreq_msg_addr        (xcelreq_msg.addr),
    .xcelresp_msg_data       (xcelresp_deq_ret.data),

    // control signals (ctrl->dpath)

    .reg_en_F                (reg_en_F),
    .pc_sel_F                (pc_sel_F),

    .reg_en_D                (reg_en_D),
    .op1_byp_sel_D           (op1_byp_sel_D),
    .op2_byp_sel_D           (op2_byp_sel_D),
    .op1_sel_D               (op1_sel_D),
    .op2_sel_D               (op2_sel_D),
    .csrr_sel_D              (csrr_sel_D),
    .imm_type_D              (imm_type_D),
    .imul_req_en_D           (imul_req_en_D),

    .reg_en_X                (reg_en_X),
    .alu_fn_X                (alu_fn_X),
    .ex_result_sel_X         (ex_result_sel_X),
    .imul_resp_en_X          (imul_resp_en_X),

    .reg_en_M                (reg_en_M),
    .wb_result_sel_M         (wb_result_sel_M),

    .reg_en_W                (reg_en_W),
    .rf_waddr_W              (rf_waddr_W),
    .rf_wen_W                (rf_wen_W),
    .stats_en_wen_W          (stats_en_wen_W),

    // status signals (dpath->ctrl)

    .inst_D                  (inst_D),
    .imul_req_rdy_D          (imul_req_rdy_D),

    .imul_resp_rdy_X         (imul_resp_rdy_X),
    .br_cond_eq_X            (br_cond_eq_X),
    .br_cond_lt_X            (br_cond_lt_X),
    .br_cond_ltu_X           (br_cond_ltu_X),

    // stats_en

    .stats_en                (stats_en)
  );

  //----------------------------------------------------------------------
  // Line tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  rv2isa_InstTasks rv2isa();

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    if ( !ctrl.val_F )
      vc_trace.append_chars( trace_str, " ", 8 );
    else if ( ctrl.squash_F ) begin
      vc_trace.append_str( trace_str, "~" );
      vc_trace.append_chars( trace_str, " ", 8-1 );
    end else if ( ctrl.stall_F ) begin
      vc_trace.append_str( trace_str, "#" );
      vc_trace.append_chars( trace_str, " ", 8-1 );
    end else begin
      $sformat( str, "%x", dpath.pc_F );
      vc_trace.append_str( trace_str, str );
    end

    vc_trace.append_str( trace_str, "|" );

    if ( !ctrl.val_D )
      vc_trace.append_chars( trace_str, " ", 23 );
    else if ( ctrl.squash_D ) begin
      vc_trace.append_str( trace_str, "~" );
      vc_trace.append_chars( trace_str, " ", 23-1 );
    end else if ( ctrl.stall_D ) begin
      vc_trace.append_str( trace_str, "#" );
      vc_trace.append_chars( trace_str, " ", 23-1 );
    end else
      vc_trace.append_str( trace_str, { 3896'b0, rv2isa.disasm( ctrl.inst_D ) } );

    vc_trace.append_str( trace_str, "|" );

    if ( !ctrl.val_X )
      vc_trace.append_chars( trace_str, " ", 4 );
    else if ( ctrl.stall_X ) begin
      vc_trace.append_str( trace_str, "#" );
      vc_trace.append_chars( trace_str, " ", 4-1 );
    end else
      vc_trace.append_str( trace_str, { 4064'b0, rv2isa.disasm_tiny( ctrl.inst_X ) } );

    vc_trace.append_str( trace_str, "|" );

    if ( !ctrl.val_M )
      vc_trace.append_chars( trace_str, " ", 4 );
    else if ( ctrl.stall_M ) begin
      vc_trace.append_str( trace_str, "#" );
      vc_trace.append_chars( trace_str, " ", 4-1 );
    end else
      vc_trace.append_str( trace_str, { 4064'b0, rv2isa.disasm_tiny( ctrl.inst_M ) } );

    vc_trace.append_str( trace_str, "|" );

    if ( !ctrl.val_W )
      vc_trace.append_chars( trace_str, " ", 4 );
    else if ( ctrl.stall_W ) begin
      vc_trace.append_str( trace_str, "#" );
      vc_trace.append_chars( trace_str, " ", 4-1 );
    end else
      vc_trace.append_str( trace_str, { 4064'b0, rv2isa.disasm_tiny( ctrl.inst_W ) } );

  end
  `VC_TRACE_END

  vc_MemReqMsg4BTrace imemreq_trace
  (
    .clk   (clk),
    .reset (reset),
    .en    (imemreq_en),
    .rdy   (imemreq_rdy),
    .msg   (imemreq_msg)
  );

  vc_MemReqMsg4BTrace dmemreq_trace
  (
    .clk   (clk),
    .reset (reset),
    .en    (dmemreq_en),
    .rdy   (dmemreq_rdy),
    .msg   (dmemreq_msg)
  );

  vc_MemRespMsg4BTrace imemresp_trace
  (
    .clk   (clk),
    .reset (reset),
    .en    (imemresp_en),
    .rdy   (imemresp_rdy),
    .msg   (imemresp_msg)
  );

  vc_MemRespMsg4BTrace dmemresp_trace
  (
    .clk   (clk),
    .reset (reset),
    .en    (dmemresp_en),
    .rdy   (dmemresp_rdy),
    .msg   (dmemresp_msg)
  );

  `endif

endmodule

`endif /* PROC_PROC_V */

