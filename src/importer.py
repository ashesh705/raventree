""" Fetch NAVs for a mutual fund"""

import asyncio
from collections.abc import Iterable
from itertools import chain
from typing import TypedDict

from aiohttp import ClientSession
from loguru import logger

from src.nav import NAV


class _APIOutputNode(TypedDict):
    """Single node of NAV API output"""

    date: str
    nav: str


class _APIOutput(TypedDict):
    """Representation of NAV API output format"""

    data: list[_APIOutputNode]


class _NAVImporter:
    """Import NAVs for a single mutual fund"""

    _URL = "https://api.mfapi.in/mf/{code}"

    def __init__(self, scheme_code: int, session: ClientSession) -> None:
        self.scheme_code = scheme_code
        self.session = session

    async def _get_raw_stream(self) -> _APIOutput:
        """Get the raw response from NAV API"""

        scheme_url = self._URL.format(code=self.scheme_code)

        logger.debug(f"Calling URL: {scheme_url}")
        async with self.session.get(scheme_url) as response:
            resp: _APIOutput = await response.json()
            return resp

    async def _read_stream(self) -> list[_APIOutputNode]:
        """Read the raw response from NAV API"""

        stream = await self._get_raw_stream()
        return stream["data"]

    async def get_nav(self) -> list[NAV]:
        """Return NAVs for the mutual fund"""

        raw = await self._read_stream()
        return list(map(self._transform, raw))

    def _transform(self, node: _APIOutputNode) -> NAV:
        """Transform the raw API response into a NAV object"""

        return NAV(scheme_code=self.scheme_code, **node)


async def import_nav(scheme_codes: Iterable[int]) -> list[NAV]:
    """Import NAVs for provided list of mutual funds"""

    scheme_codes = list(scheme_codes)
    logger.info(
        f"Trying to fetch NAVs for {len(scheme_codes)} codes: {scheme_codes}"
    )

    async with ClientSession() as session:
        data = await asyncio.gather(
            *map(
                lambda scheme_code: _NAVImporter(
                    scheme_code, session
                ).get_nav(),
                scheme_codes,
            )
        )

    return sorted(chain.from_iterable(data), reverse=True)
