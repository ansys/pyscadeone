/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_oper_test_imp_node_module0_H_
#define SWAN_oper_test_imp_node_module0_H_

#include "oper_imp_node_module0.h"

typedef struct swan_tag_outC_oper_test_imp_node_module0 {
  outC_oper_imp_node_module0 /* #5: */ Ctx_oper_imp_node1;
} outC_oper_test_imp_node_module0;

/* module0::oper_test_imp_node */
extern void oper_test_imp_node_module0(
  /* i0 */
  const array_i32_4 *i0,
  /* o0 */array_i32_4 * restrict o0,
  /* o1 */array_i32_4 * restrict o1,
  outC_oper_test_imp_node_module0 * restrict outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void oper_test_imp_node_reset_module0(
  outC_oper_test_imp_node_module0 * restrict outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void oper_test_imp_node_init_module0(
  outC_oper_test_imp_node_module0 * restrict outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_oper_test_imp_node_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** oper_test_imp_node_module0.h
*************************************************************$ */
