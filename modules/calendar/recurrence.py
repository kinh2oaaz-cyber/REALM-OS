"""Recurring-event expansion.

Given a base event and a [range_start, range_end] window, produce the
concrete occurrences. Supports DAILY/WEEKLY/MONTHLY/YEARLY with
interval, count, until, and WEEKLY byweekday. Non-recurring events are
returned if they intersect the window.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, time, timedelta

from .models import CalendarEvent

MAX_OCCURRENCES = 1000


def _parse_dt(value: str, default_time: time | None = None) -> datetime:
    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            if fmt == "%Y-%m-%d" and default_time is not None:
                return datetime.combine(dt.date(), default_time)
            return dt
        except ValueError:
            continue
    # date-only fallback
    try:
        return datetime.combine(date.fromisoformat(value[:10]), default_time or time(0, 0))
    except ValueError:
        return datetime.now()


def _parse_until(value: str | None) -> datetime | None:
    if not value:
        return None
    return _parse_dt(value, time(23, 59, 59))


def expand_events(
    events: list[CalendarEvent],
    range_start: datetime,
    range_end: datetime,
) -> list[CalendarEvent]:
    """Return concrete occurrences intersecting [range_start, range_end)."""
    out: list[CalendarEvent] = []
    for event in events:
        start = _parse_dt(event.start)
        end = _parse_dt(event.end) if event.end else start + timedelta(hours=1)
        duration = end - start
        rec = event.recurrence
        if rec.freq == "NONE" or not rec.freq:
            if start < range_end and end >= range_start:
                out.append(event)
            continue
        for occ_start in _iter_occurrences(event, start, range_end):
            occ_end = occ_start + duration
            if occ_start < range_end and occ_end >= range_start:
                out.append(replace(event, start=_fmt(occ_start), end=_fmt(occ_end)))
    out.sort(key=lambda e: e.start)
    return out


def _iter_occurrences(event: CalendarEvent, start: datetime, hard_end: datetime):
    rec = event.recurrence
    until = _parse_until(rec.until)
    limit_end = hard_end
    if until is not None:
        limit_end = min(limit_end, until + timedelta(days=1))
    interval = max(1, rec.interval)
    produced = 0
    max_count = rec.count if rec.count and rec.count > 0 else MAX_OCCURRENCES

    if rec.freq == "WEEKLY" and rec.byweekday:
        # iterate weeks, emit selected weekdays
        weekday_set = {d % 7 for d in rec.byweekday}
        # start from the week containing `start`
        day = start.date() - timedelta(days=start.weekday())
        base_week = day
        cur = start
        seen = 0
        while cur <= limit_end and produced < max_count and seen < MAX_OCCURRENCES:
            seen += 1
            week_index = ((cur.date() - base_week).days // 7)
            if week_index % interval == 0 and cur.weekday() in weekday_set and cur >= start:
                yield cur
                produced += 1
            cur += timedelta(days=1)
        return

    cur = start
    seen = 0
    while cur <= limit_end and produced < max_count and seen < MAX_OCCURRENCES:
        seen += 1
        yield cur
        produced += 1
        cur = _advance(cur, rec.freq, interval)


def _advance(cur: datetime, freq: str, interval: int) -> datetime:
    if freq == "DAILY":
        return cur + timedelta(days=interval)
    if freq == "WEEKLY":
        return cur + timedelta(weeks=interval)
    if freq == "MONTHLY":
        return _add_months(cur, interval)
    if freq == "YEARLY":
        try:
            return cur.replace(year=cur.year + interval)
        except ValueError:  # Feb 29
            return cur.replace(year=cur.year + interval, day=28)
    return cur + timedelta(days=interval)


def _add_months(cur: datetime, months: int) -> datetime:
    month = cur.month - 1 + months
    year = cur.year + month // 12
    month = month % 12 + 1
    day = min(cur.day, _days_in_month(year, month))
    return cur.replace(year=year, month=month, day=day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        return 31
    return (date(year, month + 1, 1) - date(year, month, 1)).days


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")
