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

import os
import platform
from pathlib import Path
from typing import List, Optional, Union, cast
import xml.dom.minidom as minidom

from ansys.scadeone.core.common.exception import ScadeOneException
from ansys.scadeone.core.common.logger import LOGGER, ScadeOneLogger
from ansys.scadeone.core.common.storage import ProjectFile
from ansys.scadeone.core.interfaces import IScadeOne as IScadeOne
from ansys.scadeone.core.project import Project
from ansys.scadeone.core.model.parser import Parser


class ScadeOne(IScadeOne):
    """Scade One API. This is the main entry point for users of the API,
    providing access to projects, tools, and other functionality.

    Parameters
    ----------
    install_dir : Optional[Union[str, Path]]
        Optional installation directory to use for determining tool paths.

        If not provided, the API will look for the *Configuration/modulesLocation.config*
        file next to the 'ansys.scadeone.core' module.

        If neither provided nor found, tool paths will not be available and no functionality
        requiring code generation, or other tool-dependent features, will be accessible.
    """

    def __init__(self, install_dir: Optional[Union[str, Path]] = None) -> None:
        self._logger = LOGGER
        self._projects = {}
        self._install_dir = Path(install_dir) if isinstance(install_dir, str) else install_dir
        self._parser: Optional[Parser] = None
        self._tools = self._Tools(self._install_dir)

    class _Tools:
        """Private class for Scade One installation tools.

        The *get_tool_path* method can be used to retrieve the path of a specific tool.

        The class handles several scenarios for determining tool paths, from the most specific to the least:
        - If the Scade One *install_dir* is provided, tool paths are resolved relative to the installation directory,
        as specified in the plateform-specific configuration file.
        - If the *modulesLocation.config* file is found, it will load tool paths from the file.
        - Else, there is not configuration available, and tool paths will not be found.

        Tool path resolution logic when config file is available:
        - If a tool path is specified in the configuration file and is absolute, it is used
            as is.
        - If a tool path is specified in the configuration file and is relative, it is resolved
            relative to the installation directory if available.
        - If a tool path correspond to an existing file, it is returned, otherwise None is returned.

        The *generate_config* method can be used to generate a *modulesLocation.config* configuration file
        based on the provided installation directory and default configuration. See *pyscadeone --help*.

        The installation directory is saved in the configuration file as a **relative** path to allow sharing
        the configuration across different machines. It key is *ScadeOneLocation*.

        Users can also provide their own *modulesLocation.config* configuration file placed in the *Configuration*
        folder next to the 'ansys.scadeone.core' module. All paths must be relative to the *ScadeOneLocation* folder
        or absolute.

        The *ScadeOneLocation* entry is mandatory and:
        - absolute path,
        - or relative path to the *ansys.scadeone.core* module, will be resolved relative to the module location.
        """

        def __init__(self, install_dir: Optional[Path] = None) -> None:
            self._tool_paths = self._load_config(install_dir)

        @classmethod
        def _get_config_path(cls, install_dir: Optional[Path] = None) -> Optional[Path]:
            """Get the path to the configuration file.

            Parameters
            ----------
            install_dir : Optional[Path]
                Installation directory to use for determining config file location.
                If None, looks for *modulesLocation.config* file next to this module.

            Returns
            -------
            Optional[Path]
                Path to the configuration file if found, otherwise None.
            """
            configuration_path = Path(__file__).parent / "Configuration"
            if install_dir:
                # Use default config file to get relative paths
                config_file = (
                    "modulesLocation.config.win"
                    if platform.system() == "Windows"
                    else "modulesLocation.config.linux"
                )
                return configuration_path / config_file
            config_path = configuration_path / "modulesLocation.config"
            if config_path.exists():
                return config_path
            return None

        @classmethod
        def _load_config(cls, install_dir: Optional[Path] = None) -> dict[IScadeOne.Tool, Path]:
            """Load the configuration file is any and return a dictionary of tool paths.

            Parameters
            ----------
            install_dir : Optional[Path]
                Installation directory to use for determining config file location.
                If None, looks for ``modulesLocation.config`` file next to this module.

            Returns
            -------
            dict[IScadeOne.Tool, Path]
                Dictionary mapping IScadeOne.Tool enum values to their corresponding paths.
            """
            config_path = cls._get_config_path(install_dir)
            if not config_path:
                return {}
            tool_paths = {}
            doc = minidom.parse(str(config_path))
            for tool in IScadeOne.Tool:
                elements = doc.getElementsByTagName(str(tool))
                if elements and elements[0].firstChild is not None:
                    if text := elements[0].firstChild.nodeValue:
                        path = Path(text.strip())
                        tool_paths[tool] = path
            if install_dir:
                # Override ScadeOneLocation with the user provided install_dir,
                # but keep other paths from config
                tool_paths[IScadeOne.Tool.SCADE_ONE_LOCATION] = install_dir
            elif s1_path := tool_paths.get(IScadeOne.Tool.SCADE_ONE_LOCATION):
                # s1_path should be relative to ansys.scadeone.core
                if s1_path.is_absolute():
                    # Some absolute path was provided in config, keep it as is
                    tool_paths[IScadeOne.Tool.SCADE_ONE_LOCATION] = s1_path
                else:
                    # If path is not absolute, try to resolve it relative to config file
                    s1_path = (Path(__file__).parent / s1_path).resolve().absolute()
                    tool_paths[IScadeOne.Tool.SCADE_ONE_LOCATION] = s1_path
            return tool_paths

        @classmethod
        def generate_config(cls, installation_path: Path | str) -> Path:
            """Generate a configuration file with the current tool paths.

            Parameters
            ----------
            installation_path : Path
                Path to the installation directory.

            Returns
            -------
            Path
                Path to the generated configuration file.

             Raises
             ------
             ScadeOneException
                If the installation path does not exist.
            """
            if isinstance(installation_path, str):
                installation_path = Path(installation_path).resolve().absolute()
            if not installation_path.exists():
                raise ScadeOneException(f"Installation path '{installation_path}' does not exist.")
            pyscadone_path = Path(__file__).parent
            output_path = pyscadone_path / "Configuration" / "modulesLocation.config"
            # Load appropriate default configuration
            tool_paths = cls._load_config(installation_path)
            # Override ScadeOneLocation with the provided installation path
            try:
                relative_path = Path(os.path.relpath(installation_path, pyscadone_path))
            except ValueError:
                # If relative path cannot be determined, use absolute path
                relative_path = installation_path
            tool_paths[IScadeOne.Tool.SCADE_ONE_LOCATION] = relative_path

            doc = minidom.Document()
            root = doc.createElement("ModulesLocationConfiguration")
            doc.appendChild(root)
            for tool, path in tool_paths.items():
                element = doc.createElement(str(tool))
                text_node = doc.createTextNode(str(path))
                element.appendChild(text_node)
                root.appendChild(element)
            with open(output_path, "wb") as f:
                f.write(doc.toprettyxml(indent="  ", encoding="utf-8"))
            return output_path

        def get_tool_path(self, tool: IScadeOne.Tool) -> Path | None:
            """Get the path of a Scade One tool.

            Parameters
            ----------
            tool : IScadeOne.Tool
                Enum value representing the tool.
            Returns
            -------
            Path|None
                Path to the tool executable, or None if not found.
            """
            tool_path = self._tool_paths.get(tool)
            if tool_path is None:
                # Noconfiguration or missing entry
                return None
            if not tool_path.is_absolute():
                # If path is not absolute, try to resolve it relative to install_dir if available
                install_dir = self._tool_paths.get(IScadeOne.Tool.SCADE_ONE_LOCATION)
                if install_dir is None:
                    # No installation directory available
                    return None
                tool_path = install_dir / tool_path
            return tool_path if tool_path.exists() else None

    @property
    def parser(self) -> Parser:
        """Shared :py:class:`SwanParser` used by every per-project model."""
        if self._parser is None:
            from ansys.scadeone.core.model.loader import SwanParser

            self._parser = SwanParser(self._logger)  # type: ignore[arg-type]
        return self._parser

    @property
    def projects(self) -> List[Project]:
        """Returns the loaded projects.

        Returns
        -------
        List[Project]
           Loaded projects.
        """
        return list(self._projects.values())

    @property
    def install_dir(self) -> Union[Path, None]:
        """Installation directory as given when creating the ScadeOne instance."""
        return self._install_dir

    @property
    def version(self) -> str:
        """API version."""
        from ansys.scadeone.core import __version__

        return __version__

    @property
    def logger(self) -> ScadeOneLogger:
        return self._logger

    def get_tool_path(self, tool: IScadeOne.Tool) -> Path | None:
        """Get the path of a Scade One tool.

        Parameters
        ----------
        tool : IScadeOne.Tool
            Enum value representing the tool.
            Currently supported value is IScadeOne.Tool.JOB_LAUNCHER.
        Returns
        -------
        Path|None
            Path to the tool executable, or None if not found.
        """
        return self._tools.get_tool_path(tool)

    # For context management
    def __enter__(self) -> "ScadeOne":
        self.logger.info("Entering context")
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> bool:
        if exc_type and not isinstance(exc_type, Union[ScadeOneException, SystemExit]):
            msg = f"Exiting on exception {exc_type}"
            if exc_value:
                msg += f" with value {exc_value}"
            self.logger.exception(msg)
        self.close()
        # propagate exception
        return False

    # end context management

    def close(self) -> None:
        """Close application, releasing any connection."""
        pass

    def __del__(self) -> None:
        self.close()

    def load_project(self, storage: Union[Project, str, Path]) -> Union[Project, None]:
        """Load a Scade One project.

        Parameters
        ----------
        storage : Union[Project, str, Path]
            Storage containing project data.

        Returns
        -------
        Project|None
            Project object, or None if file does not exist.
        """
        if isinstance(storage, (str, Path)):
            proj_file = ProjectFile(storage)
            if not proj_file.exists():
                self.logger.error(f"Project does not exist {proj_file.path}")
                return None
            project = Project(self, proj_file)
        else:
            project = cast(Project, storage)
            proj_file = cast(ProjectFile, project.storage)

        if proj_file.path not in self._projects:
            self._projects[proj_file.path] = project
            # load all dependencies first, then the project itself
            for proj in project.dependencies(all):
                self.load_project(proj)
        return self._projects[proj_file.path]

    def find_project(self, path: Path) -> Optional[Project]:
        """Return the loaded :py:class:`Project` for the given sproj path, or None."""
        return self._projects.get(path)

    def subst_in_path(self, path: str) -> str:
        """Substitute ``$(SCADE_ONE_LIBRARIES_DIR)`` in path.

        if :py:attr:`ScadeOne.install_dir` is None, no change is made.
        """
        if lib_dir := self.get_tool_path(IScadeOne.Tool.LIBRARIES):
            path = path.replace("$(SCADE_ONE_LIBRARIES_DIR)", str(lib_dir))
        return path

    def new_project(self, project_path: Union[str, Path]) -> Project:
        """Create a new project.

        Parameters
        ----------
        project_path : Union[str, Path]
            Project location.

        Returns
        -------
        Project
            Project object.
        """

        if not project_path:
            raise ScadeOneException("Project path must be provided.")

        if isinstance(project_path, str):
            project_path = Path(project_path)

        if project_path.exists():
            raise ScadeOneException(f"'{project_path.name}' project already exists.")

        storage = ProjectFile(project_path)

        from ansys.scadeone.core.svc.swan_creator.project_creator import (
            ProjectAdder,
            ProjectFactory,
        )

        project = ProjectFactory.create_project(self, storage)
        ProjectAdder.add_project(self, project)
        return project
