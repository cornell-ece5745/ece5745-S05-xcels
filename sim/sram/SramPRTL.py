#=========================================================================
# SRAM RTL with custom low-level interface
#=========================================================================
# This is the SRAM RTL model with our own low-level interface. It contains
# an instance of either a SRAM generated by OpenRAM memory compiler or a
# This is the SRAM RTL model with our own low-level interfacegeneric
# SRAM RTL model (SramGenericPRTL).
#
# The interface of this module are prefixed by port0_, meaning all reads
# and writes happen through the only port. Multiported SRAMs have ports
# prefixed by port1_, port2_, etc.
#
# The following list describes each port of this module.
#
#  Port Name     Direction  Description
#  -----------------------------------------------------------------------
#  port0_val     I          port enable (1 = enabled)
#  port0_type    I          transaction type, 0 = read, 1 = write
#  port0_idx     I          index
#  port0_wdata   I          write data
#  port0_rdata   O          read data output
#

from pymtl3           import *
from .SramGenericPRTL import SramGenericPRTL
from .SRAM_32x256_1P  import SRAM_32x256_1P
from .SRAM_128x256_1P import SRAM_128x256_1P

# ''' TUTORIAL TASK '''''''''''''''''''''''''''''''''''''''''''''''''''''
# Import new SRAM configuration RTL model
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

from .SRAM_64x64_1P   import SRAM_64x64_1P

# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

class SramPRTL( Component ):

  def construct( s, data_nbits=32, num_entries=256, mask_size=0 ):

    idx_nbits = clog2( num_entries )      # address width
    nbytes    = int( data_nbits + 7 ) // 8 # $ceil(data_nbits/8)

    s.port0_val   = InPort ()
    s.port0_type  = InPort ()
    s.port0_idx   = InPort ( mk_bits(idx_nbits) )
    s.port0_wdata = InPort ( mk_bits(data_nbits) )
    s.port0_rdata = OutPort( mk_bits(data_nbits) )

    s.mask_size = mask_size
    if mask_size > 0:
      s.port0_wben  = InPort( mk_bits(mask_size) )

    # Inverters

    s.port0_val_bar  = Wire()
    s.port0_val_bar  //= lambda: ~s.port0_val

    # if you have implemented a new SRAM, make sure use it
    # here instead of the generic one.

    if data_nbits == 128 and num_entries == 256 and mask_size > 0:
      assert mask_size == 4, "We only support dividing 128x256 into four 32x256"

      s.webs = Wire( mk_bits(mask_size) )
      for i in range(mask_size):
        s.webs[i] //= lambda: ~(s.port0_type & s.port0_wben[i])

      s.srams = [
        SRAM_32x256_1P()(
          CE1  = s.clk,
          CSB1 = s.port0_val_bar,  # CSB1 low-active
          OEB1 = 0,
          WEB1 = s.webs[i], # WEB1 low-active
          A1   = s.port0_idx,
          I1   = s.port0_wdata[i*32:(i+1)*32],
          O1   = s.port0_rdata[i*32:(i+1)*32],
        )
        for i in range(4)
      ]

    else:
      assert mask_size == 0, "We only support dividing 128x256 into four 32x256"

      s.port0_type_bar = Wire()
      s.port0_type_bar //= lambda: ~s.port0_type

      if   data_nbits == 32 and num_entries == 256:

        s.sram = SRAM_32x256_1P()(
          CE1  = s.clk,
          CSB1 = s.port0_val_bar,  # CSB1 low-active
          OEB1 = 0,
          WEB1 = s.port0_type_bar, # WEB1 low-active
          A1   = s.port0_idx,
          I1   = s.port0_wdata,
          O1   = s.port0_rdata,
        )


      # ''' TUTORIAL TASK '''''''''''''''''''''''''''''''''''''''''''''''''
      # Choose new SRAM configuration RTL model
      # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''\/

      elif data_nbits == 64 and num_entries == 64:
        s.sram = SRAM_64x64_1P()(
          CE1  = s.clk,
          CSB1 = s.port0_val_bar,  # CSB1 low-active
          OEB1 = 0,
          WEB1 = s.port0_type_bar, # WEB1 low-active
          A1   = s.port0_idx,
          I1   = s.port0_wdata,
          O1   = s.port0_rdata,
        )

      # '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''/\

      else:
        s.sram = SramGenericPRTL( data_nbits, num_entries )(
          CE1  = s.clk,
          CSB1 = s.port0_val_bar,  # CSB1 low-active
          OEB1 = 0,
          WEB1 = s.port0_type_bar, # WEB1 low-active
          A1   = s.port0_idx,
          I1   = s.port0_wdata,
          O1   = s.port0_rdata,
        )

  def line_trace( s ):
    try:
      print(s.webs, s.port0_wben)
    except: pass
    if s.mask_size == 0:
      return f"(A1={s.sram.A1} I1={s.sram.I1} O1={s.sram.O1})"
    return "".join([ f"(A1={x.A1} I1={x.I1} O1={x.O1})" for x in s.srams ])
