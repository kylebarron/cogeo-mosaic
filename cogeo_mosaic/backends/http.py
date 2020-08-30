"""cogeo-mosaic HTTP backend."""

import json
from typing import Any, List

import attr
import mercantile
import requests
from cachetools.keys import hashkey

from cogeo_mosaic.backends.base import BaseBackend
from cogeo_mosaic.backends.utils import _decompress_gz, get_items_from_json
from cogeo_mosaic.cache import lru_cache
from cogeo_mosaic.errors import _HTTP_EXCEPTIONS, MosaicError
from cogeo_mosaic.mosaic import MosaicJSON


@attr.s
class HttpBackend(BaseBackend):
    """Http/Https Backend Adapter"""

    _backend_name = "HTTP"

    def items_for_tile(self, x: int, y: int, z: int) -> List[str]:
        """Retrieve items for tile."""
        return get_items_from_json(self.mosaic_def.tiles, self.quadkey_zoom, x, y, z)

    def items_for_point(self, lng: float, lat: float) -> List[str]:
        """Retrieve items for point."""
        tile = mercantile.tile(lng, lat, self.quadkey_zoom)
        return get_items_from_json(
            self.mosaic_def.tiles, self.quadkey_zoom, tile.x, tile.y, tile.z
        )

    def write(self):
        """Write mosaicjson document."""
        raise NotImplementedError

    def update(self, *args, **kwargs: Any):
        """Update the mosaicjson document."""
        raise NotImplementedError

    @lru_cache(key=lambda self, gzip=None: hashkey(self.path, gzip),)
    def _read(self, gzip: bool = None) -> MosaicJSON:  # type: ignore
        """Get mosaicjson document."""
        try:
            r = requests.get(self.path)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # post-flight errors
            status_code = e.response.status_code
            exc = _HTTP_EXCEPTIONS.get(status_code, MosaicError)
            raise exc(e.response.content) from e
        except requests.exceptions.RequestException as e:
            # pre-flight errors
            raise MosaicError(e.args[0].reason) from e

        body = r.content

        self._file_byte_size = len(body)

        if gzip or (gzip is None and self.path.endswith(".gz")):
            body = _decompress_gz(body)

        return MosaicJSON(**json.loads(body))
