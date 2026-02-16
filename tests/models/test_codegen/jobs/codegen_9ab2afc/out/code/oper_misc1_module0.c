/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0306 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_consts.h"
#include "swan_sensors.h"
#include "oper_misc1_module0.h"


void oper_misc1_module0(
  swan_int32 i0,
  swan_int32 i1,
  outC_oper_misc1_module0 *outC)
{
  swan_int32 tmp;

  tmp = oper_misc2_module0(i0);
  outC->o0 = tmp + outC->i1_reg;
  outC->i1_reg = i1;
}

#ifndef SWAN_USER_DEFINED_INIT
void oper_misc1_init_module0(outC_oper_misc1_module0 *outC)
{
  outC->o0 = swan_lit_int32(0);
  outC->i1_reg = swan_lit_int32(0);
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void oper_misc1_reset_module0(outC_oper_misc1_module0 *outC)
{
  outC->i1_reg = swan_lit_int32(0);
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */



/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0306 
** oper_misc1_module0.c
*************************************************************$ */
