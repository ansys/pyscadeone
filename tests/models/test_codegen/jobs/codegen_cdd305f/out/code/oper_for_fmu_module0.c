/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#include "swan_sensors.h"
#include "swan_consts.h"
#include "oper_for_fmu_module0.h"

/* module0::oper_for_fmu */
void oper_for_fmu_module0(
  /* i0 */swan_int32 i0,
  /* i1 */
  const array_float32_3 *i1,
  swan_int8 g1_i2,
  swan_float32 g2_i2,
  /* i3 */
  const t_struct1_module0 *i3,
  swan_int32 g1_i4,
  swan_bool g2_i4,
  swan_uint8 g3_i4,
  /* i5 */t_enum1_module0 i5,
  /* i6 */t_syn1_module0 i6,
  /* i7 */
  const t_variant1_module0 *i7,
  /* i8 */
  const array_1 *i8,
  /* o0 */swan_int32 * restrict o0,
  /* o1 */swan_float32 * restrict o1,
  /* o2 */swan_bool * restrict o2,
  swan_int8 * restrict g1_o3,
  swan_float32 * restrict g2_o3,
  /* o4 */t_struct1_module0 * restrict o4,
  /* o5 */array_bool_2 * restrict o5,
  swan_int32 * restrict g1_o6,
  swan_bool * restrict g2_o6,
  swan_uint8 * restrict g3_o6,
  /* o7 */t_enum1_module0 * restrict o7,
  /* o8 */t_syn1_module0 * restrict o8,
  /* o9 */t_variant1_module0 * restrict o9,
  /* o10 */array_1 * restrict o10)
{
  *o0 = i0;
  (*o5)[0] = i0 == swan_lit_int32(0);
  (*o5)[1] = i0 < swan_lit_int32(3);
  *o2 = (*o5)[0] || i5 == sensor_enum_module0 || swan_eq_array_float32_3(
      i1,
      (const array_float32_3 *) &sensor_array_module0) ||
    swan_eq_t_variant1_module0(
      i7,
      (const t_variant1_module0 *) &sensor_variant_module0) || i6 ==
    sensor_syn_module0 || sensor_bool_module0 || swan_eq_t_struct1_module0(
      i3,
      (const t_struct1_module0 *) &sensor_struct_module0);
  *g1_o3 = i3->a + g1_i2;
  o4->a = *g1_o3;
  *g2_o3 = g2_i2 * i3->b;
  o4->b = *g2_o3;
  *g3_o6 = g3_i4;
  *g2_o6 = g2_i4;
  *g1_o6 = g1_i4;
  *o7 = i5;
  *o8 = i6 + sensor_int_module0;
  swan_cp_t_variant1_module0(o9, i7);
  *o1 = (*i1)[0] + sensor_float_module0;
  swan_cp_array_1(o10, i8);
}



/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** oper_for_fmu_module0.c
*************************************************************$ */
