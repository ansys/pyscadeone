#include "../../imports/user_types.h"
#include "swan_consts.h"
#include "textual_func_module0.h"
#include "../../imports/import_calculate_module0.h"
#include "half_module0.h"

void textual_func_module0(const array_int32_4 *i0, array_int32_4 * restrict o0)
{
  swan_size i1;
  array_int32_4 tmp_1;
  array_int32_4 tmp_2;
  import_calculate_module0(i0, &tmp_1);
  for (i1 = 0; i1 < 4; i1++) {
    tmp_2[i1] = tmp_1[i1] * swan_lit_int32(10);
  }
  half_module0((const array_int32_4 *) &tmp_2, o0);
}

