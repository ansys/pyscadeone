/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0987 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "node0_module0.h"

/* module0::node0 */
void node0_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_float32 i1,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_float32 * restrict o1,
  outC_node0_module0 * restrict outC)
{
  swan_int32 tmp1;

  tmp1 = (swan_int32) i1;
  if (outC->ini_reg) {
    outC->o0_reg = i0;
    outC->ini_reg = swan_false;
  }
  *o0 = tmp1 + outC->o0_reg;
  *o1 = (swan_float32) (tmp1 - outC->o0_reg);
  outC->o0_reg = *o0;
}

#ifndef SWAN_USER_DEFINED_INIT
void node0_init_module0(outC_node0_module0 * restrict outC)
{
  outC->o0_reg = swan_lit_i32(0);
  outC->ini_reg = swan_true;
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void node0_reset_module0(outC_node0_module0 * restrict outC)
{
  outC->ini_reg = swan_true;
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0987 - Prerelease 
** node0_module0.c
*************************************************************$ */
