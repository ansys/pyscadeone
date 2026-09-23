/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "oper_imp_func_module0.h"
#include "oper_test_imp_node_module0.h"

/* module0::oper_test_imp_node */
void oper_test_imp_node_module0(
  /* i0 */
  const array_i32_4 *i0,
  /* o0 */array_i32_4 * restrict o0,
  /* o1 */array_i32_4 * restrict o1,
  outC_oper_test_imp_node_module0 * restrict outC)
{
  /* #1: */ oper_imp_func_module0(i0, o0);
  /* #5: */ oper_imp_node_module0(i0, o1, &outC->Ctx_oper_imp_node1);
}

#ifndef SWAN_USER_DEFINED_INIT
void oper_test_imp_node_init_module0(
  outC_oper_test_imp_node_module0 * restrict outC)
{
  /* #5: */ oper_imp_node_init_module0(&outC->Ctx_oper_imp_node1);
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void oper_test_imp_node_reset_module0(
  outC_oper_test_imp_node_module0 * restrict outC)
{
  /* #5: */ oper_imp_node_reset_module0(&outC->Ctx_oper_imp_node1);
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** oper_test_imp_node_module0.c
*************************************************************$ */
