//========================================================================
// Verilog Components: Drop Unit
//========================================================================
// Drop unit allows dropping a packet when the drop signal is high. This
// is useful especially in pipelined processor, when a squash should drop
// a late arriving memory response.

`ifndef PROC_DROP_UNIT_V
`define PROC_DROP_UNIT_V

module vc_DropUnit
#(
  parameter   p_msg_nbits = 1
)
(
  input  logic                   clk,
  input  logic                   reset,

  // the drop signal will drop the next arriving packet

  input  logic                   drop,

  input  logic [p_msg_nbits-1:0] in_msg,
  input  logic                   in_en,
  output logic                   in_rdy,

  output logic [p_msg_nbits-1:0] out_msg,
  output logic                   out_en,
  input  logic                   out_rdy
);

  localparam c_state_pass = 1'b0;
  localparam c_state_drop = 1'b1;

  logic state;
  logic next_state;

  // assign output message same as input message

  assign out_msg = in_msg;

  // next state

  always_comb begin
    if ( state == c_state_pass ) begin

      // we only go to drop state if there is a drop request and we cannot
      // drop it right away (!in_en)
      if ( drop && !in_en )
        next_state = c_state_drop;
      else
        next_state = c_state_pass;

    end else begin

      // if we are in the drop mode and a message arrives, we can go back
      // to pass state
      if ( in_en )
        next_state = c_state_pass;
      else
        next_state = c_state_drop;

    end
  end

  // state outputs

  always_comb begin
    if ( state == c_state_pass ) begin

      // we combinationally take care of dropping if the packet is already
      // available
      out_en = in_en && !drop;
      in_rdy = out_rdy;

    end else begin

      // we just drop the packet
      out_en = 1'b0;
      in_rdy = 1'b1;

    end
  end

  // state transitions

  always_ff @( posedge clk ) begin

    if ( reset )
      state <= c_state_pass;
    else
      state <= next_state;

  end

endmodule

`endif /* PROC_DROP_UNIT_V */

