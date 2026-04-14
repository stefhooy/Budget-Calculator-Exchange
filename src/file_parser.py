"""
file_parser.py — handles reading uploaded JSON, CSV, and Excel files into expense dicts.
"""
import json
import pandas as pd
from datetime import date

from config import MONTH_MAP
from utils import _parse_amount, _detect_currency


def _df_to_expenses(df: pd.DataFrame) -> list[dict]:
    cols = [c.strip() for c in df.columns]
    df.columns = cols

    # App export format
    if "Amount" in cols and "Description" in cols:
        return [
            {
                "Amount":      float(row.get("Amount", 0)),
                "Currency":    str(row.get("Currency", "EUR")),
                "Description": str(row.get("Description", "")),
                "Category":    str(row.get("Category", "Other")),
                "Date":        str(row.get("Date", str(date.today()))),
            }
            for _, row in df.iterrows()
        ]

    # Legacy format (statswinter24.csv)
    if "Spending" in cols and "Type of Expense" in cols:
        expenses = []
        for _, row in df.iterrows():
            raw_spending = str(row.get("Spending", "0"))
            amount = _parse_amount(raw_spending)
            if amount == 0:
                continue
            month_str = str(row.get("Month", "")).strip().lower()
            year = str(row.get("Year", "2024")).strip()
            expenses.append({
                "Amount":      amount,
                "Currency":    _detect_currency(raw_spending),
                "Description": str(row.get("Country", "")).strip(),
                "Category":    str(row.get("Type of Expense", "Other")).strip(),
                "Date":        f"{year}-{MONTH_MAP.get(month_str, '01')}-01",
            })
        return expenses

    return []


def parse_uploaded_file(uploaded_file):
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".json"):
            data = json.load(uploaded_file)
            if "expenses" not in data:
                return None, "JSON must contain an 'expenses' key."
            return data, None

        elif name.endswith(".csv"):
            expenses = _df_to_expenses(pd.read_csv(uploaded_file))
            return {"initial_budget": None, "exchange_duration": None,
                    "budget_currency": "EUR", "expenses": expenses}, None

        elif name.endswith((".xlsx", ".xls")):
            expenses = _df_to_expenses(pd.read_excel(uploaded_file))
            return {"initial_budget": None, "exchange_duration": None,
                    "budget_currency": "EUR", "expenses": expenses}, None

        return None, "Unsupported file type."
    except Exception as e:
        return None, str(e)
