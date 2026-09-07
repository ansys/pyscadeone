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

from __future__ import annotations

from abc import ABC
from enum import Enum, auto
from pathlib import Path
import platform
from typing import TYPE_CHECKING, List, Optional, Union

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.dotnet import load_dll
from ansys.scadeone.core.interfaces import IScadeOne

if TYPE_CHECKING:
    import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore
    from System.Collections.Generic import List as NetList  # type:ignore
    from System.Collections.Generic import HashSet as NetSet  # type:ignore
    from System.Collections.Generic import IEnumerable as NetEnumerable  # type:ignore
    from System import String as NetString  # type:ignore


class _NetUtils:
    """Utilities for converting Python data structures to .NET data structures."""

    @staticmethod
    def to_net_str_set(py_str_list: List[str]) -> NetSet[NetString]:
        """Convert a Python list of strings to a .NET set of strings.

        Parameters
        ----------
        py_str_list : List[str]
            Python list of strings to convert.

        Returns
        -------
        NetSet[NetString]
            .NET set of strings.
        """
        from System import String as NetString  # type:ignore
        from System.Collections.Generic import HashSet as NetSet  # type:ignore

        net_set = NetSet[NetString]()
        for s in py_str_list:
            net_set.Add(s)
        return net_set

    @staticmethod
    def to_net_str_list(py_str_list: List[str]) -> NetList:
        """Convert a Python list of strings to a .NET list of strings.

        Parameters
        ----------
        py_str_list : List[str]
            Python list of strings to convert.

        Returns
        -------
        NetList
            .NET list of strings.
        """
        from System import String as NetString  # type:ignore
        from System.Collections.Generic import List as NetList  # type:ignore

        net_list = NetList[NetString]()
        for s in py_str_list:
            net_list.Add(s)
        return net_list


class _PyUtils:
    """Utilities for converting .NET data structures to Python data structures."""

    @staticmethod
    def to_py_str_list(net_str_set: NetEnumerable[str]) -> List[str]:
        py_list = []
        for s in net_str_set:
            py_list.append(s)
        return py_list


class BuildToolkitLoader(ABC):
    """Load .NET Build Toolkit library."""

    _dll_loaded = False

    def __init__(self, app: IScadeOne) -> None:
        if BuildToolkitLoader._dll_loaded:
            return
        simulator_dir = app.get_tool_path(IScadeOne.Tool.SIMULATOR)
        if not simulator_dir or not simulator_dir.exists():
            raise ScadeOneException("Scade Installation path is not valid")
        references = ["ANSYS.SONE.Build.Toolkit", "System.Collections"]
        load_dll(simulator_dir, references)
        BuildToolkitLoader._dll_loaded = True


class BuildResult:
    """Build result.

    Parameters
    ----------
    net_result : Toolkit.BuildResult
        .NET build result.
    """

    def __init__(self, net_result: Toolkit.BuildResult) -> None:
        self._is_succeeded = net_result.Success
        self._messages = [str(m) for m in net_result.Messages]

    @property
    def is_succeeded(self) -> bool:
        """Return True if the build succeeded, False otherwise."""
        return self._is_succeeded

    @property
    def messages(self) -> List[str]:
        """Build result messages."""
        return self._messages

    def __str__(self) -> str:
        res = "Build " + ("succeeded" if self.is_succeeded else "failed")
        if self._messages:
            res += "\nBuild messages: "
            for m in self._messages:
                res += "\n - " + str(m)
        return res


class CompilerConfig:
    """Compiler configuration.

    Parameters
    ----------
    net_build_cfg : Optional[Toolkit.CompilerConfig]
        Compiler configuration.
    """

    def __init__(self, net_build_cfg: Optional[Toolkit.CompilerConfig] = None) -> None:
        self._compiler_mk_path = net_build_cfg.MkPath if net_build_cfg else ""
        self._make_cmd_path = net_build_cfg.MakeCmdPath if net_build_cfg else ""

    @property
    def compiler_mk_path(self) -> str:
        """Makefile include path"""
        return self._compiler_mk_path

    @property
    def make_cmd_path(self) -> str:
        """Make command path"""
        return self._make_cmd_path


class BuildConfig:
    """Build configuration for building C source files.

    Attributes
    ----------
    user_config_header_files : List[str]
        List of user configuration header files to be included in the build.
    include_dirs : List[str]
        List of include directories for the compiler.
    env_path_dirs : List[str]
        List of directories to append to the environment PATH for analysis.
    preprocessor_defs : List[str]
        List of preprocessor definitions for the compiler.
    compiler_flags : Optional[str]
        Additional compiler flags.
    linker_flags : Optional[str]
        Additional linker flags.
    object_files : List[str]
        List of object files to be linked with the build.
    compiler_config : Optional[CompilerConfig]
        Optional compiler configuration.
    """

    def __init__(self) -> None:
        self.user_config_header_files: List[str] = []
        self.include_dirs: List[str] = []
        self.env_path_dirs: List[str] = []
        self.preprocessor_defs: List[str] = []
        self.compiler_flags: Optional[str] = None
        self.linker_flags: Optional[str] = None
        self.object_files: List[str] = []
        self.compiler_config: Optional[CompilerConfig] = None


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

    def __init__(self, base_name: str, kind: TargetKind) -> None:
        self._base_name = base_name
        self._kind = kind

    @property
    def base_name(self) -> str:
        """Name of the target."""
        return self._base_name

    @property
    def kind(self) -> TargetKind:
        """Kind of the target."""
        return self._kind


class BuildRequest:
    """Build request for building C source files."""

    def __init__(self):
        self.working_dir: str = ""
        self.c_files: List[str] = []
        self.h_files: List[str] = []
        self.targets: List[Target] = []
        self.mingw_dir: Optional[str] = None
        self.build_config_path: Union[Path, str, None] = None
        self.build_config: Optional[BuildConfig] = None
        self.incremental: bool = False


class NetBuildConfig:
    """Convert a Python BuildConfig to a .NET BuildConfig.

    Parameters
    ----------
    config : BuildConfig
        Python build configuration.
    """

    def __init__(self, config: BuildConfig) -> None:
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        self._config = Toolkit.BuildConfig()
        self._config.UserConfigHeaderFiles = _NetUtils.to_net_str_set(
            config.user_config_header_files
        )
        self._config.IncludeDirs = _NetUtils.to_net_str_set(config.include_dirs)
        self._config.EnvPathDirs = _NetUtils.to_net_str_set(config.env_path_dirs)
        self._config.PreprocessorDefs = _NetUtils.to_net_str_list(config.preprocessor_defs)
        self._config.CompilerFlags = config.compiler_flags
        self._config.LinkerFlags = config.linker_flags
        self._config.ObjectFiles = _NetUtils.to_net_str_set(config.object_files)
        if config.compiler_config:
            self._config.CompilerConfig = NetCompilerConfig(config.compiler_config).config

    @property
    def config(self) -> Toolkit.BuildConfig:
        """Return the .NET build configuration."""
        return self._config


class NetBuildRequest:
    """Convert a Python BuildRequest to a .NET BuildRequest.

    Parameters
    ----------
    request : BuildRequest
        Python build request.
    app : IScadeOne
        Scade One application instance.
    """

    def __init__(self, request: BuildRequest, app: IScadeOne) -> None:
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        self._request = Toolkit.BuildRequest()
        self._request.WorkingDir = request.working_dir
        self._request.CFiles = _NetUtils.to_net_str_list(request.c_files)
        self._request.HFiles = _NetUtils.to_net_str_list(request.h_files)
        for target in request.targets:
            self._request.Targets.Add(NetTarget(target).target)
        if platform.system() == "Windows":
            # Mingw is requested only for this platform
            if request.mingw_dir:
                self._request.MingwDir = str(request.mingw_dir)
            else:
                mingw_dir = app.get_tool_path(IScadeOne.Tool.MINGW)
                if mingw_dir:
                    self._request.MingwDir = str(mingw_dir)
                else:
                    raise ScadeOneException("MinGW directory not provided.")

        if request.build_config_path and request.build_config:
            raise ScadeOneException(
                "Both build_config_path and build_config are provided. Please provide only one of them."
            )
        if request.build_config_path:
            net_build_cfg, _ = Toolkit.BuildConfigLoader.Load(str(request.build_config_path))
            self._request.BuildConfig = net_build_cfg
        if request.build_config:
            self._request.BuildConfig = NetBuildConfig(request.build_config).config

    @property
    def request(self) -> Toolkit.BuildRequest:
        """Return the .NET build request."""
        return self._request


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
    def target(self) -> Toolkit.Target:
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
    def config(self) -> Toolkit.CompilerConfig:
        """Return the .NET compiler configuration."""
        return self._net_compiler_config


class BuildSystem(BuildToolkitLoader):
    """Build an executable or a shared library from C source files.

    Parameters
    ----------
    app : IScadeOne
        Scade One application instance.
    """

    def __init__(self, app: IScadeOne) -> None:
        self._result = None
        self._app = app
        super().__init__(app)

    @property
    def result(self) -> BuildResult:
        """Return the build result."""
        if self._result is None:
            raise ScadeOneException("Build has not been executed yet.")
        return self._result

    def build(self, request: BuildRequest) -> BuildResult:
        """Build the C source files according to the build configuration.

        Parameters
        ----------
        request : BuildRequest
            Build request containing the build configuration.

        Returns
        -------
        BuildResult
            Build result.
        """
        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        net_request = NetBuildRequest(request, self._app)
        bld = Toolkit.Builder()
        self._result = BuildResult(bld.Build(net_request.request))
        return self._result


class GenResult:
    """Generator result.

    Parameters
    ----------
    net_result : Toolkit.GenResult
        .NET generator result.
    """

    def __init__(self, net_result: Toolkit.GenResult):
        self.success: bool = net_result.Success
        self.messages: List[object] = [m for m in net_result.Messages]
        self.generated_files: List[str] = _PyUtils.to_py_str_list(net_result.GeneratedFiles)

    def __str__(self) -> str:
        res = "Generation " + ("succeeded" if self.success else "failed")
        if self.messages:
            res += "\nGeneration messages: "
            for m in self.messages:
                res += "\n - " + str(m)
        if self.generated_files:
            res += "\nGenerated files: "
            for f in self.generated_files:
                res += "\n - " + f
        return res


class Generator(BuildToolkitLoader):
    def __init__(self, app: IScadeOne, cg_map_path: str | Path) -> None:
        super().__init__(app)

        import ANSYS.SONE.Build.Toolkit as Toolkit  # type:ignore

        self._net_generator = Toolkit.Generator(str(cg_map_path))

    def generate_remote_debug_lib(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateRemoteDebugLib(dest_dir, True))

    def generate_remote_debug_watch(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateRemoteDebugWatch(dest_dir))

    def generate_sensor_globals_decl(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateSensorGlobalsDecl(dest_dir))

    def generate_sensor_globals_def(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateSensorGlobalsDef(dest_dir))

    def generate_root_interface_globals_decl(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateRootInterfaceGlobalsDecl(dest_dir))

    def generate_root_interface_globals_def(self, dest_dir: str) -> GenResult:
        return GenResult(self._net_generator.GenerateRootInterfaceGlobalsDef(dest_dir))
