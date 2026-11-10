/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "oper_misc2_module0.h"
#include "oper_misc1_module0.h"

/* module0::oper_misc1 */
void oper_misc1_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_int32 i1,
  /* o0 */swan_int32 * restrict o0,
  outC_oper_misc1_module0 * restrict outC)
{
  *o0 = /* #2: */ oper_misc2_module0(i0) + outC->i1_reg;
  outC->i1_reg = i1;
}

#ifndef SWAN_USER_DEFINED_INIT
void oper_misc1_init_module0(outC_oper_misc1_module0 * restrict outC)
{
  outC->i1_reg = swan_lit_i32(0);
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void oper_misc1_reset_module0(outC_oper_misc1_module0 * restrict outC)
{
  outC->i1_reg = swan_lit_i32(0);
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** oper_misc1_module0.c
*************************************************************$ */
