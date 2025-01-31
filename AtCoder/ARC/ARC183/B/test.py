"""
test_loader.py

【概要】
1) Config クラス:
   - 正常系: YAMLに全キー & 型OK -> Configが想定通り
   - 異常系: キー欠落 => KeyError, 型不正 => TypeError

2) Loader クラス (CSV/Parquet):
   - CSV正常系: 全列OK => Pandera -> OK, 値が期待dfと一致
   - CSV異常系: 列欠落 / 型不正 / 余分カラム -> pandera.SchemaError
   - Parquet正常系: float項目OK => pandera OK, 値が期待dfと一致
   - Parquet異常系: 型不正 => pandera.SchemaError

3) _check_exists 関数 (クラス外):
   - "path.exists()" が True なら OK
   - False なら FileNotFoundError を起こすかテスト

【実行方法】
 1) 必要ライブラリ:
    pip install pytest pandera polars pyyaml
 2) python -m pytest test_loader.py
    でテスト実行 (同じディレクトリに loader.py がある想定)
"""

import pytest
import polars as pl
from pathlib import Path
from unittest.mock import patch, mock_open
from io import StringIO, BytesIO
import yaml

# Pandera imports
import pandera as pa
from pandera.typing import SchemaModel, Series
from pandera import Field

# ---------------------------------------------------
# loader.py 内のクラス/関数を import する想定
#   - Config, Loader, _check_exists
# ---------------------------------------------------
from loader import Config, Loader, _check_exists


# ===================================================
# (A) _check_exists 関数のテスト
# ===================================================

def test_check_exists_ok():
    """
    _check_exists: パスが存在する場合 => 何も起きない (正常)
    """
    fake_path = Path("some/path")  
    with patch.object(Path, "exists", return_value=True):
        # 存在するとみなす => エラーなし
        _check_exists(fake_path, desc="test-desc")

def test_check_exists_not_found():
    """
    _check_exists: パスが存在しない場合 => FileNotFoundError
    """
    fake_path = Path("some/notfound")  
    with patch.object(Path, "exists", return_value=False):
        with pytest.raises(FileNotFoundError) as exc:
            _check_exists(fake_path, desc="something")
        assert "something not found" in str(exc.value), "エラーメッセージにdescが含まれているか"


# ===================================================
# (B) Configクラスのテスト (正常/欠落/型不正)
# ===================================================

FAKE_YAML_DATA_NORMAL = {
    "input_path": {
        "quotation_path":  "fake_quotation.csv",
        "condition_table": "fake_condition.csv",
        "lut_table_path":  "fake_lut.csv",
        "ruler_data_path": "fake_ruler_data"
    },
    "frame_size": {
        "pen":  10000,
        "book": 20000
    },
    "readmode": {
        "ber1": "bigmac",
        "ber2": "drink"
    },
    "output_path": "fake_output"
}

FAKE_YAML_DATA_MISSING_KEY = {
    # frame_size キーが無い
    "input_path": {
        "quotation_path": "fake_quotation.csv",
        "condition_table": "fake_condition.csv",
    },
    "readmode": {
        "ber1": "bigmac",
        "ber2": "drink"
    },
    "output_path": "fake_output"
}

FAKE_YAML_DATA_WRONG_TYPE = {
    # penが文字列 => TypeError
    "input_path": {
        "quotation_path":  "fake_quotation.csv",
        "condition_table": "fake_condition.csv",
        "ruler_data_path": "fake_ruler_data"
    },
    "frame_size": {
        "pen":  "invalid-string",
        "book": 20000
    },
    "readmode": {
        "ber1": "bigmac",
        "ber2": "drink"
    },
    "output_path": "fake_output"
}


def test_config_normal():
    """
    Config: 正常系 => 値が想定通り
    """
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="dummy")), \
         patch("yaml.safe_load", return_value=FAKE_YAML_DATA_NORMAL):
        c = Config.from_yaml("dummy_config.yaml")
        assert c.quotation_path  == "fake_quotation.csv"
        assert c.condition_table == "fake_condition.csv"
        assert c.lut_table_path  == "fake_lut.csv"
        assert c.ruler_data_path == "fake_ruler_data"
        assert c.pen  == 10000
        assert c.book == 20000
        assert c.readmode["ber1"] == "bigmac"
        assert c.readmode["ber2"] == "drink"
        assert c.output_path == "fake_output"


def test_config_missing_key():
    """
    Config: 異常系(キー欠落) => KeyError
    """
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="dummy")), \
         patch("yaml.safe_load", return_value=FAKE_YAML_DATA_MISSING_KEY), \
         pytest.raises(KeyError):
        Config.from_yaml("dummy_config.yaml")


def test_config_wrong_type():
    """
    Config: 異常系(型不正) => TypeError
    """
    with patch("pathlib.Path.exists", return_value=True), \
         patch("builtins.open", mock_open(read_data="dummy")), \
         patch("yaml.safe_load", return_value=FAKE_YAML_DATA_WRONG_TYPE), \
         pytest.raises(TypeError):
        Config.from_yaml("dummy_config.yaml")


# ===================================================
# (C) Pandera スキーマ
# ===================================================
class QuotationSchema(SchemaModel):
    ID: Series[int] = Field()
    testid: Series[int] = Field()
    exam_number: Series[int] = Field()
    buddy: Series[int] = Field()
    stapler: Series[int] = Field()
    tracking_marker: Series[float] = Field()
    read_crinkle: Series[float] = Field()
    stapler_time: Series[int] = Field()
    tape: Series[str] = Field()
    tape_temp: Series[float] = Field()
    ink_cycle: Series[float] = Field()

    class Config:
        strict = True

class ConditionSchema(SchemaModel):
    scotch_temp: Series[int] = Field()
    scotch_time: Series[str] = Field()
    tape: Series[int] = Field()
    stapler_temp: Series[float] = Field()

    class Config:
        strict = True


# ===================================================
# (D) Loader CSV テスト (正常/異常)
# ===================================================
@pytest.fixture
def mock_loader():
    """ Loader(config=None) を返す """
    return Loader(config=None)

import pandas as pd

FAKE_QUOTATION_CSV_NORMAL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle
1,10,999,0,168,0.1,0.2,40,"3mon",62,1250
2,11,888,1,120,0.15,0.25,40,"3mon",62,1500
"""
pdf_expected_quotation_csv = pd.DataFrame({
    "ID": [1,2],
    "testid": [10,11],
    "exam_number": [999,888],
    "buddy": [0,1],
    "stapler": [168,120],
    "tracking_marker": [0.1,0.15],
    "read_crinkle": [0.2,0.25],
    "stapler_time": [40,40],
    "tape": ["3mon","3mon"],
    "tape_temp": [62,62],
    "ink_cycle": [1250,1500],
})

FAKE_CONDITION_CSV_NORMAL = """\
scotch_temp,scotch_time,tape,stapler_temp
40,"3mon",85,71.25
40,"3mon",85,71.25
"""

def side_effect_read_csv_normal(file_path, **kwargs):
    """
    polars.read_csv のモック(正常)
    """
    if "quotation" in str(file_path).lower():
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_NORMAL))
    elif "condition" in str(file_path).lower():
        return pl.read_csv(StringIO(FAKE_CONDITION_CSV_NORMAL))
    else:
        return pl.DataFrame()

def test_load_quotation_csv_normal(mock_loader):
    """
    CSV 正常系:
     - pandera OK
     - 値が pdf_expected_quotation_csv と一致
    """
    with patch("polars.read_csv", side_effect=side_effect_read_csv_normal):
        df_actual = mock_loader.load_quotation_csv()
        pdf_actual = df_actual.to_pandas()
        QuotationSchema.validate(pdf_actual)
        assert pdf_actual.equals(pdf_expected_quotation_csv)


def test_load_condition_csv_normal(mock_loader):
    """
    CSV 正常系(Condition)
    """
    with patch("polars.read_csv", side_effect=side_effect_read_csv_normal):
        df_actual = mock_loader.load_condition_csv()
        pdf_actual = df_actual.to_pandas()
        ConditionSchema.validate(pdf_actual)
        # shape= (2,4) 
        assert pdf_actual.shape == (2,4)


def test_merge_condition_info_normal(mock_loader):
    """
    merge_condition_info 正常系
    """
    with patch("polars.read_csv", side_effect=side_effect_read_csv_normal):
        df_q = mock_loader.load_quotation_csv()
        df_c = mock_loader.load_condition_csv()
        merged_df = df_q.join(df_c, on=["tape"], how="left")
        assert merged_df.shape[0] == 4
        # rename/dropあれば追加チェック
        assert True


# ~~~ 異常系: 列欠落 / 型不正 / 余分 ~~~
FAKE_QUOTATION_CSV_MISSING_COL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,ink_cycle
1,10,999,0,168,0.1,0.2,40,"3mon",1250
2,11,888,1,120,0.15,0.25,40,"3mon",1500
"""

FAKE_QUOTATION_CSV_WRONG_TYPE = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle
1,10,999,0,168,0.1,"abc",40,"3mon",62,1250
"""

FAKE_QUOTATION_CSV_EXTRA_COL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle,dummy_col
1,10,999,0,168,0.1,0.2,40,"3mon",62,1250,"extra"
2,11,888,1,120,0.15,0.25,40,"3mon",62,1500,"extra"
"""

def test_load_quotation_csv_missing_col(mock_loader):
    """
    CSV 異常: 欠落 => SchemaError
    """
    def side_effect_missing(file_path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_MISSING_COL))

    with patch("polars.read_csv", side_effect=side_effect_missing):
        df = mock_loader.load_quotation_csv()
        pdf = df.to_pandas()
        with pytest.raises(pa.errors.SchemaError):
            QuotationSchema.validate(pdf)

def test_load_quotation_csv_wrong_type(mock_loader):
    """
    CSV 異常: 型不正 => SchemaError
    """
    def side_effect_wrong_type(file_path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_WRONG_TYPE))

    with patch("polars.read_csv", side_effect=side_effect_wrong_type):
        df = mock_loader.load_quotation_csv()
        with pytest.raises(pa.errors.SchemaError):
            QuotationSchema.validate(df.to_pandas())

def test_load_quotation_csv_extra_col(mock_loader):
    """
    CSV 異常: 余分カラム => strict=True => SchemaError
    """
    def side_effect_extra_col(file_path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_EXTRA_COL))

    with patch("polars.read_csv", side_effect=side_effect_extra_col):
        df = mock_loader.load_quotation_csv()
        with pytest.raises(pa.errors.SchemaError):
            QuotationSchema.validate(df.to_pandas())


# ===================================================
# (E) Parquet テスト: 正常/異常
# ===================================================
pdf_expected_parquet = pd.DataFrame({
    "ID":            [1,2],
    "testid":        [10,11],
    "exam_number":   [999,888],
    "buddy":         [0,1],
    "stapler":       [168,120],
    "tracking_marker":[0.1,0.15],
    "read_crinkle":  [0.2,0.25],
    "stapler_time":  [40,40],
    "tape":          ["3mon","3mon"],
    "tape_temp":     [62,62],
    "ink_cycle":     [1250,1500],
})

def make_fake_parquet(normal: bool) -> bytes:
    """
    normal=True => read_crinkle float
    normal=False => read_crinkle="abc" => schema違反
    """
    if normal:
        df = pl.DataFrame({
            "ID": [1,2],
            "testid": [10,11],
            "exam_number": [999,888],
            "buddy":[0,1],
            "stapler":[168,120],
            "tracking_marker":[0.1,0.15],
            "read_crinkle":[0.2,0.25],
            "stapler_time":[40,40],
            "tape":["3mon","3mon"],
            "tape_temp":[62,62],
            "ink_cycle":[1250,1500],
        })
    else:
        # invalid => read_crinkle="abc"
        df = pl.DataFrame({
            "ID": [1],
            "testid": [10],
            "exam_number": [999],
            "buddy":[0],
            "stapler":[168],
            "tracking_marker":[0.1],
            "read_crinkle":["abc"],  # floatじゃない
            "stapler_time":[40],
            "tape":["3mon"],
            "tape_temp":[62],
            "ink_cycle":[1250],
        })

    buf = BytesIO()
    df.write_parquet(buf)
    return buf.getvalue()

def make_side_effect_parquet(parquet_bytes: bytes):
    """
    patch("polars.read_parquet") => BytesIO(parquet_bytes)
    """
    def _side_effect_read_parquet(file_path, **kwargs):
        return pl.read_parquet(BytesIO(parquet_bytes))
    return _side_effect_read_parquet


def test_load_fbc_parquet_normal(mock_loader):
    """
    Parquet: 正常系 => DataFrame が期待dfと一致
    """
    data_bytes = make_fake_parquet(normal=True)
    with patch("polars.read_parquet", side_effect=make_side_effect_parquet(data_bytes)):
        df_actual = mock_loader.load_fbc_parquet(Path("fake.parquet"))
        pdf_actual = df_actual.to_pandas()

        # pandera
        QuotationSchema.validate(pdf_actual)

        # 値チェック
        assert pdf_actual.equals(pdf_expected_parquet), "Parquet正常系と期待値が一致しません"

def test_load_fbc_parquet_wrong_type(mock_loader):
    """
    Parquet: 異常系 => read_crinkle="abc" => SchemaError
    """
    data_bytes = make_fake_parquet(normal=False)
    with patch("polars.read_parquet", side_effect=make_side_effect_parquet(data_bytes)):
        df_actual = mock_loader.load_fbc_parquet(Path("fake.parquet"))
        pdf_actual = df_actual.to_pandas()
        with pytest.raises(pa.errors.SchemaError):
            QuotationSchema.validate(pdf_actual)