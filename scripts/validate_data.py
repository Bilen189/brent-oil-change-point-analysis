"""Validate the raw Brent oil price dataset."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "BrentOilPrices.csv"
EVENTS_PATH = PROJECT_ROOT / "data" / "events" / "key_oil_market_events.csv"


def load_and_validate_data(file_path: Path) -> pd.DataFrame:
    """Load the Brent oil dataset and perform basic validation."""

    if not file_path.exists():
        raise FileNotFoundError(f"Dataset was not found at: {file_path}")

    data = pd.read_csv(file_path)

    required_columns = {"Date", "Price"}
    missing_columns = required_columns.difference(data.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_columns)}"
        )

    # The supplied file contains more than one date format.
    data["Date"] = pd.to_datetime(
        data["Date"],
        format="mixed",
        dayfirst=True,
        errors="coerce",
    )

    data["Price"] = pd.to_numeric(data["Price"], errors="coerce")

    print("Dataset validation results")
    print("-" * 40)
    print(f"Rows: {len(data):,}")
    print(f"Columns: {len(data.columns)}")
    print(f"Start date: {data['Date'].min()}")
    print(f"End date: {data['Date'].max()}")
    print(f"Missing dates: {data['Date'].isna().sum()}")
    print(f"Missing prices: {data['Price'].isna().sum()}")
    print(f"Duplicate rows: {data.duplicated().sum()}")
    print(f"Minimum price: ${data['Price'].min():.2f}")
    print(f"Maximum price: ${data['Price'].max():.2f}")

    return data

def validate_events(file_path: Path) -> pd.DataFrame:
    """Validate the researched oil-market event dataset."""

    if not file_path.exists():
        raise FileNotFoundError(f"Events dataset was not found at: {file_path}")

    events = pd.read_csv(file_path)
    events["event_date"] = pd.to_datetime(
        events["event_date"],
        errors="coerce",
    )

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
        raise ValueError(
            f"Events dataset is missing columns: {sorted(missing_columns)}"
        )

    print("\nEvent dataset validation")
    print("-" * 40)
    print(f"Number of events: {len(events)}")
    print(f"First event: {events['event_date'].min()}")
    print(f"Last event: {events['event_date'].max()}")
    print(f"Missing event dates: {events['event_date'].isna().sum()}")

    return events

if __name__ == "__main__":
    load_and_validate_data(DATA_PATH)
    validate_events(EVENTS_PATH)

