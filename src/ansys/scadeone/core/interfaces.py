# for reference in Model
# IProject: app return type is 'scadeone.IScadeOne'
# see https://softwareengineering.stackexchange.com/questions/369146/how-to-avoid-bidirectional-class-and-module-dependencies  # noqa: E501
# The point is that ScadeOne and Project uses each other
# Alternative is to create an intermediate interfaces.py.

from pathlib import Path
from typing import Union


class IProject:
    """Interface class"""

    @property
    def app(self) -> "IScadeOne":
        pass


class IScadeOne:
    """Interface class"""

    @property
    def logger(self):
        return None

    @property
    def version(self) -> str:
        return ""

    @property
    def install_dir(self) -> Union[Path, None]:
        """Installation directory as given when creating the ScadeOne instance."""
        assert False

    def subst_in_path(self, _: str) -> str:
        assert False
