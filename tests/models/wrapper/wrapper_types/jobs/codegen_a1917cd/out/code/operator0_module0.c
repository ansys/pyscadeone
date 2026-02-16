/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "operator0_module0.h"

/* module0::operator0 */
void operator0_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_int32 i1,
  /* i3 */floatType_TypesModule i3,
  /* i4 */tColor_module0 i4,
  /* i5 */tSize_TypesModule i5,
  /* i6 */swan_bool i6,
  /* i7 */
  const tStruct_module0 *i7,
  /* i8 */
  const arrayType_TypesModule *i8,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_int32 * restrict o1,
  /* o3 */floatType_TypesModule * restrict o3,
  /* o4 */tColor_module0 * restrict o4,
  /* o5 */tSize_TypesModule * restrict o5,
  /* o6 */swan_bool * restrict o6,
  /* o7 */tStruct_module0 * restrict o7,
  /* o8 */arrayType_TypesModule * restrict o8,
  outC_operator0_module0 * restrict outC)
{
  *o3 = i3;
  *o4 = i4;
  *o5 = i5;
  *o6 = i6;
  swan_cp_tStruct_module0(o7, i7);
  swan_cp_arrayType_TypesModule(o8, i8);
  if (outC->ini_reg_reg) {
    outC->reg_reg_reg = i0;
  }
  if (outC->ini_reg_reg) {
    outC->ini_reg_reg = swan_false;
  }
  *o0 = outC->reg_reg_reg;
  *o1 = i1 - outC->reg_reg_reg;
  outC->reg_reg_reg = i1 + outC->reg_reg_reg;
}

#ifndef SWAN_USER_DEFINED_INIT
void operator0_init_module0(outC_operator0_module0 * restrict outC)
{
  outC->reg_reg_reg = swan_lit_int32(0);
  outC->ini_reg_reg = swan_true;
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void operator0_reset_module0(outC_operator0_module0 * restrict outC)
{
  outC->ini_reg_reg = swan_true;
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** operator0_module0.c
*************************************************************$ */
