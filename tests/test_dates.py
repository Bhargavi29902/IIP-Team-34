from datetime import date

from app.services.dates import date_warnings, resolve_due_date

MON = date(2026, 11, 2)


def test_weekday_after_sent_date():
    assert resolve_due_date("Thursday", MON).value == date(2026, 11, 5)


def test_tomorrow_and_explicit():
    assert resolve_due_date("tomorrow", MON).value == date(2026, 11, 3)
    assert resolve_due_date("15 November 2026", MON).value == date(2026, 11, 15)


def test_vague_is_never_guessed():
    for phrase in ("as soon as possible", "soon", "next week", None, ""):
        r = resolve_due_date(phrase, MON)
        assert r.value is None and r.ambiguous


def test_holiday_and_weekend_warnings():
    hol = {date(2026, 12, 25): "Christmas Day"}
    assert any("holiday" in w for w in date_warnings(date(2026, 12, 25), hol))
    assert any("Saturday" in w for w in date_warnings(date(2026, 11, 7), {}))
