//========================================================================
// CalcShamtVRTL
//========================================================================
// Looking at least significant eight bits, calculate how many bits we
// want to shift.

`ifndef LAB1_IMUL_CALC_SHAMT_V
`define LAB1_IMUL_CALC_SHAMT_V

module lab1_imul_IntMulVarLatCalcShamtVRTL
(
  input  logic [7:0] in_,
  output logic [3:0] out
);

  always @(*) begin
    if      (in_ == 0) out = 8;
    else if ( in_[0] ) out = 1;
    else if ( in_[1] ) out = 1;
    else if ( in_[2] ) out = 2;
    else if ( in_[3] ) out = 3;
    else if ( in_[4] ) out = 4;
    else if ( in_[5] ) out = 5;
    else if ( in_[6] ) out = 6;
    else if ( in_[7] ) out = 7;
  end

endmodule

`endif /* LAB1_IMUL_CALC_SHAMT_V */

