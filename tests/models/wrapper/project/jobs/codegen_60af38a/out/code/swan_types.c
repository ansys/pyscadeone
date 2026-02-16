/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_types.h"

#ifdef swan_use_array_int32_2_3
swan_bool swan_eq_array_int32_2_3(
  const array_int32_2_3 *swan_c1,
  const array_int32_2_3 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 3; swan_ci++) {
    swan_equ = swan_equ && swan_eq_array_int32_2(
        &(*swan_c1)[swan_ci],
        &(*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif /* swan_use_array_int32_2_3 */

#ifdef swan_use_array_int32_2
swan_bool swan_eq_array_int32_2(
  const array_int32_2 *swan_c1,
  const array_int32_2 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 2; swan_ci++) {
    swan_equ = swan_equ && (*swan_c1)[swan_ci] == (*swan_c2)[swan_ci];
  }
  return swan_equ;
}
#endif /* swan_use_array_int32_2 */

/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.c
*************************************************************$ */
