import io

import pandas as pd

from app.parser import parse_statement_csv


def test_parse_statement_csv_groups_known_vendors_and_recurring_unknowns():
    csv = io.BytesIO(
        b"Date,Merchant,Debit,Category\n"
        b"2026-01-01,Adobe Inc,15000,Software\n"
        b"2026-02-01,Adobe Inc,15000,Software\n"
        b"2026-01-04,Slack Pro,8000,Communication\n"
        b"2026-02-04,Slack Pro,8000,Communication\n"
        b"2026-01-10,Coffee Shop,500,Food\n"
    )
    result = parse_statement_csv(csv)
    assert set(result.columns) == {"product", "category", "monthly_cost", "status", "renewal_days", "seats"}
    assert result.loc[result["product"] == "Adobe Creative Cloud", "monthly_cost"].iloc[0] == 30000
    assert "Coffee Shop" not in result["product"].tolist()


if __name__ == "__main__":
    sample = io.BytesIO(b"Date,Description,Amount\n2026-01-01,Adobe Creative Cloud,-15000\n2026-02-01,Adobe Creative Cloud,-15000\n")
    print(parse_statement_csv(sample).to_string(index=False))
