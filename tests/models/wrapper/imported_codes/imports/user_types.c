#include "user_types.h"

#ifdef swan_use_array_int32_4
swan_bool swan_eq_array_int32_4(
  const array_int32_4 *swan_c1,
  const array_int32_4 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 4; swan_ci++) {
    swan_equ = swan_equ & ((*swan_c1)[swan_ci] == (*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif
