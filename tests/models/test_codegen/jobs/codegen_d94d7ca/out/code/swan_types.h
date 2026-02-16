/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_TYPES_H_
#define SWAN_TYPES_H_

#include "swan_config.h"

typedef swan_int32 array_int32_4[4];

#ifndef swan_cp_array_int32_4
#define swan_cp_array_int32_4(swan_c1, swan_c2)                               \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (array_int32_4)))
#endif /* swan_cp_array_int32_4 */

#ifdef swan_use_array_int32_4
#ifndef swan_eq_array_int32_4
extern swan_bool swan_eq_array_int32_4(
  const array_int32_4 *swan_c1,
  const array_int32_4 *swan_c2);
#endif /* swan_eq_array_int32_4 */
#endif /* swan_use_array_int32_4 */

#endif /* SWAN_TYPES_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** swan_types.h
*************************************************************$ */
