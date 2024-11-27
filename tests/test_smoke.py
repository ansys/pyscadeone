# %%
from pathlib import Path
from typing import cast

from ansys.scadeone.core import ProjectFile, ScadeOne


def smoke():
    app = ScadeOne()

    script_dir = Path(__file__).parents[1]
    cc_project = script_dir / "examples/models/CC/CruiseControl/CruiseControl.sproj"
    # %%
    app.load_project(cc_project)

    asset = ProjectFile(cc_project)
    CC = app.load_project(asset)

    # %%
    projects = app.projects
    assert len(projects) == 2
    assert (
        cast(ProjectFile, projects[0].storage).source  # noqa: W504
        == cast(ProjectFile, projects[1].storage).source
    )

    # %%
    model = CC.model

    import ansys.scadeone.core.swan as swan

    def op_filter(obj: swan.GlobalDeclaration):
        if isinstance(obj, swan.Operator):
            return str(obj.id) == "Regulation"
        return False

    decl = model.find_declaration(op_filter)

    # %%
    op = cast(swan.Operator, decl)
    first_input = str(next(op.inputs).id)

    assert first_input == "CruiseSpeed"
    assert model.all_modules_loaded == False

    # %%
    def type_filter(obj: swan.GlobalDeclaration):
        return isinstance(obj, swan.TypeDeclarations)

    types = model.filter_declarations(type_filter)
    count = len(list(types))

    assert count == 5

    type_list = list(t.get_full_path() for t in model.types)

    assert "CC::tCruiseState" in type_list

    assert model.all_modules_loaded


def test_smoke(capsys):
    with capsys.disabled():
        smoke()


if __name__ == "__main__":
    # run using: python smoke_test.py
    print("Running smoke test...")
    smoke()
    print("Smoke test passed.")
