#include "swan_consts.h"
#include "swan_sensors.h"
#include "oper_imp_node_module0.h"


void oper_imp_node_module0(
  const array_int32_4 *i1,
  outC_oper_imp_node_module0 *outC)
{
    swan_int32 i;
    if (outC->init) {
        outC->init = swan_false;    
        swan_cp_array_int32_4(&outC->o1, i1);
    }
    else{        
        for(i=0;i<4;i++){
            outC->o1[i] = *i1[i] + 1;
        }
    }

}

void oper_imp_node_init_module0(outC_oper_imp_node_module0 *outC)
{
    int i;
    outC->init = swan_true;
    for(i=0;i<4;i++){
        outC->o1[i] = 0;
    }
}


#ifndef SWAN_NO_EXTERN_CALL_TO_RESET
void oper_imp_node_reset_module0(outC_oper_imp_node_module0 *outC)
{
      outC->init = swan_true;
}
#endif /* SWAN_NO_EXTERN_CALL_TO_RESET */



/* $ Ansys Scade One - Swan Code Generator - Version 2.2.0 - Build 0420 
** oper_imp_node_module0.dc
*************************************************************$ */
