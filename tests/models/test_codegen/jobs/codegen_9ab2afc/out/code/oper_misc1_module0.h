/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_oper_misc1_module0_H_
#define SWAN_oper_misc1_module0_H_

#include "swan_types.h"

typedef struct swan_tag_outC_oper_misc1_module0 {
  swan_int32 i1_reg;
} outC_oper_misc1_module0;

/* module0::oper_misc1 */
extern void oper_misc1_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_int32 i1,
  /* o0 */swan_int32 * restrict o0,
  outC_oper_misc1_module0 * restrict outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void oper_misc1_reset_module0(outC_oper_misc1_module0 * restrict outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void oper_misc1_init_module0(outC_oper_misc1_module0 * restrict outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_oper_misc1_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** oper_misc1_module0.h
*************************************************************$ */
