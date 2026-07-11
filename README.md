# Brent Oil Change Point Analysis

## Project Overview

This project investigates structural changes in historical Brent crude oil
prices and examines whether detected changes align with major geopolitical,
economic, and oil-market events.

The analysis is developed for Birhan Energies to support investors,
policymakers, and energy companies in understanding oil price instability and
making data-informed decisions.

## Business Objective

The main objectives are to:

1. Examine historical trends and volatility in Brent oil prices.
2. Identify statistically significant structural changes in the price series.
3. Compare detected change points with major geopolitical, economic, and OPEC events.
4. Quantify changes in price behaviour before and after identified change points.
5. Communicate the results through a written report and interactive dashboard.

## Dataset

The project uses daily historical Brent crude oil prices expressed in US
dollars per barrel. The supplied dataset contains observations from May 1987
to November 2022.

## Project Structure

```text
├── .github/workflows/
├── .vscode/
├── data/
│   ├── raw/
│   ├── processed/
│   └── events/
├── notebooks/
├── reports/
│   └── figures/
├── scripts/
├── src/
├── tests/
├── .gitignore
├── README.md
└── requirements.txt