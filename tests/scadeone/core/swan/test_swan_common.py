# Copyright (C) 2024 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
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

from pathlib import Path

import pytest

from ansys.scadeone.core import ScadeOne
from ansys.scadeone.core.model import Model
from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, OwnerProperty, Owner
import ansys.scadeone.core.swan as swan


@pytest.fixture
def cc_model(cc_project):
    app = ScadeOne()
    rsc_dir = Path(__file__).parents[4]
    project = rsc_dir / cc_project
    project = app.load_project(project)
    model = project.model
    model.load_all_modules()
    return model


def ownership_model():
    app = ScadeOne()
    rsc_dir = Path(__file__).parents[4]
    project = rsc_dir / "tests/models/ownership/test_ownership.sproj"
    project = app.load_project(project)
    model = project.model
    model.load_all_modules()
    return model


class OwnershipVisitor(SwanVisitor):
    def __init__(self):
        super().__init__()
        self.missing_owner = []

    def visit_SwanItem(self, swan_obj: swan.SwanItem, owner: Owner, owner_property: OwnerProperty):
        if not swan_obj.owner:
            self.missing_owner.append(swan_obj)


@pytest.mark.skip(
    reason="This test is not working because it needs to migrate to swan version 2027"
)
class Test:
    @staticmethod
    def test_ownership_on_cc_example(cc_model):
        Test._test_ownership(cc_model)

    @staticmethod
    def test_ownership_on_test_model():
        # TODO: Check line 115 in module0.swan ('when case' and 'default' were removed)
        test_model = ownership_model()
        Test._test_ownership(test_model)

    @staticmethod
    def _test_ownership(model: Model):
        visitor = OwnershipVisitor()
        for item in model.all_modules:
            visitor.visit(item)

        assert not visitor.missing_owner  ## must stay empty
