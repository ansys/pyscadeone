/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_oper_test_imp_node_module0_H_
#define SWAN_oper_test_imp_node_module0_H_

#include "swan_types.h"
#include "swan_imported_functions.h"
#include "oper_imp_node_module0.h"

typedef struct Ctx_oper_test_imp_node_module0 {
  array_int32_4 o0;
  array_int32_4 o1;
  outC_oper_imp_node_module0 Ctx_1oper_imp_node;
} outC_oper_test_imp_node_module0;


extern void oper_test_imp_node_module0(
  const array_int32_4 *i0,
  outC_oper_test_imp_node_module0 *outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void oper_test_imp_node_reset_module0(
  outC_oper_test_imp_node_module0 *outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void oper_test_imp_node_init_module0(
  outC_oper_test_imp_node_module0 *outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_oper_test_imp_node_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** oper_test_imp_node_module0.h
*************************************************************$ */
