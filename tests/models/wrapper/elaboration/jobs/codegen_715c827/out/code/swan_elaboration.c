/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "swan_elaboration.h"


void swan_elaboration(void)
{
  swan_size i1;

  C1_module0[0].T_int.swan_tag = T_int;
  C1_module0[0].T_int.swan_value = swan_lit_int32(9);
  for (i1 = 1; i1 < 12; i1++) {
    swan_cp_T_Variant_module0(
      &C1_module0[i1],
      (const T_Variant_module0 *) &C1_module0[0]);
  }
  C2_module0.T_bool_box.swan_tag = T_bool_box;
  C2_module0.T_bool_box.swan_value[0] = swan_false;
}



/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_elaboration.c
*************************************************************$ */
