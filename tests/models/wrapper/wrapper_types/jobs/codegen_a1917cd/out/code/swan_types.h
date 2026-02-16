/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** Command: swan_cg.exe config.json
*************************************************************$ */
#ifndef SWAN_TYPES_H_
#define SWAN_TYPES_H_

#include "swan_config.h"

/* TypesModule::tSize */
typedef enum swan_tag_tSize_TypesModule {
  /* TypesModule::Small */ Small,
  /* TypesModule::High */ High
} tSize_TypesModule;
/* module0::tColor */
typedef enum swan_tag_tColor_module0 {
  /* module0::GREEN */ GREEN,
  /* module0::BLUE */ BLUE,
  /* module0::ORANGE */ ORANGE,
  /* module0::RED */ RED
} tColor_module0;
/* TypesModule::floatType */
typedef swan_float32 floatType_TypesModule;

/* TypesModule::arrayType */
typedef floatType_TypesModule arrayType_TypesModule[2];

/* module0::tStruct */
typedef struct swan_tag_tStruct_module0 {
  swan_int32 /* module0::x */ x;
  swan_float32 /* module0::y */ y;
} tStruct_module0;

#ifndef swan_cp_tStruct_module0
#define swan_cp_tStruct_module0(swan_c1, swan_c2)                             \
  (swan_assign_struct((swan_c1), (swan_c2), sizeof (tStruct_module0)))
#endif /* swan_cp_tStruct_module0 */

#ifndef swan_cp_arrayType_TypesModule
#define swan_cp_arrayType_TypesModule(swan_c1, swan_c2)                       \
  (swan_assign_array((swan_c1), (swan_c2), sizeof (arrayType_TypesModule)))
#endif /* swan_cp_arrayType_TypesModule */

#ifdef swan_use_tStruct_module0
#ifndef swan_eq_tStruct_module0
extern swan_bool swan_eq_tStruct_module0(
  const tStruct_module0 *swan_c1,
  const tStruct_module0 *swan_c2);
#endif /* swan_eq_tStruct_module0 */
#endif /* swan_use_tStruct_module0 */

#ifdef swan_use_arrayType_TypesModule
#ifndef swan_eq_arrayType_TypesModule
extern swan_bool swan_eq_arrayType_TypesModule(
  const arrayType_TypesModule *swan_c1,
  const arrayType_TypesModule *swan_c2);
#endif /* swan_eq_arrayType_TypesModule */
#endif /* swan_use_arrayType_TypesModule */

#endif /* SWAN_TYPES_H_ */
/* $ Ansys Scade One - Swan Code Generator - Version 2.4.0 - Build 0622 - Prerelease 
** swan_types.h
*************************************************************$ */
