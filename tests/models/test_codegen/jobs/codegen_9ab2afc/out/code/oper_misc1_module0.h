/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0306 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_oper_misc1_module0_H_
#define SWAN_oper_misc1_module0_H_

#include "swan_types.h"
#include "oper_misc2_module0.h"

typedef struct Ctx_oper_misc1_module0 {
  swan_int32 i1_reg;
  swan_int32 o0;
} outC_oper_misc1_module0;


extern void oper_misc1_module0(
  swan_int32 i0,
  swan_int32 i1,
  outC_oper_misc1_module0 *outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void oper_misc1_reset_module0(outC_oper_misc1_module0 *outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void oper_misc1_init_module0(outC_oper_misc1_module0 *outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_oper_misc1_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0306 
** oper_misc1_module0.h
*************************************************************$ */
