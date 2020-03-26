import functools
from typing import Dict, Tuple

import mercantile
import requests

from cogeo_mosaic.backend.base import BaseBackend
from cogeo_mosaic.backend.utils import get_assets_from_json
from cogeo_mosaic.utils import _decompress_gz


class HttpBackend(BaseBackend):
    """Http/Https Backend Adapter"""

    def __init__(self, url: str):
        self.mosaic_def = self.fetch_mosaic_definition(url)

    def metadata(self) -> Dict:
        return self.mosaic_def

    def tile(self, x: int, y: int, z: int, bucket: str, key: str) -> Tuple[str]:
        """Retrieve assets for tile."""

        return get_assets_from_json(self.mosaic_def, x, y, z)

    def point(self, lng: float, lat: float) -> Tuple[str]:
        """Retrieve assets for point."""

        min_zoom = self.mosaic_def["minzoom"]
        quadkey_zoom = self.mosaic_def.get("quadkey_zoom", min_zoom)  # 0.0.2
        tile = mercantile.tile(lng, lat, quadkey_zoom)
        return get_assets_from_json(self.mosaic_def, tile.x, tile.y, tile.z)

    @functools.lru_cache(maxsize=512)
    def fetch_mosaic_definition(self, url: str) -> Dict:
        """Get Mosaic definition info."""
        # use requests
        body = requests.get(url)
        body = body.content

        if url.endswith(".gz"):
            body = _decompress_gz(body)

        if isinstance(body, dict):
            return body
        else:
            return json.loads(body)