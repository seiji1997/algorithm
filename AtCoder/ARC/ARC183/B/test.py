
import pytest
import polars as pl
from pathlib import Path
from io import StringIO, BytesIO
import yaml
from loader import Config, Loader, _check_exists


# ========================================================
# 1) _check_exists のテスト (mock を pytest-mock で実行)
# ========================================================
def test_check_exists_ok(mocker):
    """パスが存在 => FileNotFoundError 出ない"""
    fake_path = Path("some/path")
    mocker.patch.object(Path, "exists", return_value=True)
    _check_exists(fake_path, desc="test-desc")  # エラー起きず OK


def test_check_exists_notfound(mocker):
    """パスが存在しない => FileNotFoundError"""
    fake_path = Path("some/notfound")
    mocker.patch.object(Path, "exists", return_value=False)
    with pytest.raises(FileNotFoundError) as exc:
        _check_exists(fake_path, desc="xyz")
    assert "xyz not found" in str(exc.value)


# ========================================================
# 2) Configクラスのテスト
# ========================================================
FAKE_YAML_DATA_NORMAL = {
    "input_path": {
        "quotation_path": "fake_quotation.csv",
        "condition_table": "fake_condition.csv",
        "lut_table_path": "fake_lut.csv",
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
    "input_path": {
        "quotation_path":  "fake_quotation.csv",
        "condition_table": "fake_condition.csv"
    },
    "readmode": {
        "ber1": "bigmac",
        "ber2": "drink"
    },
    "output_path": "fake_output"
}

FAKE_YAML_DATA_WRONG_TYPE = {
    "input_path": {
        "quotation_path":  "fake_quotation.csv",
        "condition_table": "fake_condition.csv",
        "ruler_data_path": "fake_ruler_data"
    },
    "frame_size": {
        "pen": "invalid-str",  # int のはず
        "book": 20000
    },
    "readmode": {
        "ber1": "bigmac",
        "ber2": "drink"
    },
    "output_path": "fake_output"
}


def test_config_normal(mocker):
    """
    Config: 正常系 => dataclass __eq__ で期待値と比較
    """
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data="dummy"))
    mocker.patch("yaml.safe_load", return_value=FAKE_YAML_DATA_NORMAL)

    c = Config.from_yaml("dummy_config.yaml")

    expected = Config(
        quotation_path="fake_quotation.csv",
        condition_table="fake_condition.csv",
        lut_table_path="fake_lut.csv",
        ruler_data_path="fake_ruler_data",
        pen=10000,
        book=20000,
        readmode={"ber1": "bigmac", "ber2": "drink"},
        output_path="fake_output"
    )
    # dataclass => __eq__ 比較
    assert c == expected


def test_config_missing_key(mocker):
    """キー欠落 => KeyError"""
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data="dummy"))
    mocker.patch("yaml.safe_load", return_value=FAKE_YAML_DATA_MISSING_KEY)

    with pytest.raises(KeyError):
        Config.from_yaml("dummy_config.yaml")


def test_config_wrong_type(mocker):
    """型不正 => TypeError"""
    mocker.patch.object(Path, "exists", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data="dummy"))
    mocker.patch("yaml.safe_load", return_value=FAKE_YAML_DATA_WRONG_TYPE)

    with pytest.raises(TypeError):
        Config.from_yaml("dummy_config.yaml")


# ========================================================
# 3) Loader CSV テスト: Polars のみ
# ========================================================
@pytest.fixture
def mock_loader():
    """Loader(config=None) を返す"""
    return Loader(config=None)

FAKE_QUOTATION_CSV_NORMAL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle
1,10,999,0,168,0.1,0.2,40,"3mon",62,1250
2,11,888,1,120,0.15,0.25,40,"3mon",62,1500
"""

FAKE_CONDITION_CSV_NORMAL = """\
scotch_temp,scotch_time,tape,stapler_temp
40,"3mon",85,71.25
40,"3mon",85,71.25
"""

# 正常な期待DF (Polars)
df_expected_quotation_csv = pl.DataFrame({
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

def side_effect_read_csv_normal(file_path: Path, **kwargs):
    """ポラース read_csv モック(正常)"""
    import polars as pl
    if "quotation" in str(file_path).lower():
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_NORMAL))
    elif "condition" in str(file_path).lower():
        return pl.read_csv(StringIO(FAKE_CONDITION_CSV_NORMAL))
    else:
        return pl.DataFrame()

def test_load_quotation_csv_normal(mocker, mock_loader):
    """
    CSV 正常系 => df が df_expected_quotation_csv と frame_equal
    """
    mocker.patch("polars.read_csv", side_effect=side_effect_read_csv_normal)
    df_actual = mock_loader.load_quotation_csv()
    # dtypes / columns / data が完全一致なら True
    assert df_actual.frame_equal(df_expected_quotation_csv, null_equal=True)

def test_load_quotation_csv_missingcol(mocker, mock_loader):
    """
    CSV 異常: 列欠落 => frame_equal => False
    """
    FAKE_QUOTATION_CSV_MISSING_COL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,ink_cycle
1,10,999,0,168,0.1,0.2,40,"3mon",1250
2,11,888,1,120,0.15,0.25,40,"3mon",1500
"""
    def side_effect_missing(file_path: Path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_MISSING_COL))

    mocker.patch("polars.read_csv", side_effect=side_effect_missing)
    df_actual = mock_loader.load_quotation_csv()

    # 列が足りない => frame_equal(...) => False
    assert not df_actual.frame_equal(df_expected_quotation_csv, null_equal=True)

def test_load_quotation_csv_wrongtype(mocker, mock_loader):
    """
    CSV 異常: 型不正 => frame_equal => False
    """
    FAKE_QUOTATION_CSV_WRONG_TYPE = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle
1,10,999,0,168,0.1,"abc",40,"3mon",62,1250
"""
    def side_effect_wrongtype(file_path: Path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_WRONG_TYPE))

    mocker.patch("polars.read_csv", side_effect=side_effect_wrongtype)
    df_actual = mock_loader.load_quotation_csv()
    # "abc" => 文字列 => dtypesが変わる => frame_equal => False
    assert not df_actual.frame_equal(df_expected_quotation_csv, null_equal=True)

def test_load_quotation_csv_extracol(mocker, mock_loader):
    """
    CSV 異常: 余分カラム => frame_equal => False
    """
    FAKE_QUOTATION_CSV_EXTRA_COL = """\
ID,testid,exam_number,buddy,stapler,tracking_marker,read_crinkle,stapler_time,tape,tape_temp,ink_cycle,dummy_col
1,10,999,0,168,0.1,0.2,40,"3mon",62,1250,"extra"
2,11,888,1,120,0.15,0.25,40,"3mon",62,1500,"extra"
"""
    def side_effect_extracol(file_path: Path, **kwargs):
        return pl.read_csv(StringIO(FAKE_QUOTATION_CSV_EXTRA_COL))

    mocker.patch("polars.read_csv", side_effect=side_effect_extracol)
    df_actual = mock_loader.load_quotation_csv()
    # 余分カラム => frame_equal => False
    assert not df_actual.frame_equal(df_expected_quotation_csv, null_equal=True)


# ========================================================
# 4) Loader Parquet テスト (Polars only)
# ========================================================
df_expected_quotation_parquet = pl.DataFrame({
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

def make_fake_parquet(is_normal: bool) -> bytes:
    """Polars DF => write_parquet => BytesIO (型不正なら 'abc')"""
    if is_normal:
        df = df_expected_quotation_parquet  # 正常
    else:
        # read_crinkle を文字列に変えて型不正を起こす
        df = df_expected_quotation_parquet.with_columns(
            pl.lit("abc").alias("read_crinkle")  # floatじゃなくなる
        )
    buf = BytesIO()
    df.write_parquet(buf)
    return buf.getvalue()

def test_load_parquet_normal(mocker, mock_loader):
    """Parquet 正常 => frame_equal => True"""
    def side_effect_parquet_ok(file_path, **kwargs):
        return pl.read_parquet(BytesIO(make_fake_parquet(True)))

    mocker.patch("polars.read_parquet", side_effect=side_effect_parquet_ok)
    df_actual = mock_loader.load_fbc_parquet(Path("fake.parquet"))
    assert df_actual.frame_equal(df_expected_quotation_parquet, null_equal=True)

def test_load_parquet_wrongtype(mocker, mock_loader):
    """Parquet 型不正 => frame_equal => False"""
    def side_effect_parquet_ng(file_path, **kwargs):
        return pl.read_parquet(BytesIO(make_fake_parquet(False)))

    mocker.patch("polars.read_parquet", side_effect=side_effect_parquet_ng)
    df_actual = mock_loader.load_fbc_parquet(Path("fake.parquet"))
    assert not df_actual.frame_equal(df_expected_quotation_parquet, null_equal=True)