"""cogeo_mosaic.backend.base: base Backend class."""

import abc


class BaseBackend(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def metadata(self, *args, **kwargs):
        """Retrieve MosaicJSON metadata."""

    @abc.abstractmethod
    def tile(self, *args, **kwargs):
        """Retrieve assets for tile."""

    @abc.abstractmethod
    def point(self, *args, **kwargs):
        """Retrieve assets for point."""

    @abc.abstractmethod
    def create(self, *args, **kwargs):
        """Upload new MosaicJSON to backend."""

    @abc.abstractmethod
    def update(self, *args, **kwargs):
        """Update existing MosaicJSON on backend."""
