/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0777 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_TYPES_H_
#define SWAN_TYPES_H_

#include "swan_config.h"

/* module0::t_enum1 */
typedef enum swan_tag_t_enum1_module0 {
  /* module0::value1 */ value1,
  /* module0::value2 */ value2
} t_enum1_module0;
/* module0::t_variant1 */
typedef enum swan_kind_t_variant1_module0 {
  /* module0::F */ F,
  /* module0::I */ I
} kind_t_variant1_module0;

typedef swan_bool array_bool_2[2];

/* module0::F */
typedef struct swan_variant_F {
  kind_t_variant1_module0 swan_tag;
  swan_float32 swan_value;
} variant_F;

typedef swan_float32 array_float32_3[3];

/* module0::I */
typedef struct swan_variant_I {
  kind_t_variant1_module0 swan_tag;
  swan_int32 swan_value;
} variant_I;

/* module0::t_variant1 */
typedef union swan_union_t_variant1_module0 {
  variant_F /* module0::F */ F;
  variant_I /* module0::I */ I;
} t_variant1_module0;

/* module0::t_syn1 */
typedef swan_uint8 t_syn1_module0;

/* module0::t_struct1 */
typedef struct swan_tag_t_struct1_module0 {
  swan_int8 /* module0::a */ a;
  swan_float32 /* module0::b */ b;
} t_struct1_module0;

/* module0::t_array1 */
typedef t_struct1_module0 t_array1_module0[4];

typedef t_array1_module0 array_2[3];

typedef array_2 array_1[2];

#ifndef swan_cp_t_struct1_module0
#define swan_cp_t_struct1_module0(swan_c1, swan_c2)                           \
  (swan_assign_struct((swan_c1), (swan_c2), sizeof (t_struct1_module0)))
#endif /* swan_cp_t_struct1_module0 */

#ifndef swan_cp_array_float32_3
#define swan_cp_array_float32_3(swan_c1, swan_c2)                             \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_float32_3)))
#endif /* swan_cp_array_float32_3 */

#ifndef swan_cp_array_1
#define swan_cp_array_1(swan_c1, swan_c2)                                     \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_1)))
#endif /* swan_cp_array_1 */

#ifndef swan_cp_array_2
#define swan_cp_array_2(swan_c1, swan_c2)                                     \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_2)))
#endif /* swan_cp_array_2 */

#ifndef swan_cp_t_array1_module0
#define swan_cp_t_array1_module0(swan_c1, swan_c2)                            \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (t_array1_module0)))
#endif /* swan_cp_t_array1_module0 */

#ifndef swan_cp_array_bool_2
#define swan_cp_array_bool_2(swan_c1, swan_c2)                                \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_bool_2)))
#endif /* swan_cp_array_bool_2 */

#ifndef swan_cp_t_variant1_module0
#define swan_cp_t_variant1_module0(swan_c1, swan_c2)                          \
  (swan_assign_union((swan_c1), (swan_c2), sizeof (t_variant1_module0)))
#endif /* swan_cp_t_variant1_module0 */

#ifndef swan_eq_t_struct1_module0
extern swan_bool swan_eq_t_struct1_module0(
  const t_struct1_module0 *swan_c1,
  const t_struct1_module0 *swan_c2);
#define swan_use_t_struct1_module0
#endif /* swan_eq_t_struct1_module0 */

#ifndef swan_eq_array_float32_3
extern swan_bool swan_eq_array_float32_3(
  const array_float32_3 *swan_c1,
  const array_float32_3 *swan_c2);
#define swan_use_array_float32_3
#endif /* swan_eq_array_float32_3 */

#ifdef swan_use_array_1
#ifndef swan_eq_array_1
extern swan_bool swan_eq_array_1(
  const array_1 *swan_c1,
  const array_1 *swan_c2);
#endif /* swan_eq_array_1 */
#endif /* swan_use_array_1 */

#ifdef swan_use_array_2
#ifndef swan_eq_array_2
extern swan_bool swan_eq_array_2(
  const array_2 *swan_c1,
  const array_2 *swan_c2);
#endif /* swan_eq_array_2 */
#endif /* swan_use_array_2 */

#ifdef swan_use_t_array1_module0
#ifndef swan_eq_t_array1_module0
extern swan_bool swan_eq_t_array1_module0(
  const t_array1_module0 *swan_c1,
  const t_array1_module0 *swan_c2);
#endif /* swan_eq_t_array1_module0 */
#endif /* swan_use_t_array1_module0 */

#ifdef swan_use_array_bool_2
#ifndef swan_eq_array_bool_2
extern swan_bool swan_eq_array_bool_2(
  const array_bool_2 *swan_c1,
  const array_bool_2 *swan_c2);
#endif /* swan_eq_array_bool_2 */
#endif /* swan_use_array_bool_2 */

#ifndef swan_eq_t_variant1_module0
extern swan_bool swan_eq_t_variant1_module0(
  const t_variant1_module0 *swan_c1,
  const t_variant1_module0 *swan_c2);
#define swan_use_t_variant1_module0
#endif /* swan_eq_t_variant1_module0 */

#endif /* SWAN_TYPES_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0777 - Prerelease 
** swan_types.h
*************************************************************$ */
