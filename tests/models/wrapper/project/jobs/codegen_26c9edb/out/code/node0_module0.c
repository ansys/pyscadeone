/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "node0_module0.h"

/* module0::node0 */
void node0_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_float32 i1,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_float32 * restrict o1,
  outC_node0_module0 * restrict outC)
{
  if (outC->ini_reg_reg) {
    outC->o0_reg_reg = i0;
  }
  if (outC->ini_reg_reg) {
    outC->ini_reg_reg = swan_false;
  }
  *o0 = (swan_int32) i1 + outC->o0_reg_reg;
  *o1 = (swan_float32) ((swan_int32) i1 - outC->o0_reg_reg);
  outC->o0_reg_reg = *o0;
}

#ifndef SWAN_USER_DEFINED_INIT
void node0_init_module0(outC_node0_module0 * restrict outC)
{
  outC->o0_reg_reg = swan_lit_int32(0);
  outC->ini_reg_reg = swan_true;
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void node0_reset_module0(outC_node0_module0 * restrict outC)
{
  outC->ini_reg_reg = swan_true;
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** node0_module0.c
*************************************************************$ */
