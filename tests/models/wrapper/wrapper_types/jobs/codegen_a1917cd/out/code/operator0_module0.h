/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_operator0_module0_H_
#define SWAN_operator0_module0_H_

#include "swan_types.h"

typedef struct Ctx_operator0_module0 {
  swan_int32 reg_reg_reg;
  swan_bool ini_reg_reg;
} outC_operator0_module0;

/* module0::operator0 */
extern void operator0_module0(
  /* i0 */swan_int32 i0,
  /* i1 */swan_int32 i1,
  /* i3 */floatType_TypesModule i3,
  /* i4 */tColor_module0 i4,
  /* i5 */tSize_TypesModule i5,
  /* i6 */swan_bool i6,
  /* i7 */
  const tStruct_module0 *i7,
  /* i8 */
  const arrayType_TypesModule *i8,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_int32 * restrict o1,
  /* o3 */floatType_TypesModule * restrict o3,
  /* o4 */tColor_module0 * restrict o4,
  /* o5 */tSize_TypesModule * restrict o5,
  /* o6 */swan_bool * restrict o6,
  /* o7 */tStruct_module0 * restrict o7,
  /* o8 */arrayType_TypesModule * restrict o8,
  outC_operator0_module0 * restrict outC);

#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
extern void operator0_reset_module0(outC_operator0_module0 * restrict outC);
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */

#ifndef SWAN_USER_DEFINED_INIT
extern void operator0_init_module0(outC_operator0_module0 * restrict outC);
#endif /* SWAN_USER_DEFINED_INIT */



#endif /* SWAN_operator0_module0_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** operator0_module0.h
*************************************************************$ */
