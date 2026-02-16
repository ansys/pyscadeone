/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_test_node_module0_H_
#define SWAN_test_node_module0_H_

#include "operator0_module0.h"

typedef struct Ctx_test_node_module0 {
  outC_operator0_module0 /* #0: */ Ctx_operator01;
} outC_test_node_module0;

/* module0::test_node */
extern void test_node_module0(
  /* i0 */
  const array_int32_4 *i0,
  /* o0 */array_int32_4 * restrict o0,
  outC_test_node_module0 * restrict outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void test_node_reset_module0(outC_test_node_module0 * restrict outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void test_node_init_module0(outC_test_node_module0 * restrict outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_test_node_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** test_node_module0.h
*************************************************************$ */
