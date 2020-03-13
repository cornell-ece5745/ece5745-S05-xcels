//------------------------------------------------------------------------
// 128 bits x 256 words SRAM
//------------------------------------------------------------------------

`ifndef SRAM_128x256_1P
`define SRAM_128x256_1P

`include "sram/SramGenericVRTL.v"

`ifndef SYNTHESIS

module SRAM_128x256_1P
(
  input  logic         CE1,
  input  logic         WEB1,
  input  logic         OEB1,
  input  logic         CSB1,
  input  logic [7:0]   A1,
  input  logic [127:0] I1,
  output logic [127:0] O1
);

  sram_SramGenericVRTL
  #(
    .p_data_nbits  (128),
    .p_num_entries (256)
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

`endif /* SRAM_128x256_1P */
