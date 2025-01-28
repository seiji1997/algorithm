import logging
import polars as pl

def check_page_values(df: pl.DataFrame):
    """
    1) まず df["page"] のユニークな値を取得
    2) その集合が {0,1,2} の部分集合かどうかを判定
    3) もし一部しか含まないなら => ログ出力して続行
    4) もし {0,1,2} 以外の値が混ざっていれば => エラーと該当値を表示し、処理中断
    """
    valid_pages = {0,1,2}
    # Polarsでユニーク値を取得 => python set
    actual_pages = set(df["page"].unique().to_list())

    # 1) issubset かどうか
    if actual_pages.issubset(valid_pages):
        # 2) もし完全一致
        if actual_pages == valid_pages:
            logging.info("page のユニーク値が 0,1,2 のみ => 正常")
        else:
            missing = valid_pages - actual_pages
            logging.warning(f"page に欠けがある => {missing} が含まれていませんが続行します")
        # 処理は続行
    else:
        # 3) 不正な値 (0,1,2 以外) が含まれている => エラー
        invalid_values = actual_pages - valid_pages
        raise ValueError(f"page に想定外の値 {invalid_values} が含まれているため処理中断します")