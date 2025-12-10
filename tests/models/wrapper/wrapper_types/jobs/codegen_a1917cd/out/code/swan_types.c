/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_types.h"

#ifdef swan_use_arrayType_TypesModule
swan_bool swan_eq_arrayType_TypesModule(
  const arrayType_TypesModule *swan_c1,
  const arrayType_TypesModule *swan_c2)
{
  swan_bool swan_equ;
  swan_size swan_ci;

  swan_equ = swan_true;
  for (swan_ci = 0; swan_ci < 2; swan_ci++) {
    swan_equ = swan_equ && (*swan_c1)[swan_ci] == (*swan_c2)[swan_ci];
  }
  return swan_equ;
}
#endif /* swan_use_arrayType_TypesModule */

#ifdef swan_use_tStruct_module0
swan_bool swan_eq_tStruct_module0(
  const tStruct_module0 *swan_c1,
  const tStruct_module0 *swan_c2)
{
  swan_bool swan_equ;

  swan_equ = swan_true;
  swan_equ = swan_equ && swan_c1->y == swan_c2->y;
  swan_equ = swan_equ && swan_c1->x == swan_c2->x;
  return swan_equ;
}
#endif /* swan_use_tStruct_module0 */

/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.c
*************************************************************$ */
