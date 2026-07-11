"""Validate the raw Brent oil price dataset."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "BrentOilPrices.csv"


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


if __name__ == "__main__":
    load_and_validate_data(DATA_PATH)