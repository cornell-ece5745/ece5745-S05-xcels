//=========================================================================
// Integer Multiplier Single-Cycle Implementation
//=========================================================================

`ifndef LAB1_IMUL_INT_MUL_SCYCLE_V
`define LAB1_IMUL_INT_MUL_SCYCLE_V

`include "vc/trace.v"
`include "vc/regs.v"

//=========================================================================
// Integer Multiplier Single-Cycle Implementation
//=========================================================================

module lab1_imul_IntMulScycleVRTL
(
  input  logic        clk,
  input  logic        reset,

  input  logic        req_en,
  output logic        req_rdy,
  input  logic [63:0] req_msg,

  output logic        resp_en,
  input  logic        resp_rdy,
  output logic [31:0] resp_msg
);

  // Input registers

  logic en_reg_out;

  vc_EnReg#(1) en_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (req_en),
    .en    (resp_rdy),
    .q     (en_reg_out)
  );

  logic [31:0] a_reg_out;

  vc_EnReg#(32) a_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (req_msg[63:32]),
    .en    (resp_rdy),
    .q     (a_reg_out)
  );

  logic [31:0] b_reg_out;

  vc_EnReg#(32) b_reg
  (
    .clk   (clk),
    .reset (reset),
    .d     (req_msg[31:0]),
    .en    (resp_rdy),
    .q     (b_reg_out)
  );

  assign req_rdy  = resp_rdy;
  assign resp_en  = en_reg_out && resp_rdy;
  assign resp_msg = a_reg_out * b_reg_out;

  //----------------------------------------------------------------------
  // Line Tracing
  //----------------------------------------------------------------------

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin

    $sformat( str, "%x", req_msg );

    vc_trace.append_en_rdy_str( trace_str, req_en, req_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    if ( en_reg_out ) begin
      vc_trace.append_str( trace_str, "*" );
    end else begin
      vc_trace.append_str( trace_str, " " );
    end

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", resp_msg );
    vc_trace.append_en_rdy_str( trace_str, resp_en, resp_rdy, str );
  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* LAB1_IMUL_INT_MUL_SCYCLE_V */
