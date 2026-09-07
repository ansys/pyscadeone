# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Swan Code Generator mapping module.

This module provides functionality to load and query code generator mapping
data that associates Swan model items with their generated C code counterparts.
"""

from .cgmapping import CGMapping
from .code import (
    CArray,
    CEnum,
    CEnumValue,
    CExternalType,
    CFunction,
    CGlobal,
    CMacro,
    CParameter,
    CPredefinedType,
    CStruct,
    CStructField,
    CTypedef,
    CUnion,
    CUnionVariant,
)
from .model import (
    ModelArray,
    ModelConstant,
    ModelEnum,
    ModelEnumValue,
    ModelGroup,
    ModelGroupProjection,
    ModelLoopInstance,
    ModelMonoOperator,
    ModelMonoVariable,
    ModelNamedType,
    ModelOperator,
    ModelOperatorInstance,
    ModelPredefinedType,
    ModelProbe,
    ModelProbesGroup,
    ModelSensor,
    ModelSizeParameter,
    ModelStruct,
    ModelStructField,
    ModelTypeParameter,
    ModelVariable,
    ModelVariablesGroup,
    ModelVariant,
    ModelVariantConstructor,
)

__all__ = [
    "CGMapping",
    "CArray",
    "CEnum",
    "CEnumValue",
    "CExternalType",
    "CFunction",
    "CGlobal",
    "CMacro",
    "CParameter",
    "CPredefinedType",
    "CStruct",
    "CStructField",
    "CTypedef",
    "CUnion",
    "CUnionVariant",
    "ModelArray",
    "ModelConstant",
    "ModelEnum",
    "ModelEnumValue",
    "ModelGroup",
    "ModelGroupProjection",
    "ModelLoopInstance",
    "ModelMonoOperator",
    "ModelMonoVariable",
    "ModelNamedType",
    "ModelOperator",
    "ModelOperatorInstance",
    "ModelPredefinedType",
    "ModelProbe",
    "ModelProbesGroup",
    "ModelSensor",
    "ModelSizeParameter",
    "ModelStruct",
    "ModelStructField",
    "ModelTypeParameter",
    "ModelVariable",
    "ModelVariablesGroup",
    "ModelVariant",
    "ModelVariantConstructor",
]
