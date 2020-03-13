//========================================================================
// 64 bits x 64 words SRAM
//========================================================================

`ifndef SRAM_64x64_1P
`define SRAM_64x64_1P

`include "sram/SramGenericVRTL.v"

`ifndef SYNTHESIS

module SRAM_64x64_1P
(
  input  logic        CE1,
  input  logic        WEB1,
  input  logic        OEB1,
  input  logic        CSB1,
  input  logic [5:0]  A1,
  input  logic [63:0] I1,
  output logic [63:0] O1
);

  sram_SramGenericVRTL
  #(
    .p_data_nbits  (64),
    .p_num_entries (64)
  )
  sram_generic
  (
    .CE1  (CE1),
    .A1   (A1),
    .WEB1 (WEB1),
    .OEB1 (OEB1),
    .CSB1 (CSB1),
    .I1   (I1),
    .O1   (O1)
  );

endmodule

`endif /* SYNTHESIS */

`endif /* SRAM_64x64_1P */

