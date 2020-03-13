#=========================================================================
# XcelMsg_test
#=========================================================================
# Test suite for accelerator request and response messages.

from pymtl3   import *
from proc.XcelMsg import XcelReqMsg, XcelRespMsg, XCEL_TYPE_READ, XCEL_TYPE_WRITE

#-------------------------------------------------------------------------
# test_req_fields
#-------------------------------------------------------------------------

def test_req_fields():

  # Create msg

  msg = XcelReqMsg(XCEL_TYPE_READ, 15)

  # Verify msg

  assert msg.type_ == 0
  assert msg.addr == 15

  # Create msg

  msg = XcelReqMsg(XCEL_TYPE_WRITE, 13 )
  msg.data = b32(0xdeadbeef)

  # Verify msg

  assert msg.type_ == 1
  assert msg.addr == 13
  assert msg.data  == 0xdeadbeef

#-------------------------------------------------------------------------
# test_req_str
#-------------------------------------------------------------------------

def test_req_str():

  # Create msg

  msg = XcelReqMsg(XCEL_TYPE_READ, 15)

  # Verify string

  assert str(msg) == "rd:0f:        "

  # Create msg

  msg = XcelReqMsg(XCEL_TYPE_WRITE, 13, 0xdeadbeef)

  # Verify string

  assert str(msg) == "wr:0d:deadbeef"

#-------------------------------------------------------------------------
# test_resp_fields
#-------------------------------------------------------------------------

def test_resp_fields():

  # Create msg

  msg = XcelRespMsg(XCEL_TYPE_READ, 0xcafecafe)

  # Verify msg

  assert msg.type_ == 0
  assert msg.data  == 0xcafecafe

  # Create msg

  msg = XcelRespMsg()
  msg.type_ = XCEL_TYPE_WRITE
  msg.data  = b32(0)

  # Verify msg

  assert msg.type_ == 1
  assert msg.data  == 0

#-------------------------------------------------------------------------
# test_resp_str
#-------------------------------------------------------------------------

def test_resp_str():

  # Create msg

  msg = XcelRespMsg()
  msg.type_ = XCEL_TYPE_READ
  msg.data  = b32(0xcafecafe)

  # Verify string

  assert str(msg) == "rd:cafecafe"

  # Create msg

  msg = XcelRespMsg()
  msg.type_ = XCEL_TYPE_WRITE
  msg.data  = b32(0)

  assert str(msg) == "wr:        "

