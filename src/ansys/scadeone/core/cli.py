# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
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

import argparse
from importlib import import_module
import logging
from pathlib import Path
import sys

from ansys.scadeone.core import ScadeOne, ScadeOneException, __version__
from ansys.scadeone.core.common.logger import LOGGER
from ansys.scadeone.core.common.versioning import FormatVersions
from ansys.scadeone.core.svc.fmu import FMU_2_Export

# cSpell: ignore outdir, oper


def show_formats():
    # Show supported formats: --formats option
    print(FormatVersions.get_versions())
    exit(0)


def script_command(args):
    # Scripting
    if "script" in args:
        script = Path(args.script).with_suffix("")
        args.module = script.name
        args.module_path = [str(script.parent)]

    if "module" in args:
        if "module_path" in args:
            for path in args.module_path:
                sys.path.insert(0, path)
        try:
            _ = import_module(args.module)
            exit(0)
        except Exception as e:
            print(str(e))
            exit(1)


def fmu_export_command(args):
    print(
        f"Build FMU package for job {args.job_name} under directory {args.outdir}",
        flush=True,
    )

    try:
        app = ScadeOne(args.install_dir)
        project = app.load_project(args.project)
        fmu = FMU_2_Export(project, args.job_name, args.oper_name, args.max_variables)

        outdir = f"FMU_Export_{args.kind}_{args.job_name}" if args.outdir is None else args.outdir
        if args.period is None:
            fmu.generate(args.kind, outdir)
        else:
            fmu.generate(args.kind, outdir, args.period)

        if args.build_arguments is not None:
            build_args = dict(args.build_arguments)
            if build_args.get("user_sources", "") != "":
                build_args["user_sources"] = build_args["user_sources"].split(",")
            if build_args.get("cc_opts", "") != "":
                build_args["cc_opts"] = build_args["cc_opts"].split(",")
            if build_args.get("_opts", "") != "":
                build_args["cc_opts"] = build_args["cc_opts"].split(",")
        else:
            build_args = None
        fmu.build(args.with_sources, build_args)
    except ScadeOneException as error:
        print("ERROR -", error.args[0], file=sys.stderr)


def view_sd_command(args):
    import ansys.scadeone.core.svc.simdata as sd

    if args.sd:
        sd_path = Path(args.sd)
        if not sd_path.exists():
            print(f"File not found: {sd_path}")
            sys.exit(1)
        sd_fd = sd.open_file(str(sd_path))
        print(sd_fd)
        sd_fd.close()


def main():
    """Scade One Python command line"""
    parser = argparse.ArgumentParser(
        prog="pyscadeone",
        description="Scade One Python library command line tool",
        epilog="For more information see: "
        "https://www.ansys.com/products/embedded-software/ansys-scade-one",
        fromfile_prefix_chars="@",
    )
    parser.add_argument("--version", action="version", version=__version__, help="%(prog)s version")
    parser.add_argument("--formats", action="store_true", help="Shows supported formats")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Activates verbose mode. Several occurrences increase verbosity level",
    )

    subparser = parser.add_subparsers(
        title="Sub-commands",
        help="Use: command --help for help (ex: pyscadeone fmu --help)",
        dest="subparser_command",
    )

    # Script mode command
    script_parser = subparser.add_parser("script", help="Executes given script or module")
    script_parser.add_argument("--file", help="Loads & runs script file", dest="script")
    script_parser.add_argument("--module", help="Loads & runs module")
    script_parser.add_argument(
        "--path",
        action="append",
        help="module path, inserted at beginning of sys.path." + " Several --path can be given.",
        dest="module_path",
    )
    script_parser.set_defaults(func=script_command)

    # FMU export command
    fmu_parser = subparser.add_parser("fmu", help="Generate FMU")
    fmu_parser.add_argument("project", type=Path, help="Scade One project")
    fmu_parser.add_argument("job_name", type=str, help="Generated Code job name")
    fmu_parser.add_argument(
        "-inst", "--install_dir", type=Path, help="Scade One installation directory"
    )
    fmu_parser.add_argument("-op", "--oper_name", type=str, default="", help="Root operator name")
    fmu_parser.add_argument(
        "-max",
        "--max_variables",
        type=int,
        default=1000,
        help="maximum number on FMI variables (flattened sensors, inputs and "
        "outputs) supported by the export (1000 by default).",
    )
    fmu_parser.add_argument(
        "-k",
        "--kind",
        type=str,
        default="ME",
        help="FMI kind: ‘ME’ for Model Exchange (default), ‘CS’ for Co-Simulation",
    )
    fmu_parser.add_argument(
        "-o",
        "--outdir",
        type=Path,
        help="Directory where the FMU is built (by default, 'FMU_Export_<kind>_<job_name>')",
    )
    fmu_parser.add_argument("-p", "--period", type=float, help="Execution period in seconds")
    fmu_parser.add_argument(
        "-ws", "--with_sources", action="store_true", help="Keep the sources in the FMU package"
    )
    #    fmu_parser.add_argument("-args", "--args", type=str, help="build arguments")
    fmu_parser.add_argument(
        "-args",
        "--build_arguments",
        type=str,
        action="append",
        nargs=2,
        metavar=("key", "value"),
        help=(
            """\
            Build arguments. Use one -args argument per key. Supported keys are:
            cc: compiler name (only gcc supported),
            arch: compiler architecture (only win64 supported),
            gcc_path: path on the bin directory where gcc is located,
            user_sources: list (comma separated) of user source files and directories
            (code, includes),
            cc_opts: list (comma separated) of extra compiler options,
            link_opt: list (comma separated) of extra link (dll creation) options,
            swan_config_begin: data to insert at the beginning of swan_config.h,
            swan_config_end: data to insert at the end of swan_config.h."""
        ),
    )
    fmu_parser.set_defaults(func=fmu_export_command)

    # Simulation data
    sd_parser = subparser.add_parser("simdata", help="Simulation data related command")
    sd_parser.add_argument("--show", help="Show content of a simulation data file", dest="sd")
    sd_parser.set_defaults(func=view_sd_command)

    # Parsing
    args = parser.parse_args()

    if args.verbosity > 0:
        if args.verbosity == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
        for handler in LOGGER.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.setLevel(level)

    LOGGER.debug(f"Running pyscadeone command line with: {args}")

    if args.formats:
        show_formats()

    if args.subparser_command:
        args.func(args)


if __name__ == "__main__":
    main()
