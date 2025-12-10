#include "swan_sensors.h"
#include "swan_consts.h"
#include "operator0_module0.h"

/* module0::operator0 */
void operator0_module0(
    /* i0 */
    const array_int32_4 *i0,
    /* o0 */ array_int32_4 *restrict o0,
    outC_operator0_module0 *restrict outC)
{
  swan_size i1;

  for (i1 = 0; i1 < 4; i1++)
  {
    (*o0)[i1] = (*i0)[i1] * swan_lit_int32(10);
  }
}

void operator0_init_module0(outC_operator0_module0 *restrict outC)
{
}

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void operator0_reset_module0(outC_operator0_module0 *restrict outC)
{
}
#endif