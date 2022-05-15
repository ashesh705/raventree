""" Fetch NAVs for provided list of Mutual Funds"""

import argparse
import asyncio
import csv
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

from loguru import logger

from src.importer import import_nav
from src.nav import NAV

_DATE_FORMAT = "%Y%m%d"
_MIN_DATE = date(2020, 1, 1)


def to_date(s: str) -> date:
    """Convert string input into python native date"""

    return datetime.strptime(s, _DATE_FORMAT).date()


def _get_output_file(file: Optional[str]) -> Path:
    """Get the output file to write the data"""

    if file is None:
        return Path(gettempdir()) / f"NAV_{date.today()}.csv"

    return Path(file)


def _write_to_file(file: Path, data: Iterable[NAV]) -> None:
    """Write list of NAVs to the specified file"""

    data = list(data)

    with file.open("w", newline="") as f:
        w = csv.DictWriter(
            f, fieldnames=["scheme_code", "scheme_name", "nav_date", "nav"]
        )
        w.writerows([d.dict() for d in data])

    logger.info(f"Wrote {len(data)} rows to {file}")


async def main(inputs: argparse.Namespace) -> None:
    """Main control flow of the script"""

    scheme_codes: list[int] = inputs.codes
    nav_data = await import_nav(scheme_codes)

    min_date = inputs.min_date or _MIN_DATE
    max_date = inputs.max_date or date.today()

    filtered_data = filter(
        lambda n: (n.nav_date >= min_date) and (n.nav_date <= max_date),
        nav_data,
    )

    out_file = _get_output_file(inputs.out_file)
    _write_to_file(out_file, filtered_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Fetch NAVs for a list of Mutual Funds")

    parser.add_argument(
        "--codes",
        nargs="+",
        type=int,
        required=True,
        help="List of AMFI scheme codes for the mutual funds",
    )

    parser.add_argument(
        "--min_date",
        type=to_date,
        help="Earliest date to fetch NAVs for, in YYYYMMDD format",
    )
    parser.add_argument(
        "--max-date",
        type=to_date,
        help="Latest date to fetch NAVs for, in YYYYMMDD format",
    )

    parser.add_argument(
        "--out_file", help="Full path of file to save the NAVs to"
    )

    args = parser.parse_args()
    asyncio.run(main(args))
