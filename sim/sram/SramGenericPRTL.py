#=========================================================================
# Generic model of the SRAM
#=========================================================================
# This is meant to be instantiated within a carefully named outer module
# so the outer module corresponds to an SRAM generated with the
# CACTI-based memory compiler.

from pymtl3 import *

class SramGenericPRTL( Component ):

  def construct( s, data_nbits=32, num_entries=256 ):
    DataType = mk_bits(data_nbits)

    addr_width = clog2( num_entries )      # address width
    nbytes     = int( data_nbits + 7 ) // 8 # $ceil(data_nbits/8)

    # port names set to match the ARM memory compiler

    # clock (in PyMTL simulation it uses implict .clk port when
    # translated to Verilog, actual clock ports should be CE1

    s.CE1  = InPort ()                      # clk
    s.WEB1 = InPort ()                      # bar( write en )
    s.OEB1 = InPort ()                      # bar( out en )
    s.CSB1 = InPort ()                      # bar( whole SRAM en )
    s.A1   = InPort ( mk_bits(addr_width) ) # address
    s.I1   = InPort ( DataType )            # write data
    s.O1   = OutPort( DataType )            # read data

    # memory array

    s.ram = [ Wire( DataType ) for _ in range( num_entries ) ]

    # read path

    s.dout = Wire( DataType )

    @s.update_ff
    def read_logic():
      if ~s.CSB1 & s.WEB1:
        s.dout <<= s.ram[ s.A1 ]
      else:
        s.dout <<= DataType(0)

    @s.update
    def comb_logic():
      if ~s.OEB1:
        s.O1 = s.dout
      else:
        s.O1 = DataType(0)

    # write path

    @s.update_ff
    def write_logic():
      if ~s.CSB1 and ~s.WEB1:
        s.ram[s.A1] <<= s.I1
