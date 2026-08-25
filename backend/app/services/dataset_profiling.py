"""Real pandas-based profiling — Phase 1 §9/§25. Runs synchronously, which
is honest for the ≤50MB sync path the architecture describes; there is no
Celery/background-worker setup in this environment yet for the async path
larger files would need."""

import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict:
    columns = []
    numeric_summary = {}
    outliers = {}

    for col in df.columns:
        series = df[col]
        missing = int(series.isna().sum())
        columns.append(
            {
                "name": col,
                "dtype": str(series.dtype),
                "missing_count": missing,
                "missing_pct": round(missing / len(df) * 100, 2) if len(df) else 0.0,
                "unique_count": int(series.nunique()),
            }
        )

        if pd.api.types.is_numeric_dtype(series):
            desc = series.describe()
            numeric_summary[col] = {k: (None if pd.isna(v) else round(float(v), 4)) for k, v in desc.items()}

            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            if iqr > 0:
                lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                outliers[col] = int(((series < lower) | (series > upper)).sum())
            else:
                outliers[col] = 0

    numeric_cols = df.select_dtypes(include="number").columns
    correlations = {}
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr(numeric_only=True)
        correlations = {
            col: {other: (None if pd.isna(val) else round(float(val), 3)) for other, val in row.items()}
            for col, row in corr_matrix.to_dict(orient="index").items()
        }

    return {
        "row_count": len(df),
        "column_count": len(df.columns),
        "columns": columns,
        "numeric_summary": numeric_summary,
        "correlations": correlations,
        "outliers": outliers,
    }
