import pandas as pd
import numpy as np
import sys
import os

# Let the test file find your code in the src folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from transform import remove_negatives, deduplicate, add_derived_columns


# ---- remove_negatives ----

def test_remove_negatives_drops_negative_quantity():
    """Rows with a negative quantity should be removed."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [100, -5],
        "INDICATIVE_COST": [50.0, 10.0],
    })
    result = remove_negatives(df)
    assert len(result) == 1
    assert result["TOTAL_QUANITY_IN_VMP_UNIT"].min() >= 0


def test_remove_negatives_drops_negative_cost():
    """Rows with a negative cost should be removed."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [100, 200],
        "INDICATIVE_COST": [50.0, -10.0],
    })
    result = remove_negatives(df)
    assert len(result) == 1


def test_remove_negatives_keeps_null_cost():
    """A row with a null cost but valid quantity should be kept."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [100, 200],
        "INDICATIVE_COST": [50.0, None],
    })
    result = remove_negatives(df)
    assert len(result) == 2


def test_remove_negatives_keeps_all_valid_rows():
    """If nothing is negative, no rows are removed."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [1, 2, 3],
        "INDICATIVE_COST": [10.0, 20.0, 30.0],
    })
    result = remove_negatives(df)
    assert len(result) == 3


def test_remove_negatives_keeps_zero():
    """Zero is not negative, so a zero quantity row should be kept."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [0],
        "INDICATIVE_COST": [0.0],
    })
    result = remove_negatives(df)
    assert len(result) == 1


# ---- deduplicate ----

def test_deduplicate_removes_exact_duplicate():
    """Two rows with the same key should collapse to one."""
    df = pd.DataFrame({
        "YEAR_MONTH": [202605, 202605],
        "ODS_CODE": ["RA2", "RA2"],
        "VMP_SNOMED_CODE": ["123", "123"],
    })
    result = deduplicate(df)
    assert len(result) == 1


def test_deduplicate_keeps_different_trusts():
    """Same medicine at different trusts is not a duplicate."""
    df = pd.DataFrame({
        "YEAR_MONTH": [202605, 202605],
        "ODS_CODE": ["RA2", "RTH"],
        "VMP_SNOMED_CODE": ["123", "123"],
    })
    result = deduplicate(df)
    assert len(result) == 2


# ---- add_derived_columns ----

def test_derived_columns_are_added():
    """cost_per_unit and cost_category columns should exist after enrichment."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [10, 20, 30, 40],
        "INDICATIVE_COST": [100.0, 200.0, 300.0, 400.0],
    })
    result = add_derived_columns(df)
    assert "cost_per_unit" in result.columns
    assert "cost_category" in result.columns


def test_cost_per_unit_is_correct():
    """cost_per_unit should equal cost divided by quantity."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [10, 20, 40, 50],
        "INDICATIVE_COST": [100.0, 200.0, 400.0, 500.0],
    })
    result = add_derived_columns(df)
    # first row: 100 / 10 = 10
    assert result["cost_per_unit"].iloc[0] == 10.0


def test_cost_per_unit_handles_zero_quantity():
    """A zero quantity must not crash; cost_per_unit should be NaN."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [0, 10, 20, 30],
        "INDICATIVE_COST": [50.0, 150.0, 250.0, 400.0],
    })
    result = add_derived_columns(df)
    # dividing by zero should give NaN, not infinity or an error
    assert pd.isna(result["cost_per_unit"].iloc[0])


def test_cost_category_has_three_levels():
    """cost_category should use the low/medium/high labels."""
    df = pd.DataFrame({
        "TOTAL_QUANITY_IN_VMP_UNIT": [1, 2, 3, 4, 5, 6, 7, 8],
        "INDICATIVE_COST": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0],
    })
    result = add_derived_columns(df)
    categories = set(result["cost_category"].dropna().unique())
    assert categories.issubset({"low", "medium", "high"})
# ---- load_raw and save_parquet (round-trip via a temp file) ----

def test_load_raw_reads_csv(tmp_path):
    """load_raw should read a CSV and keep code columns as text."""
    from transform import load_raw
    csv = tmp_path / "sample.csv"
    csv.write_text(
        "YEAR_MONTH,ODS_CODE,VMP_SNOMED_CODE,VMP_PRODUCT_NAME,"
        "UNIT_OF_MEASURE_IDENTIFIER,UNIT_OF_MEASURE_NAME,"
        "TOTAL_QUANITY_IN_VMP_UNIT,INDICATIVE_COST\n"
        "202605,RA2,123,Aspirin,428,TABLET,100,50.0\n"
    )
    df = load_raw(str(csv))
    assert len(df) == 1
        # kept as text (not converted to a number) — accept object or the newer string dtype
    assert df["ODS_CODE"].dtype == object or str(df["ODS_CODE"].dtype) in ("string", "str")


def test_save_parquet_writes_file(tmp_path):
    """save_parquet should write a readable Parquet file."""
    from transform import save_parquet
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = tmp_path / "out.parquet"
    save_parquet(df, str(out))
    # read it back and confirm it matches
    reloaded = pd.read_parquet(out)
    assert len(reloaded) == 2