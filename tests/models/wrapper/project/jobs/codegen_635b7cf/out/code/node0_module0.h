/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_node0_module0_H_
#define SWAN_node0_module0_H_

#include "swan_types.h"

typedef struct Ctx_node0_module0 {
  swan_int32 o0_reg_reg;
  swan_bool ini_reg_reg;
} outC_node0_module0;

/* module0::node0 */
extern void node0_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_float32 i1,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_float32 * restrict o1,
  outC_node0_module0 * restrict outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void node0_reset_module0(outC_node0_module0 * restrict outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void node0_init_module0(outC_node0_module0 * restrict outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_node0_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** node0_module0.h
*************************************************************$ */
