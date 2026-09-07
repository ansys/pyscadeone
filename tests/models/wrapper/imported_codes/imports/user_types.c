
#include "swan_types.h"
#include "user_types.h"

void MyType_init_module0(MyType_module0 * restrict swan_c1)
{
	*swan_c1 = 0;
}

swan_bool swan_eq_MyType_module0(
  const MyType_module0 *swan_c1,
  const MyType_module0 *swan_c2) 
  {
	  return (*swan_c1 == *swan_c2 ? swan_true : swan_false);
  }
