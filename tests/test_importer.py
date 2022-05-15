""" Test the NAV import functionality"""

import pytest
from loguru import logger

from src.importer import import_nav

SCHEME_CODES = [118585, 122639]


@pytest.mark.asyncio
async def test_nav_import() -> None:
    """Test importing NAVs for sample mutual funds"""

    nav_data = await import_nav(SCHEME_CODES)

    logger.info(f"NAV data: {nav_data}")
    assert len(nav_data) > 0
