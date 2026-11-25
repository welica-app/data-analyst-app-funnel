import pandas as pd


EVENT_COLUMNS = [
    "event_id",
    "user_id",
    "event_name",
    "event_time_utc",
    "event_order",
    "segment",
]
SORT_KEY = ["event_time_utc", "event_order"]
MATCH_COLUMNS = ["user_id", "event_id", *SORT_KEY, "segment", "cohort_entry_at"]
SEGMENTS = ["mobile", "desktop"]
TIMESTAMP_PATTERN = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def read_events(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def prepare_events(raw, duplicate_rule):
    if duplicate_rule not in {"event_id", "exact_row"}:
        raise ValueError("duplicate_rule must be event_id or exact_row")
    if list(raw.columns) != EVENT_COLUMNS:
        raise ValueError("Unexpected source columns")
    if raw[["event_id", "user_id", "event_name"]].eq("").any().any():
        raise ValueError("Missing event identifier, user identifier or event name")
    if not raw["segment"].isin(SEGMENTS).all():
        raise ValueError("Unexpected segment")
    if not raw["event_order"].str.fullmatch(r"[1-9]\d*").all():
        raise ValueError("event_order must be a positive integer")

    exact_rows = raw.drop_duplicates()
    if exact_rows["event_id"].duplicated().any():
        raise ValueError("An event_id has conflicting data")
    events = (
        raw.drop_duplicates(subset="event_id")
        if duplicate_rule == "event_id"
        else exact_rows
    ).copy()
    events["event_order"] = events["event_order"].astype("int64")
    if events.duplicated(["user_id", "event_order"]).any():
        raise ValueError("Distinct events have the same event_order for one user")
    if events.groupby("user_id")["segment"].nunique().gt(1).any():
        raise ValueError("A user appears in more than one segment")

    utc_text = events["event_time_utc"]
    timestamps = pd.to_datetime(
        utc_text.where(utc_text.str.fullmatch(TIMESTAMP_PATTERN)),
        format=TIMESTAMP_FORMAT,
        errors="coerce",
        utc=True,
    )
    audit = {
        "source_rows": len(raw),
        "replayed_rows_removed": len(raw) - len(events),
        "invalid_timestamp_rows_removed": int(timestamps.isna().sum()),
        "usable_rows": int(timestamps.notna().sum()),
    }
    events["event_time_utc"] = timestamps
    return events.dropna(subset="event_time_utc").sort_values(SORT_KEY), audit


def first_step(events, event_name, cohort_start, cohort_end):
    start = pd.to_datetime(cohort_start, format="%Y-%m-%d", utc=True)
    end = pd.to_datetime(cohort_end, format="%Y-%m-%d", utc=True)
    if not start < end:
        raise ValueError("Cohort start must be before cohort end")
    eligible = events.loc[
        events["event_name"].eq(event_name)
        & events["event_time_utc"].ge(start)
        & events["event_time_utc"].lt(end)
    ].drop_duplicates(subset="user_id")
    return eligible.assign(cohort_entry_at=eligible["event_time_utc"])[MATCH_COLUMNS]


def next_step(events, previous, event_name, followup_hours):
    prior = previous[["user_id", *SORT_KEY, "cohort_entry_at"]].rename(
        columns={"event_time_utc": "prior_time_utc", "event_order": "prior_order"}
    )
    candidates = events.loc[events["event_name"].eq(event_name)].merge(
        prior, on="user_id", how="inner", validate="many_to_one"
    )
    timestamp = candidates["event_time_utc"]
    after_prior = timestamp.gt(candidates["prior_time_utc"]) | (
        timestamp.eq(candidates["prior_time_utc"])
        & candidates["event_order"].gt(candidates["prior_order"])
    )
    within_followup = timestamp.le(
        candidates["cohort_entry_at"] + pd.Timedelta(hours=followup_hours)
    )
    eligible = candidates.loc[after_prior & within_followup].sort_values(SORT_KEY)
    return eligible.drop_duplicates(subset="user_id")[MATCH_COLUMNS]


def summarise_steps(steps):
    rows = []
    for group in ["overall", *SEGMENTS]:
        previous_users = None
        for position, (event_name, step) in enumerate(steps.items(), start=1):
            user_ids = step["user_id"] if group == "overall" else step.loc[
                step["segment"].eq(group), "user_id"
            ]
            reached_users = user_ids.nunique()
            dropoff_users = (
                None if previous_users is None else previous_users - reached_users
            )
            rows.append({
                "group": group,
                "step_position": position,
                "event_name": event_name,
                "reached_users": reached_users,
                "previous_users": previous_users,
                "dropoff_users": dropoff_users,
                "dropoff_rate": dropoff_users / previous_users if previous_users else None,
            })
            previous_users = reached_users
    return pd.DataFrame(rows)


def matched_events(steps):
    return pd.concat(
        [
            step.assign(step_position=position, event_name=event_name)[
                ["step_position", "event_name", "user_id", "segment", "event_id", *SORT_KEY]
            ]
            for position, (event_name, step) in enumerate(steps.items(), start=1)
        ],
        ignore_index=True,
    )
