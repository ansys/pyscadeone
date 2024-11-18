#include "swan_types.h"

void oper_imp_func_module0(const array_int32_4 *i1, array_int32_4 *o1)
{
    swan_int32 i;
    for (i=0;i<4;i++){
        *o1[i] = *i1[i] + 1;
    }
}
