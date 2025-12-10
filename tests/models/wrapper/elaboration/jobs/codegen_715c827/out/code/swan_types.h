/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_TYPES_H_
#define SWAN_TYPES_H_

#include "swan_config.h"

/* module0::T_Variant */
typedef enum swan_kind_T_Variant_module0 {
  /* module0::T_int */ T_int,
  /* module0::T_bool_box */ T_bool_box
} kind_T_Variant_module0;

typedef swan_bool array_bool_1[1];

/* module0::T_bool_box */
typedef struct swan_variant_T_bool_box {
  kind_T_Variant_module0 swan_tag;
  array_bool_1 swan_value;
} variant_T_bool_box;

/* module0::T_int */
typedef struct swan_variant_T_int {
  kind_T_Variant_module0 swan_tag;
  swan_int32 swan_value;
} variant_T_int;

/* module0::T_Variant */
typedef union swan_union_T_Variant_module0 {
  variant_T_int /* module0::T_int */ T_int;
  variant_T_bool_box /* module0::T_bool_box */ T_bool_box;
} T_Variant_module0;

typedef T_Variant_module0 array_1[12];

#ifndef swan_cp_array_1
#define swan_cp_array_1(swan_c1, swan_c2)                                     \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_1)))
#endif /* swan_cp_array_1 */

#ifndef swan_cp_array_bool_1
#define swan_cp_array_bool_1(swan_c1, swan_c2)                                \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_bool_1)))
#endif /* swan_cp_array_bool_1 */

#ifndef swan_cp_T_Variant_module0
#define swan_cp_T_Variant_module0(swan_c1, swan_c2)                           \
  (swan_assign_union((swan_c1), (swan_c2), sizeof (T_Variant_module0)))
#endif /* swan_cp_T_Variant_module0 */

#ifdef swan_use_array_1
#ifndef swan_eq_array_1
extern swan_bool swan_eq_array_1(
  const array_1 *swan_c1,
  const array_1 *swan_c2);
#endif /* swan_eq_array_1 */
#endif /* swan_use_array_1 */

#ifdef swan_use_array_bool_1
#ifndef swan_eq_array_bool_1
extern swan_bool swan_eq_array_bool_1(
  const array_bool_1 *swan_c1,
  const array_bool_1 *swan_c2);
#endif /* swan_eq_array_bool_1 */
#endif /* swan_use_array_bool_1 */

#ifdef swan_use_T_Variant_module0
#ifndef swan_eq_T_Variant_module0
extern swan_bool swan_eq_T_Variant_module0(
  const T_Variant_module0 *swan_c1,
  const T_Variant_module0 *swan_c2);
#endif /* swan_eq_T_Variant_module0 */
#endif /* swan_use_T_Variant_module0 */

#endif /* SWAN_TYPES_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.h
*************************************************************$ */
