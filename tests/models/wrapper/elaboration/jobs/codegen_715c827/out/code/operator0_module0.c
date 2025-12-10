/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "operator0_module0.h"

/* module0::operator0 */
swan_int32 operator0_module0(/* i0 */swan_bool i0)
{
  /* variant */
  T_Variant_module0 variant;
  /* o0 */
  swan_int32 o0;

  if (i0) {
    swan_cp_T_Variant_module0(&variant, (const T_Variant_module0 *) &C1_module0[0]);
  }
  else {
    swan_cp_T_Variant_module0(&variant, (const T_Variant_module0 *) &C2_module0);
  }
  switch (variant.T_bool_box.swan_tag) {
    case T_bool_box :
      if (variant.T_bool_box.swan_value[0]) {
        o0 = swan_lit_int32(1);
      }
      else {
        o0 = swan_lit_int32(-1);
      }
      break;
    case T_int :
      o0 = variant.T_int.swan_value;
      break;
    default :
      /* this default branch is unreachable */
      break;
  }
  return o0;
}



/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** operator0_module0.c
*************************************************************$ */
