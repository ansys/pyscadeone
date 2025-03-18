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

from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Union

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.dotnet import load_dll

if TYPE_CHECKING:
    import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore


class BuildResult:
    """Build result.

    Parameters
    ----------
    net_result : Toolkit.BuildResult
        .NET build result.
    """

    def __init__(self, net_result: "Toolkit.BuildResult") -> None:
        self._success = net_result.Success
        self._messages = [str(m) for m in net_result.Messages]

    @property
    def success(self) -> bool:
        return self._success

    @property
    def messages(self) -> List[str]:
        return self._messages

    def __str__(self) -> str:
        res = "Build " + ("succeeded" if self._success else "failed")
        if self._messages:
            res += "\nBuild messages: "
            for m in self._messages:
                res += "\n - " + str(m)
        return res


class BuildConfig:
    """Build configuration for building C source files.

    Attributes
    ----------
    working_dir : str
        Working directory.
    c_files : List[str]
        List of C source files.
    h_files : List[str]
        List of header files.
    o_files : List[str]
        List of object files.
    include_dirs : List[str]
        List of include directories.
    proto_files : List[str]
        List of protocol buffer files.
    preproc_defs : List[str]
        List of preprocessor definitions.
    lib_files : List[str]
        List of library files.
    targets : List[Target]
        List of build targets.
    mingw_dir : Optional[str]
        Path to the MinGW directory.
    compiler_config : Optional[CompilerConfig]
        Compiler configuration.
    incremental : bool
        Incremental build.
    """

    def __init__(self) -> None:
        self.working_dir: str = ""
        self.c_files: List[str] = []
        self.h_files: List[str] = []
        self.o_files: List[str] = []
        self.include_dirs: List[str] = []
        self.proto_files: List[str] = []
        self.preproc_defs: List[str] = []
        self.lib_files: List[str] = []
        self.targets: List[Target] = []
        self.mingw_dir: Optional[str] = None
        self.compiler_config: Optional[CompilerConfig] = None
        self.incremental: bool = False


class BuildSystem:
    """Build an executable or a shared library from C source files.

    Parameters
    ----------
    sone_install_dir : Union[Path, str]
        Path to the Scade One installation directory.
    """

    def __init__(self, sone_install_dir: Union[Path, str]) -> None:
        self._result = None
        if not sone_install_dir:
            raise ScadeOneException("Scade One installation directory not provided.")
        if isinstance(sone_install_dir, str):
            self._sone_install_dir = Path(sone_install_dir)
        else:
            self._sone_install_dir = sone_install_dir
        if not self._sone_install_dir.exists():
            raise ScadeOneException(
                f"Scade One installation directory not found: {self._sone_install_dir}"
            )
        self._register_build_system_dll()

    @property
    def result(self) -> BuildResult:
        """Return the build result."""
        return self._result

    def build(self, config: BuildConfig) -> BuildResult:
        """Build the C source files according to the build configuration.

        Parameters
        ----------
        config : BuildConfig
            Build configuration.

        Returns
        -------
        BuildResult
            Build result.
        """
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        net_config = NetBuildConfig(config, self._sone_install_dir)
        bld = Toolkit.Builder()
        self._result = BuildResult(bld.Build(net_config.config))
        return self._result

    def _register_build_system_dll(self) -> None:
        simulator_dir = self._sone_install_dir / "tools/simulator"
        if not simulator_dir.exists():
            raise ScadeOneException(f"Simulator directory not found: {simulator_dir}")
        references = ["ANSYS.SONE.Build.Toolkit", "System.Collections"]
        load_dll(simulator_dir, references)


class TargetKind(Enum):
    """Kind of build target."""

    #: Executable target.
    EXECUTABLE = auto()

    #: Shared library target.
    SHARED_LIBRARY = auto()


class Target:
    """Build target.

    Parameters
    ----------
    base_name : str
        Name of the target.
    kind : TargetKind
        Kind of the target.
    """

    def __init__(self, base_name: str, kind: TargetKind):
        self._base_name = base_name
        self._kind = kind

    @property
    def base_name(self) -> str:
        return self._base_name

    @property
    def kind(self) -> TargetKind:
        return self._kind


class CompilerConfig:
    """Compiler configuration.

    Parameters
    ----------
    compiler_mk_path : str
        Path to the compiler configuration file.
    make_cmd_path : str
        Path to the make command.
    """

    def __init__(self, compiler_mk_path: str, make_cmd_path: str) -> None:
        self._compiler_mk_path = compiler_mk_path
        self._make_cmd_path = make_cmd_path

    @property
    def compiler_mk_path(self) -> str:
        return self._compiler_mk_path

    @property
    def make_cmd_path(self) -> str:
        return self._make_cmd_path


class NetBuildConfig:
    """Convert a Python BuildConfig to a .NET BuildConfig.

    Parameters
    ----------
    config : BuildConfig
        Python build configuration.
    """

    def __init__(self, config: BuildConfig, sone_install_dir: Optional[Path] = None) -> None:
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore
        from System.Collections.Generic import List as NetList  # type:ignore

        self._net_config = Toolkit.BuildConfig()
        self._net_config.WorkingDir = config.working_dir
        self._net_config.CFiles = self._to_net_str_list(config.c_files)
        self._net_config.HFiles = self._to_net_str_list(config.h_files)
        self._net_config.OFiles = self._to_net_str_list(config.o_files)
        self._net_config.IncludeDirs = self._to_net_str_list(config.include_dirs)
        self._net_config.ProtoFiles = self._to_net_str_list(config.proto_files)
        self._net_config.PreprocDefs = self._to_net_str_list(config.preproc_defs)
        self._net_config.LibFiles = self._to_net_str_list(config.lib_files)
        self._net_config.Targets = NetList[Toolkit.Target]()
        for target in config.targets:
            self._net_config.Targets.Add(NetTarget(target).target)
        if config.mingw_dir:
            self._net_config.MingwDir = str(config.mingw_dir)
        elif sone_install_dir:
            self._net_config.MingwDir = str(sone_install_dir / "contrib/mingw64")
        else:
            raise ScadeOneException("MinGW directory not provided.")
        if config.compiler_config:
            self._net_config.CompilerConfig = NetCompilerConfig(config.compiler_config).config
        self._net_config.Incremental = config.incremental

    @property
    def config(self) -> "Toolkit.BuildConfig":
        """Return the .NET build configuration."""
        return self._net_config

    @staticmethod
    def _to_net_str_list(
        py_str_list: List[str],
    ):  # TODO: fix adding typing return -> NetList[NetString]
        """Convert a Python list of strings to a .NET list of strings."""
        from System import String as NetString  # type:ignore
        from System.Collections.Generic import List as NetList  # type:ignore

        net_list = NetList[NetString]()
        for s in py_str_list:
            net_list.Add(s)
        return net_list


class NetTarget:
    """Convert a Python Target to a .NET Target.

    Parameters
    ----------
    target : Target
        Python target.
    """

    def __init__(self, target: Target) -> None:
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        kind = None
        if target.kind == TargetKind.EXECUTABLE:
            kind = Toolkit.TargetKind.Executable
        elif target.kind == TargetKind.SHARED_LIBRARY:
            kind = Toolkit.TargetKind.SharedLibrary

        self._net_target = Toolkit.Target(target.base_name, kind)

    @property
    def target(self) -> "Toolkit.Target":
        """Return the .NET target."""
        return self._net_target


class NetCompilerConfig:
    """Convert a Python CompilerConfig to a .NET CompilerConfig.

    Parameters
    ----------
    config : CompilerConfig
        Python compiler configuration.
    """

    def __init__(self, config: CompilerConfig) -> None:
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        self._net_compiler_config = Toolkit.CompilerConfig(
            config.compiler_mk_path, config.make_cmd_path
        )

    @property
    def config(self) -> "Toolkit.CompilerConfig":
        """Return the .NET compiler configuration."""
        return self._net_compiler_config
