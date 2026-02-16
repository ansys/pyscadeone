/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_types.h"

#ifdef swan_use_T_Variant_module0
swan_bool swan_eq_T_Variant_module0(
  const T_Variant_module0 *swan_c1,
  const T_Variant_module0 *swan_c2)
{
  swan_bool swan_equ;

  swan_equ = swan_c1->T_bool_box.swan_tag == swan_c2->T_bool_box.swan_tag;
  if (swan_equ) {
    switch (swan_c1->T_bool_box.swan_tag) {
      case T_int :
        swan_equ = swan_equ && swan_c1->T_int.swan_value == swan_c2->T_int.swan_value;
        break;
      case T_bool_box :
        swan_equ = swan_equ && swan_eq_array_bool_1(
            &swan_c1->T_bool_box.swan_value,
            &swan_c2->T_bool_box.swan_value);
        break;
      default :
        /* this default branch is unreachable */
        break;
    }
  }
  return swan_equ;
}
#endif /* swan_use_T_Variant_module0 */

#ifdef swan_use_array_1
swan_bool swan_eq_array_1(const array_1 *swan_c1, const array_1 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 12; swan_ci++) {
    swan_equ = swan_equ && swan_eq_T_Variant_module0(
        &(*swan_c1)[swan_ci],
        &(*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif /* swan_use_array_1 */

#ifdef swan_use_array_bool_1
swan_bool swan_eq_array_bool_1(
  const array_bool_1 *swan_c1,
  const array_bool_1 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 1; swan_ci++) {
    swan_equ = swan_equ && (*swan_c1)[swan_ci] == (*swan_c2)[swan_ci];
  }
  return swan_equ;
}
#endif /* swan_use_array_bool_1 */

/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.c
*************************************************************$ */
