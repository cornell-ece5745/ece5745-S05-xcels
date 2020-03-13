//========================================================================
// ubmark-accum
//========================================================================

#include "common.h"
#include "ubmark-accum.dat"

//------------------------------------------------------------------------
// accum-scalar
//------------------------------------------------------------------------

__attribute__ ((noinline))
int accum_scalar( int* src, int size )
{
  // ''' SECTION TASK ''''''''''''''''''''''''''''''''''''''''''''''''''''
  // Implement a simple C function to add all of the elements in the
  // source array and then return this result.
  // '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
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
  int sum = accum_scalar( src, size );
  test_stats_off();

  verify_results( sum, ref );

  return 0;
}
