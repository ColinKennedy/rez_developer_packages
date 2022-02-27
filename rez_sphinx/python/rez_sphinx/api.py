"""All public-facing commands which :ref:`rez_sphinx` allows other packages to run."""

from .core.bootstrap import bootstrap

__all__ = ["bootstrap"]
