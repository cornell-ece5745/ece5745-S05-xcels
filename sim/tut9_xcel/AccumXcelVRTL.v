//========================================================================
// Accumulator Xcel Unit RTL Model
//========================================================================

`ifndef TUT9_XCEL_ACCUM_XCEL_V
`define TUT9_XCEL_ACCUM_XCEL_V

`include "vc/trace.v"

`include "vc/mem-msgs.v"
`include "vc/queues.v"
`include "proc/XcelMsg.v"

//========================================================================
// ACCUM Xcel Implementation
//========================================================================

module tut9_xcel_AccumXcelVRTL
(
  input  logic        clk,
  input  logic        reset,

  // Interface

  output logic         xcelreq_rdy,
  input  logic         xcelreq_en,
  input  XcelReqMsg    xcelreq_msg,

  input  logic         xcelresp_rdy,
  output logic         xcelresp_en,
  output XcelRespMsg   xcelresp_msg,

  input  logic         memreq_rdy,
  output logic         memreq_en,
  output mem_req_4B_t  memreq_msg,

  output logic         memresp_rdy,
  input  logic         memresp_en,
  input  mem_resp_4B_t memresp_msg

);

  // Accelerator ports and queues

  logic        xcelreq_deq_en;
  logic        xcelreq_deq_rdy;
  XcelReqMsg   xcelreq_deq_ret;

  vc_Queue#(`VC_QUEUE_PIPE,$bits(xcelreq_msg),1) xcelreq_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(),
    .enq_en  (xcelreq_en),
    .enq_rdy (xcelreq_rdy),
    .enq_msg (xcelreq_msg),
    .deq_en  (xcelreq_deq_en),
    .deq_rdy (xcelreq_deq_rdy),
    .deq_ret (xcelreq_deq_ret)
  );

  // Memory ports and queues

  logic           memresp_deq_en;
  logic           memresp_deq_rdy;
  mem_resp_4B_t   memresp_deq_ret;

  vc_Queue#(`VC_QUEUE_PIPE,$bits(memresp_msg),1) memresp_q
  (
    .clk     (clk),
    .reset   (reset),
    .num_free_entries(),
    .enq_en  (memresp_en),
    .enq_rdy (memresp_rdy),
    .enq_msg (memresp_msg),
    .deq_en  (memresp_deq_en),
    .deq_rdy (memresp_deq_rdy),
    .deq_ret (memresp_deq_ret)
  );

  // Extra state registers

  logic [31:0] idx,         idx_in;
  logic [31:0] size,        size_in;
  logic [31:0] base_src,    base_src_in;
  logic [31:0] result,      result_in;

  always_ff @(posedge clk) begin
    idx         <= idx_in;
    size        <= size_in;
    base_src    <= base_src_in;
    result      <= result_in;
  end

  //======================================================================
  // State Update
  //======================================================================

  typedef enum logic [$clog2(3)-1:0] {
    STATE_XCFG,
    STATE_M_RD,
    STATE_CALC
  } state_t;

  state_t state_reg;

  logic go;

  always_ff @(posedge clk) begin

    if ( reset )
      state_reg <= STATE_XCFG;
    else begin
      state_reg <= state_reg;

      case ( state_reg )

        STATE_XCFG:

          // ''' SECTION TASK ''''''''''''''''''''''''''''''''''''''''''''
          // Add the state transition logic for XCFG state.
          // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        STATE_M_RD:
          if ( memreq_rdy  )
            state_reg <= STATE_CALC;

        STATE_CALC:
          if ( memresp_deq_rdy )
            if ( idx < size - 1 )
              state_reg <= STATE_M_RD;
            else
              state_reg <= STATE_XCFG;

        default:
          state_reg <= STATE_XCFG;

      endcase
    end
  end

  //======================================================================
  // State Outputs
  //======================================================================

  // Temporary
  logic [31:0] base_addr;

  always_comb begin

    xcelreq_deq_en = 0;
    xcelresp_en    = 0;
    memreq_en      = 0;
    memresp_deq_en = 0;
    go             = 0;

    base_src_in    = base_src;
    size_in        = size;

    //--------------------------------------------------------------------
    // STATE: XCFG
    //--------------------------------------------------------------------
    // In this state we handle the accelerator configuration protocol,
    // where we write the base addresses, size, and then tell the
    // accelerator to start. We also handle responding when the
    // accelerator is done.

    if ( state_reg == STATE_XCFG ) begin

      if ( xcelreq_deq_rdy & xcelresp_rdy ) begin
        xcelreq_deq_en = 1;
        xcelresp_en    = 1;

        // Send xcel response message, obviously you only want to
        // send the response message when accelerator is done

        if ( xcelreq_deq_ret.type_ == `XcelReqMsg_TYPE_READ ) begin
          xcelresp_msg.type_ = `XcelRespMsg_TYPE_READ;
          xcelresp_msg.data  = result;
        end
        else begin
          if ( xcelreq_deq_ret.addr == 0 ) begin
            go        = 1;
            idx_in    = 0;
            result_in = 0;
          end
          else if ( xcelreq_deq_ret.addr == 1 )
            base_src_in = xcelreq_deq_ret.data;

          else if ( xcelreq_deq_ret.addr == 2 )
            size_in = xcelreq_deq_ret.data;

          xcelresp_msg.type_ = `XcelRespMsg_TYPE_WRITE;
          xcelresp_msg.data  = 0;
        end
      end
    end

    //--------------------------------------------------------------------
    // STATE: M_RD
    //--------------------------------------------------------------------
    // Memory read stage. Send memory request to read src[i].

    else if ( state_reg == STATE_M_RD )
    begin
      if ( memreq_rdy )
      begin
        memreq_en            = 1;
        memreq_msg.type_ = `VC_MEM_REQ_MSG_TYPE_READ;
        memreq_msg.addr  = base_src + (idx << 2);
        memreq_msg.len   = 0;
      end
    end

    //--------------------------------------------------------------------
    // STATE: CALC
    //--------------------------------------------------------------------
    // Wait for memory response to come back, then do accumulate.

    else if ( state_reg == STATE_CALC )
    begin
      if ( memresp_deq_rdy ) begin
        memresp_deq_en = 1;
        result_in = result + memresp_deq_ret.data;

        // if idx < size - 1, still not through entire vector
        if ( idx < size - 1 )
          idx_in = idx + 1;
        else
          idx_in = 0;
      end
    end
  end

  //======================================================================
  // Line Tracing
  //======================================================================

  `ifndef SYNTHESIS

  logic [`VC_TRACE_NBITS-1:0] str;
  `VC_TRACE_BEGIN
  begin
    $sformat( str, "xr%2x = %x", xcelreq_msg.addr, xcelreq_msg.data );
    vc_trace.append_en_rdy_str( trace_str, xcelreq_en, xcelreq_rdy, str );

    vc_trace.append_str( trace_str, "(" );

    case ( state_reg )
      STATE_XCFG:      vc_trace.append_str( trace_str, "X " );
      STATE_M_RD:      vc_trace.append_str( trace_str, "RD" );
      STATE_CALC:      vc_trace.append_str( trace_str, "C " );
      default:         vc_trace.append_str( trace_str, "? " );
    endcase
    vc_trace.append_str( trace_str, " " );

    $sformat( str, "%x", result  );
    vc_trace.append_str( trace_str, str );

    vc_trace.append_str( trace_str, "|" );

    $sformat( str, "%x", memreq_msg.data );
    vc_trace.append_en_rdy_str( trace_str, memreq_en, memreq_rdy, str );

    $sformat( str, "%x", memresp_msg.data );
    vc_trace.append_en_rdy_str( trace_str, memresp_en, memresp_rdy, str );

    vc_trace.append_str( trace_str, ")" );

    $sformat( str, "%x", xcelresp_msg.data );
    vc_trace.append_en_rdy_str( trace_str, xcelresp_en, xcelresp_rdy, str );

  end
  `VC_TRACE_END

  `endif /* SYNTHESIS */

endmodule

`endif /* TUT9_XCEL_ACCUM_XCEL_V */

