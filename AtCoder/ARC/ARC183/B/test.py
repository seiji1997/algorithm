import polars as pl
import pytest
from pathlib import Path

from loader import (
    load_quotation_table,
    load_condition_table,
    merge_condition_info,
)


@pytest.fixture
def input_data_path() -> Path:
    return Path("test_data")


def test_load_quotation_table(input_data_path):
    df = load_quotation_table(input_data_path)
    assert df.shape[0] > 0
    assert set(df.columns) == {
        "ID",
        "stapler",
        "scotch_temp",
        "scotch_time",
        "ink_cycle",
        "tracking_marker",
        "read_crinkle",
    }


def test_load_condition_table(input_data_path):
    df = load_condition_table(input_data_path)
    assert df.shape[0] > 0
    assert set(df.columns) == {
        "scotch_temp",
        "scotch_time",
        "tape",
        "stapler_temp",
    }


def test_merge_condition_info(input_data_path):
    df_q = load_quotation_table(input_data_path)
    df_c = load_condition_table(input_data_path)
    merged_df = merge_condition_info(df_q, df_c)
    assert "tape" in merged_df.columns
    assert "stapler_temp" in merged_df.columns
    assert "scotch_temp" not in merged_df.columns
    assert "scotch_time" not in merged_df.columns
    assert merged_df.shape[0] > 0


import pytest
import pandera as pa
import pandera.typing as pt
from pandera import Column
from pathlib import Path
import polars as pl

from loader import load_quotation_table, load_condition_table


class QuotationSchema(pa.SchemaModel):
    ID: Column[int] = pa.Field(nullable=False)
    stapler: Column[int] = pa.Field(nullable=False)
    scotch_temp: Column[str] = pa.Field(nullable=False)
    scotch_time: Column[str] = pa.Field(nullable=False)
    ink_cycle: Column[float] = pa.Field(nullable=False)
    tracking_marker: Column[float] = pa.Field(nullable=False)
    read_crinkle: Column[float] = pa.Field(nullable=False)

    class Config:
        strict = True


class ConditionSchema(pa.SchemaModel):
    scotch_temp: Column[int] = pa.Field()
    scotch_time: Column[str] = pa.Field()
    tape: Column[int] = pa.Field()
    stapler_temp: Column[float] = pa.Field()

    class Config:
        strict = True


@pytest.fixture
def input_data_path() -> Path:
    return Path("test_data")


def test_quotation_schema(input_data_path):
    df = load_quotation_table(input_data_path)
    pdf = df.to_pandas()
    QuotationSchema.validate(pdf)
    assert True


def test_condition_schema(input_data_path):
    df = load_condition_table(input_data_path)
    pdf = df.to_pandas()
    ConditionSchema.validate(pdf)
    assert True
    
    
    
    
#----------------
import polars as pl

def check_id_consistency_using_print(
    df_result: pl.DataFrame,
    reference_ids: set
):
    """
    df_result には (ID, noise, filename1, filename2) が含まれる想定。
    - 各 ID が1行しかないはずなのに2行以上ある場合 => print でエラー表示
    - reference_ids に含まれる ID が df_result になければ => print でエラー表示
    - 処理は継続 (中断しない)
    """

    # ID列ごとの行数を取得
    df_count = (
        df_result
        .groupby("ID")
        .count()
        .rename({"count": "row_count"})
    )

    # 2行以上あるIDを抽出
    duplicated = df_count.filter(pl.col("row_count") > 1)
    if not duplicated.is_empty():
        for row in duplicated.iter_rows(named=True):
            print(
                f"[ERROR] ID={row['ID']} が {row['row_count']} 行存在します (1行のみ想定)",
                flush=True
            )

    # df_result に含まれるID集合
    actual_ids = set(df_result["ID"].unique().to_list())
    # 参照ID集合から欠けたものを確認
    missing_ids = reference_ids - actual_ids
    if missing_ids:
        print(f"[ERROR] ID={missing_ids} が出力に存在しません", flush=True)

    # ここで例外はraiseしない => printした後も処理続行
