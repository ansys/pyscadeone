/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_TYPES_H_
#define SWAN_TYPES_H_

#include "swan_config.h"

typedef swan_int32 array_int32_2[2];

typedef array_int32_2 array_int32_2_3[3];

#ifndef swan_cp_array_int32_2_3
#define swan_cp_array_int32_2_3(swan_c1, swan_c2)                             \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_int32_2_3)))
#endif /* swan_cp_array_int32_2_3 */

#ifndef swan_cp_array_int32_2
#define swan_cp_array_int32_2(swan_c1, swan_c2)                               \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_int32_2)))
#endif /* swan_cp_array_int32_2 */

#ifdef swan_use_array_int32_2_3
#ifndef swan_eq_array_int32_2_3
extern swan_bool swan_eq_array_int32_2_3(
  const array_int32_2_3 *swan_c1,
  const array_int32_2_3 *swan_c2);
#endif /* swan_eq_array_int32_2_3 */
#endif /* swan_use_array_int32_2_3 */

#ifdef swan_use_array_int32_2
#ifndef swan_eq_array_int32_2
extern swan_bool swan_eq_array_int32_2(
  const array_int32_2 *swan_c1,
  const array_int32_2 *swan_c2);
#endif /* swan_eq_array_int32_2 */
#endif /* swan_use_array_int32_2 */

#endif /* SWAN_TYPES_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.h
*************************************************************$ */
