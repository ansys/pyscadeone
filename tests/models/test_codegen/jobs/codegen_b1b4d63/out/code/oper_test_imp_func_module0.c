/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0351 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_imported_functions.h"
#include "swan_sensors.h"
#include "swan_consts.h"
#include "oper_test_imp_func_module0.h"

/* module0::oper_test_imp_func */
void oper_test_imp_func_module0(
  /* i0 */
  const array_int32_4 *i0,
  /* o0 */array_int32_4 * restrict o0,
  /* o1 */array_int32_4 * restrict o1,
  /* o2 */array_int32_4 * restrict o2)
{
  /* #1: */ oper_imp_func_module0(i0, o0);
  /* #5: */ link_obj_module0(i0, o1);
  /* #8: */ static_lib_module0(i0, o2);
}



/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0351 - Prerelease 
** oper_test_imp_func_module0.c
*************************************************************$ */
