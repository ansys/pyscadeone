/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "static_lib_module0.h"
#include "link_obj_module0.h"
#include "oper_imp_func_module0.h"
#include "oper_test_imp_func_module0.h"

/* module0::oper_test_imp_func */
void oper_test_imp_func_module0(
  /* i0 */
  const array_i32_4 *i0,
  /* o0 */array_i32_4 * restrict o0,
  /* o1 */array_i32_4 * restrict o1,
  /* o2 */array_i32_4 * restrict o2)
{
  /* #1: */ oper_imp_func_module0(i0, o0);
  /* #5: */ link_obj_module0(i0, o1);
  /* #8: */ static_lib_module0(i0, o2);
}



/* $ Ansys Scade One - Swan Code Generator - Version 2.5.0 - Build 0801 - Prerelease 
** oper_test_imp_func_module0.c
*************************************************************$ */
