/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "test_node_module0.h"

/* module0::test_node */
void test_node_module0(
  /* i0 */
  const array_int32_4 *i0,
  /* o0 */array_int32_4 * restrict o0,
  outC_test_node_module0 * restrict outC)
{
  /* #0: */ operator0_module0(i0, o0, &outC->Ctx_operator01);
}

#ifndef SWAN_USER_DEFINED_INIT
void test_node_init_module0(outC_test_node_module0 * restrict outC)
{
  /* #0: */ operator0_init_module0(&outC->Ctx_operator01);
}
#endif /* SWAN_USER_DEFINED_INIT */


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void test_node_reset_module0(outC_test_node_module0 * restrict outC)
{
  /* #0: */ operator0_reset_module0(&outC->Ctx_operator01);
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */




/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** test_node_module0.c
*************************************************************$ */
