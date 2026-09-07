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

import argparse
from pathlib import Path
import os
import sys

from ansys.scadeone.core import ScadeOne, ScadeOneException, version_info
from ansys.scadeone.core.common.logger import LOGGER, LoggerLevel
from ansys.scadeone.core.common.versioning import FormatVersions

# cSpell: ignore outdir, oper

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[no-untyped-call]


def print_banner() -> None:
    version = f"{version_info.major}.{version_info.minor}.{version_info.patch}"
    build = f" - Build {version_info.build}" if version_info.build else ""
    build += " - Prerelease" if version_info.pre_release else ""

    banner = f"""Ansys Scade One - PyScadeOne - Version {version}{build}
Copyright © 2026-2027 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
"""
    print(banner)


def scadeone_app(args) -> ScadeOne:
    """Returns a ScadeOne application instance based on the provided arguments.

    Parameters
    ----------
    args : Namespace
        Namespace containing the command line arguments.
    Returns
    -------
    ScadeOne
        ScadeOne application instance.
    """
    install_dir = args.install_dir if args.install_dir else os.getenv("SCADE_ONE_INSTALL_DIR")
    # If install_dir is still None, ScadeOne will try to find the installation directory
    # based on the configuration file or default locations.
    return ScadeOne(install_dir)


# ========================================================================================
# PyScadeOne main options
# ========================================================================================
def main_options_parser(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="",
        help="%(prog)s version",
    )
    parser.add_argument(
        "--formats",
        action="store_true",
        help="Shows supported formats",
    )

    parser.add_argument(
        "--log",
        metavar="DIR",
        const=Path("."),
        nargs="?",
        type=Path,
        help="Directory where the log is stored (current path used if argument value not specified)",
    )

    parser.add_argument(
        "-v",
        "--verbosity",
        action="count",
        default=0,
        help="Activates verbose mode. Several occurrences increase verbosity level",
    )

    parser.add_argument(
        "--set-install-dir",
        type=Path,
        help="See https://scadeone.docs.pyansys.com/version/stable/user_guide/cli.html",
        dest="set_install_dir",
    )

    parser.add_argument(
        "--no-exit",
        action="store_true",
        help=(
            "When this option is set, cli.main() uses `return` instead of `sys.exit()`. "
            "To be used when calling cli.main() from a script to avoid exiting the Python interpreter."
        ),
        dest="no_exit",
    )


def show_formats() -> bool:
    # Show supported formats: --formats option
    print(FormatVersions.get_versions())
    return True


def set_install_dir_command(install_dir: str) -> bool:
    from ansys.scadeone.core.interfaces import IScadeOne

    try:
        config_file = ScadeOne._Tools.generate_config(install_dir)
        print(f"Configuration file:\n{config_file}\nContent:")
        print(config_file.read_text())
        tool = ScadeOne._Tools()
        print("Tool paths:")
        for tool_enum in IScadeOne.Tool:
            tool_path = tool.get_tool_path(tool_enum)
            print(f"{tool_enum}: {tool_path}")
        ret = True
    except ScadeOneException as error:
        print("ERROR -", error.args[0], file=sys.stderr)
        ret = False
    return ret


# ========================================================================================
# Python wrapper generation
# ========================================================================================
def python_wrapper_options_parser(pw_parser: argparse.ArgumentParser):
    pw_parser.add_argument(
        "--install-dir",
        type=Path,
        help="Scade One installation directory",
        dest="install_dir",
    )
    pw_parser.add_argument(
        "project",
        type=Path,
        help="Scade One project",
    )
    pw_parser.add_argument("-j", "--job", type=str, help="Generated Code job name", required=True)
    pw_parser.add_argument(
        "-o",
        "--output",
        help="Name of the Python wrapper module. By default, the name is `root_wrapper`",
    )
    pw_parser.add_argument(
        "--target-dir",
        type=Path,
        help="Target wrapper directory. By default, a directory with the wrapper name is created "
        "in the current directory.",
    )

    pw_parser.set_defaults(func=python_wrapper_command)


def python_wrapper_command(args) -> bool:
    from ansys.scadeone.core.svc.pywrapper.python_wrapper import PythonWrapper

    print(
        f"Generate Python wrapper for project {args.project}",
        flush=True,
    )

    try:
        app = scadeone_app(args)
        project_path = Path(args.project)
        if not project_path.is_absolute():
            project_path = Path.cwd() / project_path
        project = app.load_project(project_path)
        if project is None:
            print(f"Failed to load project: {args.project}", file=sys.stderr)
            return False
        job_name = args.job
        out_name = None
        if args.output:
            out_name = args.output
        target_path = None
        if args.target_dir:
            target_path = args.target_dir

        py_wrapper = PythonWrapper(project, job_name, out_name, target_path)
        py_wrapper.generate()

        print(
            f"Files generated under {py_wrapper._target_dir()}",
            flush=True,
        )
        return True
    except ScadeOneException as error:
        print("ERROR -", error.args[0], file=sys.stderr)
        return False


# ========================================================================================
# Simulation data file viewing and dumping
# ========================================================================================
def view_sd_options_parser(sd_parser: argparse.ArgumentParser):
    sd_parser.add_argument(
        "--show",
        help="Show content of a simulation data file",
        dest="sd",
    )
    sd_parser.set_defaults(func=view_sd_command)
    sd_parser.add_argument(
        "--dump",
        help="Content of a simulation data file in dump format for debugging",
        dest="sd_dump",
    )
    sd_parser.set_defaults(func=view_sd_command)


def view_sd_command(args) -> bool:
    import ansys.scadeone.core.svc.simdata as sd
    from ansys.scadeone.core.svc.simdata.core.dll_wrap import sdf_open, sdf_dump, sdf_close
    from ansys.scadeone.core.svc.simdata.core import FileOpenMode

    if args.sd:
        sd_path = Path(args.sd)
        if not sd_path.exists():
            print(f"File not found: {sd_path}")
            return False
        sd_fd = sd.open_file(str(sd_path))
        print(sd_fd)
        sd_fd.close()
        return True

    if args.sd_dump:
        sd_path = Path(args.sd_dump)
        if not sd_path.exists():
            print(f"File not found: {sd_path}")
            return False
        sd_fd = sdf_open(str(sd_path), FileOpenMode.READ)
        if sdf_dump(sd_fd) != 0:
            print(f"Failed to dump simulation data file: {sd_path}")
            return False
        sdf_close(sd_fd)
        return True

    return False


# ========================================================================================
# Job related commands
# ========================================================================================
def job_options_parser(job_parser: argparse.ArgumentParser):
    job_parser.add_argument(
        "project",
        type=Path,
        help="Scade One project",
    )
    job_parser.add_argument(
        "--install-dir",
        type=Path,
        help="Scade One installation directory",
        dest="install_dir",
    )
    job_parser.add_argument(
        "--list",
        help="List all jobs in the project",
        dest="job_list",
        action="store_true",
    )
    job_parser.add_argument(
        "--run",
        help="Run a specific job",
        dest="job_run",
    )
    job_parser.add_argument(
        "--run-all",
        help="Run all jobs in the project",
        dest="job_run_all",
        action="store_true",
    )
    job_parser.set_defaults(func=job_command)


def job_command(args) -> bool:
    from ansys.scadeone.core.common.storage import FileStorage

    app = scadeone_app(args)
    project = app.load_project(args.project)
    if not project:
        print(f"Failed to load project: {args.project}", file=sys.stderr)
        return False
    project.load_jobs()

    if args.job_list:
        job_kinds = {}
        for job in project.jobs:
            kind = str(job._kind)
            if kind not in job_kinds:
                job_kinds[kind] = []
            job_kinds[kind].append(job)
        for kind in sorted(job_kinds.keys()):
            project_path = Path(args.project).absolute().parent
            print(kind)
            for job in job_kinds[kind]:
                if isinstance(job.storage, FileStorage):
                    print(
                        f"   {job.name} (file: {Path(job.storage.path).relative_to(project_path)})"
                    )
                else:
                    print(f"   {job.name}")
        return True
    if args.job_run or args.job_run_all:
        if args.job_run_all:
            jobs = project.jobs
            print("Running all jobs in project ...")
        else:
            job = project.get_job(args.job_run)
            if not job:
                print(f"Job '{args.job_run}' not found in project {args.project}", file=sys.stderr)
                return False
            jobs = [job]
        result = True
        success_count = 0
        for job in jobs:
            print("=" * 80)
            print(f"Running job '{job.name}'...")
            res = job.run()
            if res.code != 0:
                print(
                    f"Job '{job.name}' failed with return code {res.code}\nMessage: {res.message}",
                )
            else:
                success_count += 1
            result = result and res.code == 0
        print("-" * 80)
        print(f"{success_count}/{len(jobs)} jobs ran successfully.")
        return result
    return False


# ========================================================================================
# Main
# ========================================================================================
def main() -> bool:
    """Scade One Python command line.

    Returns True if the command line is executed successfully."""
    print_banner()
    parser = argparse.ArgumentParser(
        prog="pyscadeone",  # type: ignore[assignment]
        description="Scade One Python library command line tool",
        epilog="For more information see: "
        "https://scadeone.docs.pyansys.com/"
        " and "
        "https://www.ansys.com/products/embedded-software/ansys-scade-one",
        fromfile_prefix_chars="@",
    )
    main_options_parser(parser)
    # Adding subparsers for other commands
    subparser = parser.add_subparsers(
        title="Sub-commands",
        help="Use: command --help for help (ex: pyscadeone simdata --help)",
        dest="subparser_command",
    )

    # Python wrapper command
    pw_parser = subparser.add_parser("pycodewrap", help="Generates Scade One wrapper in Python")
    python_wrapper_options_parser(pw_parser)

    # Simulation data
    sd_parser = subparser.add_parser("simdata", help="Simulation data related command")
    view_sd_options_parser(sd_parser)

    # Job related commands
    job_parser = subparser.add_parser("job", help="Job related command")
    job_options_parser(job_parser)

    # Parsing
    parser_args = parser.parse_args()

    if parser_args.log:
        LOGGER.log_to_file(parser_args.log)

    if parser_args.verbosity > 0:
        if parser_args.verbosity == 1:
            level = LoggerLevel.INFO
        else:
            level = LoggerLevel.DEBUG
        LOGGER.log_to_console(level)
    LOGGER.debug(f"Running pyscadeone command line with: {parser_args}")

    ret = False
    if parser_args.formats:
        ret = show_formats()
    elif parser_args.set_install_dir:
        ret = set_install_dir_command(parser_args.set_install_dir)
    elif parser_args.subparser_command:
        ret = parser_args.func(parser_args)
    LOGGER.flush()
    if parser_args.no_exit:
        return ret
    sys.exit(0 if ret else 1)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
