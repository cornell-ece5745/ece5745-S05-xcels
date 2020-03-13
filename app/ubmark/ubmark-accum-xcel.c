//========================================================================
// ubmark-accum-xcel
//========================================================================

#include "common.h"
#include "ubmark-accum.dat"

//------------------------------------------------------------------------
// accum_xcel
//------------------------------------------------------------------------

__attribute__ ((noinline))
int accum_xcel( int* src, int size )
{
  int result = 0;

  asm volatile (
    "csrw ?????, %[src]; \n"
    "csrw ?????, %[size];\n"
    "csrw ?????, x0     ;\n"
    "csrr %[result], ?????;\n"

    // Outputs from the inline assembly block

    : [result] "=r"(result)

    // Inputs to the inline assembly block

    : [src]    "r"(src),
      [size]   "r"(size)

    // Tell the compiler this accelerator read/writes memory

    : "memory"
  );

  return result;
}

//------------------------------------------------------------------------
// verify_results
//------------------------------------------------------------------------

void verify_results( int sum, int ref )
{
  if ( sum != ref )
    test_fail( 0, sum, ref );
  test_pass();
}

//------------------------------------------------------------------------
// Test Harness
//------------------------------------------------------------------------

int main( int argc, char* argv[] )
{
  test_stats_on();
  int sum = accum_xcel( src, size );
  test_stats_off();

  verify_results( sum, ref );

  return 0;
}

