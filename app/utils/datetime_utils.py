"""
Author: xuyoushun
Email: xuyoushun@bestpay.com.cn
Date: 2026/1/12 10:09
Description:
FilePath: datetime_utils
"""

from __future__ import annotations

from datetime import (
    UTC,
    datetime
)
from collections.abc import Iterable
from zoneinfo import ZoneInfo

SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
_ISO_Z_SUFFIX = "+00:00"


def utc_now() -> datetime:
    """Return the current UTC time as an aware datetime."""
    return datetime.now(UTC)


def shanghai_now() -> datetime:
    """Return the current Asia/Shanghai time as an aware datetime."""
    return utc_now().astimezone(SHANGHAI_TZ)


def ensure_utc(value: datetime) -> datetime:
    """
    Convert a datetime to UTC.

    Naive values are assumed to be in Asia/Shanghai to preserve legacy data.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=SHANGHAI_TZ)
    return value.astimezone(UTC)


def ensure_shanghai(value: datetime) -> datetime:
    """
    Convert a datetime to Asia/Shanghai.

    Naive values are assumed to be in Asia/Shanghai (legacy behaviour).
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=SHANGHAI_TZ)
    return value.astimezone(SHANGHAI_TZ)


def utc_isoformat(value: datetime | None = None) -> str:
    """Return an ISO 8601 string in UTC with a trailing Z suffix."""
    value = ensure_utc(value or utc_now())
    iso_string = value.isoformat()
    if iso_string.endswith(_ISO_Z_SUFFIX):
        return iso_string.replace(_ISO_Z_SUFFIX, "Z")
    return iso_string


def shanghai_isoformat(value: datetime | None = None) -> str:
    """Return an ISO 8601 string in Asia/Shanghai timezone."""
    value = ensure_shanghai(value or shanghai_now())
    return value.isoformat()


def coerce_datetime(value: datetime | None) -> datetime | None:
    """Normalize persisted datetimes to UTC, handling nulls gracefully."""
    if value is None:
        return None
    return ensure_utc(value)


def coerce_any_to_utc_datetime(value: datetime | int | float | str | None) -> datetime | None:
    """
    Convert heterogeneous timestamp representations to an aware UTC datetime.

    Supports:
      * aware or naive datetime objects
      * unix timestamps (seconds) as int/float
      * ISO 8601 strings
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return ensure_utc(value)

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)

    if isinstance(value, str):
        # Attempt to parse ISO 8601 strings.
        try:
            parsed = datetime.fromisoformat(value.replace("Z", _ISO_Z_SUFFIX))
            return ensure_utc(parsed)
        except ValueError:
            # Attempt fallback to numeric string
            try:
                as_number = float(value)
                return datetime.fromtimestamp(as_number, tz=UTC)
            except ValueError:
                raise ValueError(f"Unsupported datetime string format: {value!r}") from None

    raise TypeError(f"Unsupported datetime value: {value!r}")


def normalize_iterable_to_utc(values: Iterable[datetime | None]) -> list[datetime | None]:
    """Normalize each datetime in iterable to UTC."""
    return [coerce_datetime(item) if isinstance(item, datetime) else None for item in values]


__all__ = [
    "UTC",
    "SHANGHAI_TZ",
    "utc_now",
    "shanghai_now",
    "ensure_utc",
    "ensure_shanghai",
    "utc_isoformat",
    "shanghai_isoformat",
    "coerce_datetime",
    "coerce_any_to_utc_datetime",
    "normalize_iterable_to_utc",
]