#=========================================================================
# TestCacheSink.py
#=========================================================================

from pymtl3  import *
from pymtl3.stdlib.ifcs import MemMsgType

class TestCacheSink( Component ):

  def construct( s, Type, msgs, initial_delay=0, interval_delay=0,
                 arrival_time=None, check_test=False ):

    s.recv.Type = Type
    s.check_test = check_test

    # [msgs] and [arrival_time] must have the same length.
    if arrival_time is not None:
      assert len( msgs ) == len( arrival_time )

    s.idx          = 0
    s.cycle_count  = 0
    s.msgs         = list( msgs )
    s.arrival_time = None if not arrival_time else list( arrival_time )
    s.error_msg    = ''

    s.all_msg_recved = False
    s.done_flag      = False

    s.count = initial_delay
    s.intv  = interval_delay

    s.recv_called = False

    @s.update
    def up_sink_count():
      # Raise exception at the start of next cycle so that the errored
      # line trace gets printed out
      if s.error_msg:
        raise Exception( s.error_msg )

      # Tick one more cycle after all message is received so that the
      # exception gets thrown
      if s.all_msg_recved:
        s.done_flag = True

      if s.idx >= len( s.msgs ):
        s.all_msg_recved = True

      if not s.reset:
        s.cycle_count += 1
      else:
        s.cycle_count = 0

      # if recv was called in previous cycle
      if s.recv_called:
        s.count = s.intv
      elif s.count != 0:
        s.count -= 1
      else:
        s.count = 0

      s.recv_called = False

    s.add_constraints(
      U( up_sink_count ) < M( s.recv ),
      U( up_sink_count ) < M( s.recv.rdy )
    )

  def compare_cacheresp( s, msg, ref ):
    if msg.type_  != ref.type_ or msg.len != ref.len or msg.opaque != msg.opaque:
      return False

    # if memresp is a write, ignore the data
    if   ref.type_ == MemMsgType.WRITE:
      pass

    elif ref.type_ == MemMsgType.WRITE_INIT:
      pass

    else:
      if ref.data != msg.data:
        return False

    # check test field
    if s.check_test:
      if ref.test != 2:
        if ref.test != msg.test:
          return False

    return True

  @non_blocking( lambda s: s.count==0 )
  def recv( s, msg ):
    assert s.count == 0

    # Sanity check
    if s.idx >= len( s.msgs ):
      s.error_msg = ( 'Test Sink received more msgs than expected!\n'
                      f'Received : {msg}' )

    # Check correctness first
    elif not s.compare_cacheresp( msg, s.msgs[s.idx] ):
      s.error_msg = (
        f'Test sink {s} received WRONG message!\n'
        f'Expected : { s.msgs[ s.idx ] }\n'
        f'Received : { msg }'
      )

    # Check timing if performance regeression is turned on
    elif s.arrival_time and s.cycle_count > s.arrival_time[ s.idx ]:
      s.error_msg = (
        f'Test sink {s} received message LATER than expected!\n'
        f'Expected msg : {s.msgs[ s.idx ]}\n'
        f'Expected at  : {s.arrival_time[ s.idx ]}\n'
        f'Received msg : {msg}\n'
        f'Received at  : {s.cycle_count}'
      )

    else:
      s.idx += 1
      s.recv_called = True

  def done( s ):
    return s.done_flag

  # Line trace
  def line_trace( s ):
    return "{}".format( s.recv )
