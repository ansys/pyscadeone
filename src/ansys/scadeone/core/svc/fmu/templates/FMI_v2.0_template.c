/*************** Ansys Scade One FMI wrapper *******************
** Begin of file {{ FMI_FILE_NAME }}
****************************************************************
** Copyright (c) 2024 - 2024 ANSYS, Inc. and/or its affiliates.
** SPDX-License-Identifier: MIT
**
**
** Permission is hereby granted, free of charge, to any person obtaining a copy
** of this software and associated documentation files (the "Software"), to deal
** in the Software without restriction, including without limitation the rights
** to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
** copies of the Software, and to permit persons to whom the Software is
** furnished to do so, subject to the following conditions:
**
** The above copyright notice and this permission notice shall be included in all
** copies or substantial portions of the Software.
**
** THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
** IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
** FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
** AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
** LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
** OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
** SOFTWARE.

****************************************************************/

/* Includes */
#include <stdio.h>
#include <string.h>
#include <assert.h>
#include <float.h>

#include "swan_consts.h"
#include "swan_sensors.h"

{{ FMI_INCLUDES }}

#include "FMI/fmi2Functions.h"

#define ENSURE_USED(x) (void)(x)

/* Define SCADE context structure */
{{ FMI_DEFINE_SCADE_CONTEXT }}

/* Define FMU context structure */
typedef struct {
    fmi2String instanceName;
    fmi2String GUID;
    const fmi2CallbackFunctions *functions;
    fmi2Boolean loggingOn;
    fmi2Real initTime;
    fmi2Real currentTime;
    fmi2Real nextTime;
    fmi2Real period;
    fmi2Boolean initDone;
    {{ FMI_SCADE_CONTEXT }} *context;
} ModelInstance;

/* FMI logging */
#define TRACE_F(fmt, ...) if (comp->loggingOn) \
    comp->functions->logger(comp->functions->componentEnvironment, comp->instanceName, fmi2OK, "log", fmt, ## __VA_ARGS__)
#define WARNING_F(fmt, ...) if (comp->loggingOn) \
    comp->functions->logger(comp->functions->componentEnvironment, comp->instanceName, fmi2Warning, "warning", fmt, ## __VA_ARGS__)
#define ERROR_F(fmt, ...) if (comp->loggingOn) \
    comp->functions->logger(comp->functions->componentEnvironment, comp->instanceName, fmi2Error, "error", fmt, ## __VA_ARGS__)

#define TRACE(s) TRACE_F(s, NULL)
#define WARNING(s) WARNING_F(s, NULL)
#define ERROR(s) ERROR_F(s, NULL)

/* Debug logging */
{% if FMI_USE_DBG_LOG %}
#include "stdio.h"
#include "stdarg.h"
static FILE* m_pLogFile = NULL;
void OPEN_FMI_DBG_LOG()
{
    m_pLogFile = fopen("C:\\FMI_log.txt", "w");
}
void CLOSE_FMI_DBG_LOG()
{
    if (m_pLogFile) {
        fclose(m_pLogFile);
    }
}
void DO_FMI_DBG_LOG(const char * format, ...)
{
    va_list args;
    if (m_pLogFile) {
        va_start(args, format);
        vfprintf(m_pLogFile, format, args);
        fflush(m_pLogFile);
        va_end(args);
    }
}
{% else %}
void OPEN_FMI_DBG_LOG(){}
void CLOSE_FMI_DBG_LOG(){}
void DO_FMI_DBG_LOG(const char * format, ...){}
{% endif %}

/* Declare State Vector structure */
{{ FMI_DEFINE_STATE_VECTOR }}

/*$************ MODEL DEFINITIONS *************$*/

/* Define class name and unique id */
#define MODEL_IDENTIFIER {{ FMI_MODEL_IDENTIFIER }}
#define MODEL_GUID "{{ FMI_MODEL_GUID }}"

/* Task period setting */
#define TASK_PERIOD {{ FMI_TASK_PERIOD }} 

/* Define model size */
#define NUMBER_OF_REALS {{ FMI_NB_REALS }}
#define NUMBER_OF_INTEGERS {{ FMI_NB_INTEGERS }}
#define NUMBER_OF_BOOLEANS {{ FMI_NB_BOOLEANS }}
#define NUMBER_OF_STRINGS 0
#define NUMBER_OF_STATES 0
#define STATES {0}
#define NUMBER_OF_EVENT_INDICATORS 0

{{ FMI_GET_STATES_FUNC_DECL }}

{{ FMI_SET_STATES_FUNC_DECL }}

/* Called by fmi2Terminate and fmi2Reset */
static void terminate(ModelInstance* comp)
{
    ENSURE_USED(comp);
}

/* ---------------------------------------------------------------------------*
 * Private helpers used below to validate function arguments
 * ---------------------------------------------------------------------------*/

static fmi2Boolean nullPointer(ModelInstance* comp, const char* f, const char* arg, const void* p)
{
    if (!p) {
        DO_FMI_DBG_LOG("%s: invalid argument %s = NULL.\n", f, arg);
        ERROR_F("%s: invalid argument %s = NULL.", f, arg);
        return fmi2True;
    }
    return fmi2False;
}

static fmi2Boolean vrOutOfRange(ModelInstance* comp, const char* f, fmi2ValueReference vr, fmi2ValueReference end)
{
    if (vr >= end) {
        DO_FMI_DBG_LOG("%s: illegal value reference %u.\n", f, vr);
        ERROR_F("%s: illegal value reference %u.", f, vr);
        return fmi2True;
    }
    return fmi2False;
}

/* ---------------------------------------------------------------------------*
 * FMI functions: class methods not depending of a specific model instance
 * ---------------------------------------------------------------------------*/

const char* fmi2GetVersion()
{
    return fmi2Version;
}

const char* fmi2GetTypesPlatform()
{
    return fmi2TypesPlatform;
}

/* ---------------------------------------------------------------------------
 * FMI functions: for FMI Model Exchange 2.0 and for FMI Co-Simulation 2.0
 * logging control, setters and getters for Real, Integer, Boolean, String
 * ---------------------------------------------------------------------------*/

fmi2Status fmi2SetDebugLogging(fmi2Component c, fmi2Boolean loggingOn, size_t nCategories, const fmi2String categories[])
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(nCategories);
    ENSURE_USED(categories);
    
    DO_FMI_DBG_LOG("fmi2SetDebugLogging: loggingOn=%s\n", loggingOn ? "true" : "false");
    TRACE_F("fmi2SetDebugLogging: loggingOn=%s", loggingOn ? "true" : "false");
    
    comp->loggingOn = loggingOn;
    return fmi2OK;
}

fmi2Status fmi2SetReal(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Real value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2SetReal", "vr[]", vr) ||
         nullPointer(comp, "fmi2SetReal", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2SetReal", vr[i], NUMBER_OF_REALS)) {
            return fmi2Error;
        }
        DO_FMI_DBG_LOG("fmi2SetReal: #r%d# = %.17g\n", vr[i], value[i]);
        TRACE_F("fmi2SetReal: #r%d# = %.16g", vr[i], value[i]);
        switch (vr[i]) {
{{ FMI_SET_REAL | indent(8, true)}}
        default: break;
        }
    }
    return fmi2OK;
}

fmi2Status fmi2SetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;
    
    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2SetInteger", "vr[]", vr) ||
         nullPointer(comp, "fmi2SetInteger", "value[]", value))) {
        return fmi2Error;
    }
    
    for (i=0; i<nvr; i++) {
        if (vrOutOfRange(comp, "fmi2SetInteger", vr[i], NUMBER_OF_INTEGERS)) {
            return fmi2Error;
        }
        DO_FMI_DBG_LOG("fmi2SetInteger: #i%d# = %d\n", vr[i], value[i]);
        TRACE_F("fmi2SetInteger: #i%d# = %d", vr[i], value[i]);
        switch (vr[i]) {
{{ FMI_SET_INTEGER | indent(8, true)}}
        default: break;
        }
    }
    return fmi2OK;
}

fmi2Status fmi2SetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Boolean value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;
    
    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2SetBoolean", "vr[]", vr) ||
         nullPointer(comp, "fmi2SetBoolean", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2SetBoolean", vr[i], NUMBER_OF_BOOLEANS)) {
            return fmi2Error;
        }
        DO_FMI_DBG_LOG("fmi2SetBoolean: #b%d# = %s\n", vr[i], value[i] ? "true" : "false");
        TRACE_F("fmi2SetBoolean: #b%d# = %s", vr[i], value[i] ? "true" : "false");
        switch (vr[i]) {
{{ FMI_SET_BOOLEAN | indent(8, true)}}
        default: break;
        }
    }
    return fmi2OK;
}

fmi2Status fmi2SetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2String value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2SetString", "vr[]", vr) ||
         nullPointer(comp, "fmi2SetString", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2SetString", vr[i], NUMBER_OF_STRINGS)) {
            return fmi2Error;
        }
        DO_FMI_DBG_LOG("fmi2SetString: #s%d# = '%s'", vr[i], value[i]);
        TRACE_F("fmi2SetString: #s%d# = '%s'", vr[i], value[i]);
        if (nullPointer(comp, "fmi2SetString", "value[i]", value[i])) {
            return fmi2Error;
        }
        /* string not supported: nothing done */
    }
    return fmi2OK;
}

fmi2Status fmi2GetReal(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Real value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2GetReal", "vr[]", vr) ||
         nullPointer(comp, "fmi2GetReal", "value[]", value))) {
         return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2GetReal", vr[i], NUMBER_OF_REALS)) {
            return fmi2Error;
        }

        switch (vr[i]) {
{{ FMI_GET_REAL | indent(8, true)}}
        default: break;
        }

        DO_FMI_DBG_LOG("fmi2GetReal: #r%u# = %.16g\n", vr[i], value[i]);
        TRACE_F("fmi2GetReal: #r%u# = %.16g", vr[i], value[i]);
    }
    return fmi2OK;
}

fmi2Status fmi2GetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Integer value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2GetInteger", "vr[]", vr) ||
         nullPointer(comp, "fmi2GetInteger", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2GetInteger", vr[i], NUMBER_OF_INTEGERS)) {
           return fmi2Error;
        }

        switch (vr[i]) {
{{ FMI_GET_INTEGER | indent(8, true)}}
        default: break;
        }

        DO_FMI_DBG_LOG("fmi2GetInteger: #i%u# = %d\n", vr[i], value[i]);
        TRACE_F("fmi2GetInteger: #i%u# = %d", vr[i], value[i]);
    }
    return fmi2OK;
}

fmi2Status fmi2GetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Boolean value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2GetBoolean", "vr[]", vr) ||
         nullPointer(comp, "fmi2GetBoolean", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2GetBoolean", vr[i], NUMBER_OF_BOOLEANS)) {
            return fmi2Error;
        }
        switch (vr[i]) {
{{ FMI_GET_BOOLEAN | indent(8, true)}}
        default: break;
        }

        DO_FMI_DBG_LOG("fmi2GetBoolean: #b%u# = %s\n", vr[i], value[i]? "true" : "false");
        TRACE_F("fmi2GetBoolean: #b%u# = %s", vr[i], value[i] ? "true" : "false");
    }
    return fmi2OK;
}

fmi2Status fmi2GetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2String  value[])
{
    size_t i;
    ModelInstance* comp = (ModelInstance *)c;

    if ((nvr > 0) &&
        (nullPointer(comp, "fmi2GetString", "vr[]", vr) ||
         nullPointer(comp, "fmi2GetString", "value[]", value))) {
        return fmi2Error;
    }

    for (i = 0; i < nvr; i++) {
        if (vrOutOfRange(comp, "fmi2GetString", vr[i], NUMBER_OF_STRINGS)) {
           return fmi2Error;
        }

        /* string not supported: nothing done */

        DO_FMI_DBG_LOG("fmi2GetString: #s%u# = '%s'", vr[i], value[i]);
        TRACE_F("fmi2GetString: #s%u# = '%s'", vr[i], value[i]);
    }
    return fmi2OK;
}

fmi2Status fmi2GetFMUstate (fmi2Component c, fmi2FMUstate* FMUstate)
{
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2GetFMUstate: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2GetFMUstate", "FMUstate", FMUstate)) {
        return fmi2Error;
    }

    DO_FMI_DBG_LOG("fmi2GetFMUstate\n");
    TRACE("fmi2GetFMUstate");
    {{ FMI_GET_FMU_STATE_FUNC }}    

    return fmi2OK;
}

fmi2Status fmi2SetFMUstate (fmi2Component c, fmi2FMUstate FMUstate)
{
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2SetFMUstate: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2SetFMUstate", "FMUstate", FMUstate)) {
        return fmi2Error;
    }
    DO_FMI_DBG_LOG("fmi2SetFMUstate\n");
    TRACE("fmi2SetFMUstate");
    {{ FMI_SET_FMU_STATE_FUNC }}

    return fmi2OK;
}

fmi2Status fmi2FreeFMUstate(fmi2Component c, fmi2FMUstate* FMUstate)
{
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2FreeFMUstate: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2FreeFMUstate", "FMUstate", FMUstate)) {
        return fmi2Error;
    }

    DO_FMI_DBG_LOG("fmi2FreeFMUstate\n");
    TRACE("fmi2FreeFMUstate");   
    if (*FMUstate != NULL) {
        comp->functions->freeMemory(*FMUstate);
        *FMUstate = NULL;
    }
    
    return fmi2OK;
}

fmi2Status fmi2SerializedFMUstateSize(fmi2Component c, fmi2FMUstate FMUstate, size_t *size)
{
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2SerializedFMUstateSize: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2SerializedFMUstateSize", "FMUstate", FMUstate)) {
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2SerializedFMUstateSize", "size", size)) {
        return fmi2Error;   
    }
    
    DO_FMI_DBG_LOG("fmi2SerializedFMUstateSize\n");
    TRACE("fmi2SerializedFMUstateSize");
    *size = STATE_VECTOR_SIZE;
    
    return fmi2OK;
}

#ifndef wu_serialize_states_{{ FMI_ROOT_OP_NAME }}
#define wu_serialize_states_{{ FMI_ROOT_OP_NAME }}(state_D, state_S, state_sz) (memcpy((state_D), (state_S), (state_sz)))
#endif /* wu_serialize_states_{{ FMI_ROOT_OP_NAME }} */

fmi2Status fmi2SerializeFMUstate(fmi2Component c, fmi2FMUstate FMUstate, fmi2Byte serializedState[], size_t size)
{
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2SerializeFMUstate: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2SerializeFMUstate", "FMUstate", FMUstate)) {
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2SerializeFMUstate", "serializedState", serializedState)) {
        return fmi2Error;   
    }

    DO_FMI_DBG_LOG("fmi2SerializeFMUstate\n");
    TRACE("fmi2SerializeFMUstate");   
    if (size != STATE_VECTOR_SIZE) {
        ERROR_F("fmi2SerializeFMUstate: Invalid input FMUstate size %d in regarding the internal size %d", size, STATE_VECTOR_SIZE);
        return fmi2Error;
    }
    wu_serialize_states_{{ FMI_ROOT_OP_NAME }}(serializedState, FMUstate, size);
    
    return fmi2OK;
}

#ifndef wu_deserialize_states_{{ FMI_ROOT_OP_NAME }}
#define wu_deserialize_states_{{ FMI_ROOT_OP_NAME }}(state_D, state_S, state_sz) (memcpy((state_D), (state_S), (state_sz)))
#endif /* wu_deserialize_states_{{ FMI_ROOT_OP_NAME }} */

fmi2Status fmi2DeSerializeFMUstate(fmi2Component c, const fmi2Byte serializedState[], size_t size,
                                    fmi2FMUstate* FMUstate)
{    
    ModelInstance* comp = (ModelInstance*)c;
    if (STATE_VECTOR_SIZE == 0) {
        ERROR("fmi2DeSerializeFMUstate: function is not enabled.");
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2DeSerializeFMUstate", "serializedState", serializedState)) {
        return fmi2Error;
    }
    if (nullPointer(comp, "fmi2DeSerializeFMUstate", "FMUstate", FMUstate)) {
        return fmi2Error;
    }

    DO_FMI_DBG_LOG("fmi2DeSerializeFMUstate\n");
    TRACE("fmi2DeSerializeFMUstate");
    if (size != STATE_VECTOR_SIZE) {
        ERROR_F("fmi2DeSerializeFMUstate: Invalid input FMUstate size %d in regarding the internal size %d", size, STATE_VECTOR_SIZE);
        return fmi2Error;
    }       
    if (*FMUstate == NULL) {
        *FMUstate = (fmi2FMUstate)comp->functions->allocateMemory(1, STATE_VECTOR_SIZE);
    }   
    wu_deserialize_states_{{ FMI_ROOT_OP_NAME }}(*FMUstate, serializedState, size); 

    return fmi2OK;
}

fmi2Status fmi2GetDirectionalDerivative(fmi2Component c, const fmi2ValueReference vUnknown_ref[], size_t nUnknown,
                                        const fmi2ValueReference vKnown_ref[] , size_t nKnown,
                                        const fmi2Real dvKnown[], fmi2Real dvUnknown[])
{
    ModelInstance* comp = (ModelInstance *)c;
    
    DO_FMI_DBG_LOG("fmi2GetDirectionalDerivative\n");
    TRACE("fmi2GetDirectionalDerivative");
    
    ENSURE_USED(vUnknown_ref);
    ENSURE_USED(nUnknown);
    ENSURE_USED(vKnown_ref);
    ENSURE_USED(nKnown);
    ENSURE_USED(dvKnown);
    ENSURE_USED(dvUnknown);
    return fmi2OK;
}


/* ---------------------------------------------------------------------------
 * FMI functions
 * ---------------------------------------------------------------------------*/

fmi2Component fmi2Instantiate(fmi2String instanceName, fmi2Type fmuType, fmi2String GUID,
                            fmi2String fmuResourceLocation, const fmi2CallbackFunctions *functions,
                            fmi2Boolean visible, fmi2Boolean loggingOn)
{
    ModelInstance* comp;
    ENSURE_USED(fmuResourceLocation);
    ENSURE_USED(visible);
    
    OPEN_FMI_DBG_LOG();
    DO_FMI_DBG_LOG("fmi2Instantiate: GUID=%s\n", GUID);

    if (!functions->logger) 
        return NULL;
    if (!functions->allocateMemory || !functions->freeMemory) {
        functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "error", "fmi2Instantiate: missing callback function.");
        return NULL;
    }
    if (!instanceName || !(*instanceName)) {
        functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "error", "fmi2Instantiate: missing instance name.");
        return NULL;
    }
    if (strcmp(GUID, MODEL_GUID)) {
        functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "error", "fmi2Instantiate: wrong GUID %s. Expected %s.", GUID, MODEL_GUID);
        return NULL;
    }
    comp = (ModelInstance *)functions->allocateMemory(1, sizeof(ModelInstance));
    if (!comp) {
        functions->logger(functions->componentEnvironment, instanceName, fmi2Error, "error", "fmi2Instantiate: out of memory.");
        return NULL;
    }
    /* Allocate KCG context */
    comp->context = (void*)functions->allocateMemory(1, {{ FMI_SCADE_CONTEXT_SIZE }});
    comp->instanceName = (fmi2String)functions->allocateMemory(strlen(instanceName)+1, sizeof(char));
    strcpy((char*)comp->instanceName, instanceName);
    comp->GUID = (fmi2String)functions->allocateMemory(strlen(GUID)+1, sizeof(char));
    strcpy((char*)comp->GUID, GUID);
    comp->functions = functions;
    comp->loggingOn = loggingOn;
    comp->initTime = 0.0;
    comp->currentTime = 0.0;
    comp->nextTime = 0.0;
    comp->initDone = fmi2False;
    TRACE_F("fmi2Instantiate: GUID=%s", GUID);

    /* Set KCG context variables to clean initial values */
{{ FMI_INIT_VALUES | indent(4, true) }}

    return comp;
}

fmi2Status fmi2SetupExperiment(fmi2Component c, fmi2Boolean toleranceDefined, fmi2Real tolerance,
                            fmi2Real startTime, fmi2Boolean stopTimeDefined, fmi2Real stopTime)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2SetupExperiment startTime=%.17g, stopTimeDefined=%s, stopTime=%.17g\n", startTime, stopTimeDefined ? "true" : "false", stopTime);
    TRACE_F("fmi2SetupExperiment: startTime=%.17g, stopTimeDefined=%s, stopTime=%.17g", startTime, stopTimeDefined ? "true" : "false", stopTime);

    comp->initTime = startTime;
    comp->nextTime = startTime;
    return fmi2OK;
}

fmi2Status fmi2EnterInitializationMode(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2EnterInitializationMode\n");
    TRACE("fmi2EnterInitializationMode");
 
    return fmi2OK;
}

fmi2Status fmi2ExitInitializationMode(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2ExitInitializationMode\n");
    TRACE("fmi2ExitInitializationMode");

    return fmi2OK;
}

fmi2Status fmi2Terminate(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;
    
    DO_FMI_DBG_LOG("fmi2Terminate\n");
    TRACE("fmi2Terminate");
    
    terminate(comp);
    return fmi2OK;
}

fmi2Status fmi2Reset(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2Reset\n");
    TRACE("fmi2Reset");
    
    // Stop scenario recording & SCADE co-simulation
    terminate(comp);
    // Force reinitialization at next eventUpdate()/doStep()
    comp->initDone = fmi2False; 
    return fmi2OK;
}

void fmi2FreeInstance(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2FreeInstance\n");
    TRACE("fmi2FreeInstance");

    if (comp != NULL) {
        if (comp->context) {
            comp->functions->freeMemory(comp->context);
        }
        comp->functions->freeMemory((char*)comp->instanceName);
        comp->functions->freeMemory((char*)comp->GUID);
        comp->functions->freeMemory(comp);
    }

    CLOSE_FMI_DBG_LOG();
}

{% if FMI_KIND_CS %}
// ---------------------------------------------------------------------------
// FMI functions: only for Co-Simulation 2.0
// ---------------------------------------------------------------------------

/* Simulating the slave */
fmi2Status fmi2SetRealInputDerivatives(fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
                                     const fmi2Integer order[], const fmi2Real value[])
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(vr);
    ENSURE_USED(order);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2SetRealInputDerivatives: nvr=%u\n", nvr);
    TRACE("fmi2SetRealInputDerivatives");

    if (nvr!=0) {
        ERROR("This model cannot interpolate inputs");
        return fmi2Error;
    }
    return fmi2OK;
}

fmi2Status fmi2GetRealOutputDerivatives(fmi2Component c, const fmi2ValueReference vr[], size_t nvr,
                                      const fmi2Integer order[], fmi2Real value[])
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(vr);
    ENSURE_USED(order);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2GetRealOutputDerivatives: nvr=%u\n", nvr);
    TRACE("fmi2GetRealOutputDerivatives");

    if (nvr!=0) {
        ERROR("This model cannot compute derivatives of outputs");
        return fmi2Error;
    }
    return fmi2OK;
}

fmi2Status fmi2DoStep(fmi2Component c, fmi2Real time, fmi2Real step, fmi2Boolean newStep)
{
    ModelInstance *comp = (ModelInstance *)c;
    fmi2Real finalTime = time + step;

    DO_FMI_DBG_LOG("fmi2DoStep: time=%.17g step=%.17g newStep=%s\n", time, step, newStep ? "true" : "false");
    TRACE_F("fmi2DoStep: time=%.17g step=%.17g newStep=%s", time, step, newStep?"true":"false");

    /*if (newStep == fmi2False) {
        ERROR("This FMU does not support rollbacks.");
        return fmi2Error;
    }*/

    /* check period first */
    if (comp->period < 1e-8) {
        comp->period = TASK_PERIOD;
    }
    if (!comp->initDone) {
        DO_FMI_DBG_LOG("First step => SCADE initialization\n");
        /* Perform initialization at beginning */
{{ FMI_INIT_CONTEXT }}
        comp->initDone = fmi2True;
    }
    if (comp->nextTime >= finalTime + 100 * DBL_EPSILON) {
        DO_FMI_DBG_LOG("** nextTime=%.17g, finalTime=%.17g => no SCADE cycle\n", comp->nextTime, finalTime);
    }
    else {
        while (comp->nextTime < finalTime + 100 * DBL_EPSILON) {
            DO_FMI_DBG_LOG("nextTime=%.17g, finalTime=%.17g => SCADE cycle\n", comp->nextTime, finalTime);
            /* Executing SCADE cycle */
{{ FMI_CALL_CYCLE | indent(12, true) }}
            comp->nextTime += comp->period;
        }
    }

    return fmi2OK;
}

fmi2Status fmi2CancelStep(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2CancelStep\n");
    ERROR("fmi2CancelStep should not be called as fmi2DoStep never returns fmiPending");

    return fmi2Error;
}

fmi2Status fmi2GetStatus(fmi2Component c, const fmi2StatusKind s, fmi2Status* value)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(s);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2GetStatus\n");
    ERROR("fmi2GetStatus: this function should not be called as fmiDoStep never returns fmiPending");

    return fmi2Error;
}

fmi2Status fmi2GetRealStatus(fmi2Component c, const fmi2StatusKind s, fmi2Real* value)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(s);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2GetRealStatus\n");
    ERROR("fmi2GetRealStatus: this function should not be called as fmiDoStep never returns fmiPending");

    return fmi2Error;
}

fmi2Status fmi2GetIntegerStatus(fmi2Component c, const fmi2StatusKind s, fmi2Integer* value)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(s);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2GetIntegerStatus\n");
    ERROR("fmi2GetIntegerStatus: this function should not be called as fmiDoStep never returns fmiPending");

    return fmi2Error;
}

fmi2Status fmi2GetBooleanStatus(fmi2Component c, const fmi2StatusKind s, fmi2Boolean* value)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2GetBooleanStatus\n");

    if (s == fmi2Terminated) {
        TRACE("fmi2GetBooleanStatus");
        *value = fmi2False;
        return fmi2OK;
    } else {
        ERROR("fmi2GetBooleanStatus: this function should not be called as fmiDoStep never returns fmiPending");
    }
    return fmi2Error;
}

FMI2_Export fmi2Status fmi2GetStringStatus(fmi2Component c, const fmi2StatusKind s, fmi2String*  value)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(s);
    ENSURE_USED(value);

    DO_FMI_DBG_LOG("fmi2GetStringStatus\n");
    ERROR("fmi2GetStringStatus: this function should not be called as fmiDoStep never returns fmiPending");

    return fmi2Error;
}

{% else %}
// ---------------------------------------------------------------------------
// FMI functions: only for Model Exchange 2.0
// ---------------------------------------------------------------------------

fmi2Status fmi2EnterEventMode(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2EnterEventMode\n");
    TRACE("fmi2EnterEventMode");

    return fmi2OK;
}

fmi2Status fmi2NewDiscreteStates(fmi2Component c, fmi2EventInfo* eventInfo)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2NewDiscreteStates: currentTime=%.17g, nextEventTime=%.17g\n", comp->currentTime, eventInfo->nextEventTime);
    TRACE_F("fmi2NewDiscreteStates: currentTime=%.17g, nextEventTime=%.17g", comp->currentTime, eventInfo->nextEventTime);

    if (nullPointer(comp, "fmi2NewDiscreteStates", "eventInfo", eventInfo)) {
        return fmi2Error;
    }
    eventInfo->newDiscreteStatesNeeded = fmi2False;
    eventInfo->nominalsOfContinuousStatesChanged = fmi2False;
    eventInfo->valuesOfContinuousStatesChanged = fmi2False;
    eventInfo->terminateSimulation = fmi2False;
    eventInfo->nextEventTimeDefined = fmi2False;
    
    /* check period first */
    if (comp->period < 1e-8) {
        comp->period = TASK_PERIOD;
    }
    if (!comp->initDone) {
        DO_FMI_DBG_LOG("Fist step => SCADE initialization\n");
        /* Perform initialization at beginning */
{{ FMI_INIT_CONTEXT }}
        comp->initDone = fmi2True;
    } 
    if (comp->nextTime <= comp->currentTime + 100 * DBL_EPSILON) {
        DO_FMI_DBG_LOG("SCADE cycle\n", comp->nextTime, comp->currentTime);
        /* Executing SCADE cycle */
{{ FMI_CALL_CYCLE | indent(8, true) }}
        comp->nextTime = comp->nextTime + comp->period;
    } 
    else {
        DO_FMI_DBG_LOG("**Period not elapsed => no SCADE cycle\n");
    }

    /* Set delay for next cycle */
    eventInfo->nextEventTimeDefined = fmi2True;
    eventInfo->nextEventTime        = comp->nextTime;
    
    return fmi2OK;
}

fmi2Status fmi2EnterContinuousTimeMode(fmi2Component c)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2EnterContinuousTimeMode\n");
    TRACE("fmi2EnterContinuousTimeMode");

    return fmi2OK;
}

fmi2Status fmi2CompletedIntegratorStep(fmi2Component c, fmi2Boolean noSetFMUStatePriorToCurrentPoint,
                                     fmi2Boolean *enterEventMode, fmi2Boolean *terminateSimulation)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(noSetFMUStatePriorToCurrentPoint);

    DO_FMI_DBG_LOG("fmi2CompletedIntegratorStep\n");
    TRACE("fmi2CompletedIntegratorStep");

    *enterEventMode = fmi2False;
    *terminateSimulation = fmi2False;
    return fmi2OK;
}

fmi2Status fmi2SetTime(fmi2Component c, fmi2Real time)
{
    ModelInstance* comp = (ModelInstance *)c;

    DO_FMI_DBG_LOG("fmi2SetTime: time=%.17g\n", time);
    TRACE_F("fmi2SetTime: time=%.17g", time);

    comp->currentTime = time;
    return fmi2OK;
}

fmi2Status fmi2SetContinuousStates(fmi2Component c, const fmi2Real x[], size_t nx)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(x);

    DO_FMI_DBG_LOG("fmi2SetContinuousStates: nx=%u\n", nx);
    TRACE("fmi2SetContinuousStates");

    if (nx!=0) {
        WARNING("fmi2SetContinuousStates: no continuous state");
    }
    return fmi2OK;
}

fmi2Status fmi2GetContinuousStates(fmi2Component c, fmi2Real states[], size_t nx)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(states);

    DO_FMI_DBG_LOG("fmi2GetContinuousStates: nx=%u\n", nx);
    TRACE("fmi2GetContinuousStates");

    if (nx!=0) {
        WARNING("fmi2GetContinuousStates: no continuous state");
    }
    return fmi2OK;
}

fmi2Status fmi2GetNominalsOfContinuousStates(fmi2Component c, fmi2Real x_nominal[], size_t nx)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(x_nominal);

    DO_FMI_DBG_LOG("fmi2GetNominalsOfContinuousStates: nx=%u\n", nx);
    TRACE("fmi2GetNominalsOfContinuousStates");

    if (nx!=0) {
        WARNING("fmi2GetNominalsOfContinuousStates: no continuous state");
    }
    return fmi2OK;
}

fmi2Status fmi2GetDerivatives(fmi2Component c, fmi2Real derivatives[], size_t nx)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(derivatives);
 
    DO_FMI_DBG_LOG("fmi2GetDerivatives: nx=%u\n", nx);
    TRACE("fmi2GetDerivatives");

    if (nx!=0) {
        WARNING("fmi2GetDerivatives: no derivatives");
    }
    return fmi2OK;
}

fmi2Status fmi2GetEventIndicators(fmi2Component c, fmi2Real eventIndicators[], size_t ni)
{
    ModelInstance* comp = (ModelInstance *)c;
    ENSURE_USED(eventIndicators);

    DO_FMI_DBG_LOG("fmi2GetEventIndicators: ni=%u\n", ni);
    TRACE("fmi2GetEventIndicators");

    if (ni!=0) {
        WARNING("fmi2GetEventIndicators: no event indicators");
    }
    return fmi2OK;
}
{% endif %}

/******************* Ansys Scade One FMI wrapper ***************
** End of file {{ FMI_FILE_NAME }}
****************************************************************/
