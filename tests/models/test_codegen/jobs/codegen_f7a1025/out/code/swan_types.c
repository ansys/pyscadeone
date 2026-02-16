/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0777 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_types.h"

#ifdef swan_use_t_variant1_module0
swan_bool swan_eq_t_variant1_module0(
  const t_variant1_module0 *swan_c1,
  const t_variant1_module0 *swan_c2)
{
  swan_bool swan_equ;

  swan_equ = swan_c1->I.swan_tag == swan_c2->I.swan_tag;
  if (swan_equ) {
    switch (swan_c1->I.swan_tag) {
      case F :
        swan_equ = swan_equ && swan_c1->F.swan_value == swan_c2->F.swan_value;
        break;
      case I :
        swan_equ = swan_equ && swan_c1->I.swan_value == swan_c2->I.swan_value;
        break;
      default :
        /* this default branch is unreachable */
        break;
    }
  }
  return swan_equ;
}
#endif /* swan_use_t_variant1_module0 */

#ifdef swan_use_array_float32_3
swan_bool swan_eq_array_float32_3(
  const array_float32_3 *swan_c1,
  const array_float32_3 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 3; swan_ci++) {
    swan_equ = swan_equ && (*swan_c1)[swan_ci] == (*swan_c2)[swan_ci];
  }
  return swan_equ;
}
#endif /* swan_use_array_float32_3 */

#ifdef swan_use_array_1
swan_bool swan_eq_array_1(const array_1 *swan_c1, const array_1 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 2; swan_ci++) {
    swan_equ = swan_equ && swan_eq_array_2(
        &(*swan_c1)[swan_ci],
        &(*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif /* swan_use_array_1 */

#ifdef swan_use_array_2
swan_bool swan_eq_array_2(const array_2 *swan_c1, const array_2 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 3; swan_ci++) {
    swan_equ = swan_equ && swan_eq_t_array1_module0(
        &(*swan_c1)[swan_ci],
        &(*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif /* swan_use_array_2 */

#ifdef swan_use_t_array1_module0
swan_bool swan_eq_t_array1_module0(
  const t_array1_module0 *swan_c1,
  const t_array1_module0 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 4; swan_ci++) {
    swan_equ = swan_equ && swan_eq_t_struct1_module0(
        &(*swan_c1)[swan_ci],
        &(*swan_c2)[swan_ci]);
  }
  return swan_equ;
}
#endif /* swan_use_t_array1_module0 */

#ifdef swan_use_array_bool_2
swan_bool swan_eq_array_bool_2(
  const array_bool_2 *swan_c1,
  const array_bool_2 *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 2; swan_ci++) {
    swan_equ = swan_equ && (*swan_c1)[swan_ci] == (*swan_c2)[swan_ci];
  }
  return swan_equ;
}
#endif /* swan_use_array_bool_2 */

#ifdef swan_use_t_struct1_module0
swan_bool swan_eq_t_struct1_module0(
  const t_struct1_module0 *swan_c1,
  const t_struct1_module0 *swan_c2)
{
  swan_bool swan_equ;

  swan_equ = swan_true;
  swan_equ = swan_equ && swan_c1->b == swan_c2->b;
  swan_equ = swan_equ && swan_c1->a == swan_c2->a;
  return swan_equ;
}
#endif /* swan_use_t_struct1_module0 */

/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0777 - Prerelease 
** swan_types.c
*************************************************************$ */
