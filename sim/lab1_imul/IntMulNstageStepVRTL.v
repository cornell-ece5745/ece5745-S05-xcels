//========================================================================
// Integer Multiplier Nstage shift and add step
//========================================================================

`ifndef LAB1_IMUL_INT_MUL_NSTAGE_STEP_V
`define LAB1_IMUL_INT_MUL_NSTAGE_STEP_V

`include "vc/muxes.v"
`include "vc/regs.v"
`include "vc/arithmetic.v"

//========================================================================
// Integer Multiplier Nstage Step
//========================================================================

module lab1_imul_IntMulNstageStepVRTL
(
  input  logic        in_en,
  input  logic [31:0] in_a,
  input  logic [31:0] in_b,
  input  logic [31:0] in_result,

  output logic        out_en,
  output logic [31:0] out_a,
  output logic [31:0] out_b,
  output logic [31:0] out_result
);

  // Right shifter

  vc_RightLogicalShifter#(32,1) rshifter
  (
    .in    (in_b),
    .shamt (1'b1),
    .out   (out_b)
  );

  // Left shifter

  vc_LeftLogicalShifter#(32,1) lshifter
  (
    .in    (in_a),
    .shamt (1'b1),
    .out   (out_a)
  );

  // Adder

  logic [31:0] add_out;

  vc_SimpleAdder#(32) add
  (
    .in0   (in_a),
    .in1   (in_result),
    .out   (add_out)
  );

  // Result mux

  vc_Mux2#(32) result_mux
  (
    .sel   (in_b[0]),
    .in0   (in_result),
    .in1   (add_out),
    .out   (out_result)
  );

  // Connect the enid bits

  assign out_en = in_en;

endmodule

`endif /* LAB1_IMUL_INT_MUL_NSTAGE_STEP_V */

