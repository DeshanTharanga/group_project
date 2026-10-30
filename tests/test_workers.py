from datetime import UTC, datetime, time

from app.workers.celery_app import celery_app
from app.workers.tasks.maintenance import occurrence_times


def dt(value):
    return datetime.fromisoformat(value).astimezone(UTC)


def test_colombo_times_become_utc():
    times = occurrence_times(
        dt("2026-10-30T00:00:00+00:00"),
        None,
        [time(8)],
        "Asia/Colombo",
        dt("2026-10-30T00:00:00+00:00"),
        dt("2026-10-31T00:00:00+00:00"),
    )
    assert times == [dt("2026-10-30T02:30:00+00:00")]


def test_nonexistent_dst_time_is_skipped():
    lower = dt("2026-03-08T00:00:00+00:00")
    upper = dt("2026-03-09T00:00:00+00:00")
    assert occurrence_times(lower, None, [time(2, 30)], "America/New_York", lower, upper) == []


def test_dst_fold_generates_one_occurrence():
    lower = dt("2026-11-01T00:00:00+00:00")
    upper = dt("2026-11-02T00:00:00+00:00")
    assert occurrence_times(lower, None, [time(1, 30)], "America/New_York", lower, upper) == [
        dt("2026-11-01T05:30:00+00:00")
    ]


def test_schedule_end_is_inclusive_and_limits_window():
    lower = dt("2026-10-30T00:00:00+00:00")
    end = dt("2026-10-30T08:00:00+00:00")
    assert occurrence_times(
        lower, end, [time(8), time(20)], "UTC", lower, dt("2026-11-01T00:00:00+00:00")
    ) == [end]


def test_broker_messages_use_json_and_ignore_results():
    assert celery_app.conf.accept_content == ["json"]
    assert celery_app.conf.task_ignore_result is True
    assert celery_app.conf.task_acks_late is True
