"""Data-loading and transformation utilities for the Flask API."""

from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

PREPARED_PRICES_PATH = (
    PROJECT_ROOT / "data" / "processed" / "brent_prices_prepared.csv"
)

MONTHLY_PRICES_PATH = (
    PROJECT_ROOT / "data" / "processed" / "monthly_brent_prices.csv"
)

CHANGE_POINT_RESULTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bayesian_change_point_results.csv"
)

CHANGE_POINT_SUMMARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "bayesian_change_point_summary.csv"
)

EVENT_ASSOCIATION_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "event_association_results.csv"
)

EVENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "events"
    / "key_oil_market_events.csv"
)


class DataServiceError(Exception):
    """Raised when dashboard data cannot be loaded or validated."""


def _read_csv(file_path: Path) -> pd.DataFrame:
    """Read a required CSV file with clear error handling."""

    if not file_path.exists():
        raise DataServiceError(
            f"Required data file was not found: {file_path}"
        )

    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError as error:
        raise DataServiceError(
            f"Data file is empty: {file_path}"
        ) from error
    except pd.errors.ParserError as error:
        raise DataServiceError(
            f"Data file could not be parsed: {file_path}"
        ) from error


def _records_to_json_safe(data: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame into JSON-safe records."""

    cleaned = data.copy()
    cleaned = cleaned.where(pd.notna(cleaned), None)

    return cleaned.to_dict(orient="records")


def load_historical_prices(
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[dict[str, Any]]:
    """Load historical Brent prices with optional date filtering."""

    data = _read_csv(PREPARED_PRICES_PATH)

    required_columns = {
        "Date",
        "Price",
        "Log_Return",
        "Rolling_30D_Volatility",
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise DataServiceError(
            "Historical price data is missing columns: "
            f"{sorted(missing_columns)}"
        )

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
    )

    data = data.dropna(subset=["Date", "Price"])

    if start_date:
        parsed_start = pd.to_datetime(
            start_date,
            errors="coerce",
        )

        if pd.isna(parsed_start):
            raise ValueError(
                "start_date must use a valid date format such as YYYY-MM-DD."
            )

        data = data[data["Date"] >= parsed_start]

    if end_date:
        parsed_end = pd.to_datetime(
            end_date,
            errors="coerce",
        )

        if pd.isna(parsed_end):
            raise ValueError(
                "end_date must use a valid date format such as YYYY-MM-DD."
            )

        data = data[data["Date"] <= parsed_end]

    if start_date and end_date:
        if parsed_start > parsed_end:
            raise ValueError(
                "start_date cannot be later than end_date."
            )

    data = data.sort_values("Date")
    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

    return _records_to_json_safe(data)


def load_monthly_prices() -> list[dict[str, Any]]:
    """Load monthly average Brent prices."""

    data = _read_csv(MONTHLY_PRICES_PATH)

    required_columns = {
        "Date",
        "Monthly_Average_Price",
    }

    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise DataServiceError(
            "Monthly price data is missing columns: "
            f"{sorted(missing_columns)}"
        )

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce",
    )

    data = data.dropna(
        subset=["Date", "Monthly_Average_Price"]
    )

    data["Date"] = data["Date"].dt.strftime("%Y-%m-%d")

    return _records_to_json_safe(data)


def load_change_point_results() -> dict[str, Any]:
    """Load Bayesian change-point metrics and convergence summary."""

    results = _read_csv(CHANGE_POINT_RESULTS_PATH)
    summary = _read_csv(CHANGE_POINT_SUMMARY_PATH)

    if not {"metric", "value"}.issubset(results.columns):
        raise DataServiceError(
            "Change-point results must contain metric and value columns."
        )

    metrics = dict(
        zip(
            results["metric"],
            results["value"],
            strict=False,
        )
    )

    return {
        "metrics": metrics,
        "posterior_summary": _records_to_json_safe(summary),
    }


def load_events(
    category: str | None = None,
) -> list[dict[str, Any]]:
    """Load researched events with optional category filtering."""

    events = _read_csv(EVENTS_PATH)

    required_columns = {
        "event_date",
        "event_name",
        "event_category",
        "event_description",
        "expected_market_channel",
        "source_organization",
    }

    missing_columns = required_columns.difference(events.columns)

    if missing_columns:
        raise DataServiceError(
            f"Event data is missing columns: {sorted(missing_columns)}"
        )

    events["event_date"] = pd.to_datetime(
        events["event_date"],
        errors="coerce",
    )

    events = events.dropna(
        subset=["event_date", "event_name"]
    )

    if category:
        events = events[
            events["event_category"].str.contains(
                category,
                case=False,
                na=False,
            )
        ]

    events = events.sort_values("event_date")
    events["event_date"] = events["event_date"].dt.strftime(
        "%Y-%m-%d"
    )

    return _records_to_json_safe(events)


def load_event_association() -> list[dict[str, Any]]:
    """Load the modeled change-point and nearest-event association."""

    data = _read_csv(EVENT_ASSOCIATION_PATH)

    return _records_to_json_safe(data)


def build_overview() -> dict[str, Any]:
    """Build summary indicators for dashboard cards."""

    prices = _read_csv(PREPARED_PRICES_PATH)
    events = _read_csv(EVENTS_PATH)
    change_results = _read_csv(CHANGE_POINT_RESULTS_PATH)

    metrics = dict(
        zip(
            change_results["metric"],
            change_results["value"],
            strict=False,
        )
    )

    return {
        "observation_count": int(len(prices)),
        "event_count": int(len(events)),
        "minimum_price": round(float(prices["Price"].min()), 2),
        "maximum_price": round(float(prices["Price"].max()), 2),
        "average_price": round(float(prices["Price"].mean()), 2),
        "change_point_date": metrics.get(
            "change_point_date_median"
        ),
        "mean_before": metrics.get("mean_before_median"),
        "mean_after": metrics.get("mean_after_median"),
        "percentage_change": metrics.get(
            "percentage_mean_change"
        ),
    }