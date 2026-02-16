/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_consts.h"
#include "swan_sensors.h"
#include "oper_test_imp_node_module0.h"


void oper_test_imp_node_module0(
  const array_int32_4 *i0,
  outC_oper_test_imp_node_module0 *outC)
{
  oper_imp_node_module0(i0, &outC->Ctx_1oper_imp_node);
  swan_cp_array_int32_4(
    &outC->o1,
    (const array_int32_4 *) &outC->Ctx_1oper_imp_node.o1);
  oper_imp_func_module0(i0, &outC->o0);
}

#ifndef SWAN_USER_DEFINED_INIT
void oper_test_imp_node_init_module0(outC_oper_test_imp_node_module0 *outC)
{
  swan_size idx1;
  swan_size idx;

  for (idx = 0; idx < 4; idx++) {
    outC->o1[idx] = swan_lit_int32(0);
  }
  for (idx1 = 0; idx1 < 4; idx1++) {
    outC->o0[idx1] = swan_lit_int32(0);
  }
  oper_imp_node_init_module0(&outC->Ctx_1oper_imp_node);
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void oper_test_imp_node_reset_module0(outC_oper_test_imp_node_module0 *outC)
{
  oper_imp_node_reset_module0(&outC->Ctx_1oper_imp_node);
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */



/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** oper_test_imp_node_module0.c
*************************************************************$ */
