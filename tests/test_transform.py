import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from transform import (
    load_raw,
    remove_negatives,
    deduplicate,
    add_derived_columns,
    save_parquet,
    transform_pipeline,
)


def test_remove_negatives_drops_negative_quantity():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [100, -5], "INDICATIVE_COST": [50.0, 10.0]})
    result = remove_negatives(df)
    assert len(result) == 1
    assert result["TOTAL_QUANITY_IN_VMP_UNIT"].min() >= 0


def test_remove_negatives_drops_negative_cost():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [100, 200], "INDICATIVE_COST": [50.0, -10.0]})
    assert len(remove_negatives(df)) == 1


def test_remove_negatives_keeps_null_cost():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [100, 200], "INDICATIVE_COST": [50.0, None]})
    assert len(remove_negatives(df)) == 2


def test_remove_negatives_keeps_all_valid_rows():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [1, 2, 3], "INDICATIVE_COST": [10.0, 20.0, 30.0]})
    assert len(remove_negatives(df)) == 3


def test_remove_negatives_keeps_zero():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [0], "INDICATIVE_COST": [0.0]})
    assert len(remove_negatives(df)) == 1


def test_deduplicate_removes_exact_duplicate():
    df = pd.DataFrame({"YEAR_MONTH": [202605, 202605], "ODS_CODE": ["RA2", "RA2"], "VMP_SNOMED_CODE": ["123", "123"]})
    assert len(deduplicate(df)) == 1


def test_deduplicate_keeps_different_trusts():
    df = pd.DataFrame({"YEAR_MONTH": [202605, 202605], "ODS_CODE": ["RA2", "RTH"], "VMP_SNOMED_CODE": ["123", "123"]})
    assert len(deduplicate(df)) == 2


def test_derived_columns_are_added():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [10, 20, 30, 40], "INDICATIVE_COST": [100.0, 200.0, 300.0, 400.0]})
    result = add_derived_columns(df)
    assert "cost_per_unit" in result.columns
    assert "cost_category" in result.columns


def test_cost_per_unit_is_correct():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [10, 20, 40, 50], "INDICATIVE_COST": [100.0, 200.0, 400.0, 500.0]})
    assert add_derived_columns(df)["cost_per_unit"].iloc[0] == 10.0


def test_cost_per_unit_handles_zero_quantity():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [0, 10, 20, 30], "INDICATIVE_COST": [50.0, 150.0, 250.0, 400.0]})
    assert pd.isna(add_derived_columns(df)["cost_per_unit"].iloc[0])


def test_cost_category_has_three_levels():
    df = pd.DataFrame({"TOTAL_QUANITY_IN_VMP_UNIT": [1, 2, 3, 4, 5, 6, 7, 8], "INDICATIVE_COST": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0]})
    cats = set(add_derived_columns(df)["cost_category"].dropna().unique())
    assert cats.issubset({"low", "medium", "high"})


def test_load_raw_reads_csv(tmp_path):
    csv = tmp_path / "sample.csv"
    csv.write_text("YEAR_MONTH,ODS_CODE,VMP_SNOMED_CODE,VMP_PRODUCT_NAME,UNIT_OF_MEASURE_IDENTIFIER,UNIT_OF_MEASURE_NAME,TOTAL_QUANITY_IN_VMP_UNIT,INDICATIVE_COST\n202605,RA2,123,Aspirin,428,TABLET,100,50.0\n")
    df = load_raw(str(csv))
    assert len(df) == 1
    assert df["ODS_CODE"].dtype == object or str(df["ODS_CODE"].dtype) in ("string", "str")


def test_save_parquet_writes_file(tmp_path):
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    out = tmp_path / "out.parquet"
    save_parquet(df, str(out))
    assert len(pd.read_parquet(out)) == 2


def test_transform_pipeline_end_to_end(tmp_path):
    csv = tmp_path / "sample.csv"
    csv.write_text("YEAR_MONTH,ODS_CODE,VMP_SNOMED_CODE,VMP_PRODUCT_NAME,UNIT_OF_MEASURE_IDENTIFIER,UNIT_OF_MEASURE_NAME,TOTAL_QUANITY_IN_VMP_UNIT,INDICATIVE_COST\n202605,RA2,123,Aspirin,428,TABLET,100,50.0\n202605,RTH,456,Ibuprofen,428,TABLET,200,80.0\n202605,RA2,789,Paracetamol,428,TABLET,-5,10.0\n")
    out = tmp_path / "out.parquet"
    result = transform_pipeline(str(csv), str(out))
    assert len(result) == 2
    assert "cost_per_unit" in result.columns
    assert out.exists()
