#ifndef USER_TYPES_H_
#define USER_TYPES_H_

typedef swan_int8 MyType_module0;

extern void MyType_init_module0(MyType_module0 * restrict swan_c1);

#define swan_cp_MyType_module0(swan_c1, swan_c2)                              \
  (swan_assign((swan_c1), (swan_c2), sizeof (MyType_module0)))

extern swan_bool swan_eq_MyType_module0(
  const MyType_module0 *swan_c1,
  const MyType_module0 *swan_c2);

#endif /* USER_TYPES_H_ */
