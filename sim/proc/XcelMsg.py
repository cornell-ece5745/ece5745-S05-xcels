#=========================================================================
# XcelMsg
#=========================================================================
# Accelerator request and response messages.

from pymtl3 import *
from pymtl3.stdlib.ifcs.XcelMsg import mk_xcel_msg

#-------------------------------------------------------------------------
# XcelReqMsg
#-------------------------------------------------------------------------
# Accelerator request messages can either be to read or write an
# accelerator register. Read requests include just a register specifier,
# while write requests include an accelerator register specifier and the
# actual data to write to the accelerator register.
#
# Message Format:
#
#    1b     5b      32b
#  +------+-------+-----------+
#  | type | raddr | data      |
#  +------+-------+-----------+
#

#-------------------------------------------------------------------------
# XcelRespMsg
#-------------------------------------------------------------------------
# Accelerator response messages can either be from a read or write of an
# accelerator register. Read requests include the actual value read from
# the accelerator register, while write requests currently include
# nothing other than the type.
#
# Message Format:
#
#    1b     32b
#  +------+-----------+
#  | type | data      |
#  +------+-----------+
#

XcelReqMsg, XcelRespMsg = mk_xcel_msg( 5, 32 )

XCEL_TYPE_READ  = b1(0)
XCEL_TYPE_WRITE = b1(1)

class XcelMsgs:
  req  = XcelReqMsg
  resp = XcelRespMsg
