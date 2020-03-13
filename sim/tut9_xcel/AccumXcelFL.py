#=========================================================================
# Accumulator Xcel Unit FL Model
#=========================================================================
# Accumulates values in a vector in memory.
# Accelerator register interface:
#
#  xr0 : go/done
#  xr1 : base address of the array src
#  xr2 : size of the array
#
# Accelerator protocol involves the following steps:
#  1. Write the base address of src to xr1
#  2. Write the number of elements in the array to xr2
#  3. Tell accelerator to go by writing xr0
#  4. Wait for accelerator to finish by reading xr0, result will be sum

from pymtl3      import *
from pymtl3.stdlib.ifcs.xcel_ifcs import XcelMinionIfcFL
from pymtl3.stdlib.ifcs.mem_ifcs  import MemMasterIfcFL

class AccumXcelFL( Component ):

  def read( s, addr ):
    return s.xr[addr]

  def write( s, addr, data ):

    if addr == 0:
      base = s.xr[1]
      size = s.xr[2]

      s.xr[0] = b32(0)
      for i in range( size ):
        s.xr[0] += s.mem.read( addr=base + i*4, nbytes=4 )

    else:
      s.xr[addr] = b32(data)

  # Constructor

  def construct( s ):

    # Interface

    s.xcel = XcelMinionIfcFL( read=s.read, write=s.write )
    s.mem  = MemMasterIfcFL()

    # Storage

    s.xr = [ b32(0) for _ in range(3) ]

    # Explicitly tell PyMTL3 than s.read calls s.mem.read

    s.add_constraints(
      M(s.read)  == M(s.mem.read),
      M(s.write) == M(s.mem.write),
    )

  # Line tracing

  def line_trace( s ):
    return f"{s.xcel}|{s.mem}"
