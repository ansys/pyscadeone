#ifndef SWAN_oper_imp_node_module0_H_
#define SWAN_oper_imp_node_module0_H_

#include "swan_types.h"

typedef struct Ctx_oper_imp_node_module0 {
  array_int32_4 o1;
  swan_bool init;
} outC_oper_imp_node_module0;


extern void oper_imp_node_module0(
  const array_int32_4 *i1,
  outC_oper_imp_node_module0 *outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void oper_imp_node_reset_module0(outC_oper_imp_node_module0 *outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

extern void oper_imp_node_init_module0(outC_oper_imp_node_module0 *outC);



#endif /* SWAN_oper_imp_node_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** oper_imp_node_module0.dh
*************************************************************$ */
