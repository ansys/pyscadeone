#include "swan_types.h"
#include "half_module0.h"

void half_module0(const array_i32_4 *i0, array_i32_4 * o0)
{
  swan_size i1;

  for (i1 = 0; i1 < 4; i1++) {
    (*o0)[i1] = (*i0)[i1] / swan_lit_i32(2);
  }
}
