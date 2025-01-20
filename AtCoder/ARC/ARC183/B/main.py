# (Press Ctrl+D to revert)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
calculator.py

各種処理を小さな関数に分割し、責任範囲を明確化したリファクタリング版:
 1) decide_mode_by_sheet:        pen or book 判定
 2) merge_condition_info:        Quotation+Condition の結合
 3) prepare_lut_df:             ruler_pencilcase 突き合わせ => pivot => filename_glue1, glue2
 4) calc_glue_for_id:           Parquet読み込み => (sheet, stripe) で糊(glue)計算 => df_glue_stripe
 5) aggregate_glue_by_sheet:    (sheet, stripe)->(sheet) 集約
 6) calc_ink_ratio_for_sheet_stripe: (sheet, stripe) の glue / (sheet) 合計 => ratio
 7) append_glue_to_quotation:   Quotation CSV に glue(集約) を join => CSV出力
 8) process_id_flow:            IDごとに 4~7 を実行する例
 9) main_process:               全体の流れ (pen/book 判定, LUT突き合わせ, IDループなど)
"""

import polars as pl
import numpy as np
from pathlib import Path
from typing import Tuple, Dict

from loader import Loader, Config  # config.yaml, CSV/Parquetロードを担当

class Calculator:
    """
    リファクタリング後の計算クラス:
      - 処理単位を細かく分割し、テストや可読性を向上。
      - カラム名が多少変わっても loader/definitions 側の rename を調整するだけで済む設計。
      - ここでは "sheet","stripe","ink","ruler" が主に必要となるカラムと想定。
    """

    def __init__(self, config: Config, loader: Loader):
        """
        Args:
          config: config.yaml の設定オブジェクト
          loader: CSV/Parquetの読み込みクラス
        """
        self.config = config
        self.loader = loader

    # ----------------------------------------------------------------
    # (1) decide_mode_by_sheet: pen or book 判定
    # ----------------------------------------------------------------
    def decide_mode_by_sheet(self) -> Tuple[str, int]:
        """
        ruler_data_path 内の最初の Parquet をチェックし、
         - sheet ユニーク数が3 → pen (frame_size= self.config.pen)
         - sheet ユニーク数が4 → book (frame_size= self.config.book)
        戻り値: (mode, frame_size)  例: ("pen",36672)
        """
        data_dir = Path(self.config.ruler_data_path)
        files = list(data_dir.glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"No .parquet found in {data_dir}")

        # 最初の1つだけで判定
        df_sample = self.loader.load_ruler_parquet(files[0])
        unique_sheets = df_sample["sheet"].unique().to_list()

        if len(unique_sheets) == 3:
            return ("pen", self.config.pen)
        elif len(unique_sheets) == 4:
            return ("book", self.config.book)
        else:
            raise ValueError(f"Invalid sheet unique count={len(unique_sheets)} (not 3 or 4)")

    # ----------------------------------------------------------------
    # (2) merge_condition_info: Quotation+Condition を結合
    # ----------------------------------------------------------------
    def merge_condition_info(self, df_q: pl.DataFrame, df_c: pl.DataFrame) -> pl.DataFrame:
        """
        Quotation CSV + Condition CSV の JOIN:
         - on=["condition_temp","condition_time"]
         - scotch_temp => rename("tape")
         - scotch_time => rename("stapler_temp")
        戻り値: df_merged
        """
        from definitions import UNUSED_COLUMNS_AFTER_MERGE
        merged = df_q.join(
            df_c,
            how="left",
            on=["condition_temp","condition_time"]
        ).rename({
            "scotch_temp": "tape",
            "scotch_time": "stapler_temp"
        })
        drop_cols = [c for c in UNUSED_COLUMNS_AFTER_MERGE if c in merged.columns]
        if drop_cols:
            merged = merged.drop(drop_cols)
        return merged

    # ----------------------------------------------------------------
    # (3) prepare_lut_df: ruler_pencilcase 突き合わせ => filename_glue1, glue2
    # ----------------------------------------------------------------
    def prepare_lut_df(self, mode: str) -> pl.DataFrame:
        """
        1) Quotation+Condition => df_m
        2) ruler_pencilcase 読み込み => rename(tape->lut_tape)
        3) cross join => filter => pivot => readmode="bigmac"->filename_glue1, "drink"->filename_glue2
        """
        df_q = self.loader.load_quotation_csv()
        df_c = self.loader.load_condition_csv()
        df_m = self.merge_condition_info(df_q, df_c)

        # Quotation 側 tape => "quo_tape"
        df_m = df_m.rename({"tape": "quo_tape"})

        df_lut = self.loader.load_lut_csv()
        df_lut = df_lut.rename({"tape": "lut_tape"})

        df_cross = df_m.join(df_lut, how="cross")
        df_match = df_cross.filter(
            (pl.col("ink_cycle") >= pl.col("inkcycle_start")) &
            (pl.col("ink_cycle") <= pl.col("inkcycle_end")) &
            (
                (pl.col("lut_tape") == 0.0) |
                (pl.col("lut_tape") == pl.col("quo_tape"))
            ) &
            pl.col("readmode").is_in(list(self.config.readmode.values()))
        )

        # pivot => readmode="bigmac" => filename_glue1, "drink" => filename_glue2
        df_pivot = df_match.pivot(
            index=["ID","ink_cycle","tracking_marker","read_crinkle"],
            columns="readmode",
            values="filename",
            aggregate_function="first"
        )

        rename_map = {}
        for k, v in self.config.readmode.items():
            # k="glue1", v="bigmac" => rename => "bigmac" -> "filename_glue1"
            rename_map[v] = f"filename_{k}"
        df_pivot = df_pivot.rename(rename_map)
        return df_pivot

    # ----------------------------------------------------------------
    # compute_glue_from_parquet: (sheet, stripe) 線形補間 => glue
    # ----------------------------------------------------------------
    def compute_glue_from_parquet(
        self,
        parquet_path: Path,
        ink_cycle_val: float,
        track_val: float,
        crinkle_val: float,
        frame_size: int
    ) -> pl.DataFrame:
        """
        1) Parquet => (sheet, stripe, ink, ruler)
        2) "ink <= target_ink" の最大 と "ink >= target_ink" の最小 の2点を取得
        3) 線形補間 => ruler_val
        4) glue = ruler_val * track_val * crinkle_val / frame_size
        5) 戻り => (sheet, stripe, glue)
        """
        df_raw = self.loader.load_ruler_parquet(parquet_path)

        # 下側
        df_lower = (
            df_raw.filter(pl.col("ink") <= ink_cycle_val)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").max().alias("ink_lower"),
                pl.col("ruler").take(pl.col("ink").arg_max()).alias("ruler_lower")
            ])
        )
        # 上側
        df_upper = (
            df_raw.filter(pl.col("ink") >= ink_cycle_val)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").min().alias("ink_upper"),
                pl.col("ruler").take(pl.col("ink").arg_min()).alias("ruler_upper")
            ])
        )
        df_joined = df_lower.join(df_upper, on=["sheet","stripe"], how="inner")

        def interpolate_glue(row: dict):
            i_l= row["ink_lower"]
            r_l= row["ruler_lower"]
            i_u= row["ink_upper"]
            r_u= row["ruler_upper"]
            if i_l> i_u:
                return None
            if abs(i_u - i_l)<1e-12:
                ruler_val= r_l
            else:
                ratio= (ink_cycle_val - i_l)/(i_u - i_l)
                ruler_val= r_l + (r_u - r_l)* ratio
            return (ruler_val * track_val * crinkle_val)/ frame_size

        df_joined = df_joined.with_columns(
            pl.struct(["ink_lower","ruler_lower","ink_upper","ruler_upper"]).apply(
                interpolate_glue
            ).alias("glue")
        )
        df_joined = df_joined.filter(pl.col("glue").is_not_null())

        return df_joined.select(["sheet","stripe","glue"])

    # ----------------------------------------------------------------
    # (4) calc_glue_for_id: glue1, glue2 => outer join => (sheet, stripe)
    # ----------------------------------------------------------------
    def calc_glue_for_id(
        self,
        idx: int,
        filenames: Dict[str,str],
        ink_cycle_val: float,
        track_val: float,
        crinkle_val: float,
        frame_size: int
    ) -> pl.DataFrame:
        """
        1) filename_glue1 => compute => rename(glue->"glue_glue1")
        2) filename_glue2 => compute => rename(glue->"glue_glue2")
        3) outer join => (sheet, stripe, glue_glue1, glue_glue2)
        4) ID 列付加
        戻り => df_glue_stripe: (ID, sheet, stripe, glue_glue1, glue_glue2)
        """
        data_dir= Path(self.config.ruler_data_path)
        df_list= []
        for k in self.config.readmode.keys():
            fname= filenames.get(k, None)
            if fname:
                df_one= self.compute_glue_from_parquet(
                    parquet_path=(data_dir/fname),
                    ink_cycle_val= ink_cycle_val,
                    track_val= track_val,
                    crinkle_val= crinkle_val,
                    frame_size= frame_size
                ).rename({"glue": f"glue_{k}"})
                df_list.append(df_one)
            else:
                schema= [("sheet", pl.Int64), ("stripe", pl.Int64), (f"glue_{k}", pl.Float64)]
                df_list.append(pl.DataFrame(schema=schema))

        if not df_list:
            return pl.DataFrame()

        df_merged= df_list[0]
        for dfx in df_list[1:]:
            df_merged= df_merged.join(dfx, on=["sheet","stripe"], how="outer")

        df_merged= df_merged.with_columns(pl.lit(idx).alias("ID"))

        # カラム並び
        final_cols= ["ID","sheet","stripe"]
        for k in self.config.readmode.keys():
            final_cols.append(f"glue_{k}")
        df_merged= df_merged.select(final_cols).sort(["ID","sheet","stripe"])
        return df_merged

    # ----------------------------------------------------------------
    # (5) aggregate_glue_by_sheet: (sheet, stripe)->(sheet) 集約
    # ----------------------------------------------------------------
    def aggregate_glue_by_sheet(
        self,
        df_glue_stripe: pl.DataFrame
    ) -> pl.DataFrame:
        """
        (ID, sheet, stripe, glue_glue1, glue_glue2) => groupby(sheet) => e.g. mean
        戻り => (ID, sheet, glue_glue1_sheet, glue_glue2_sheet)
        """
        df_agg= (
            df_glue_stripe
            .groupby(["ID","sheet"])
            .agg([
                pl.col("glue_glue1").mean().alias("glue_glue1_sheet"),
                pl.col("glue_glue2").mean().alias("glue_glue2_sheet")
            ])
            .sort(["ID","sheet"])
        )
        return df_agg

    # ----------------------------------------------------------------
    # (6) calc_ink_ratio_for_sheet_stripe: ratio= glue / sum(sheet)
    # ----------------------------------------------------------------
    def calc_ink_ratio_for_sheet_stripe(
        self,
        df_glue_stripe: pl.DataFrame
    ) -> pl.DataFrame:
        """
        we_ratio_glue1= glue_glue1(sheet,stripe)/ sum(glue_glue1 by (sheet))
        we_ratio_glue2= ...
        戻り => df_join(sheet,stripe, we_ratio_glue1, we_ratio_glue2)
        """
        df_sum= (
            df_glue_stripe
            .groupby(["ID","sheet"], maintain_order=True)
            .agg([
                pl.col("glue_glue1").sum().alias("sum_glue1_sheet"),
                pl.col("glue_glue2").sum().alias("sum_glue2_sheet")
            ])
        )
        df_join= df_glue_stripe.join(df_sum, on=["ID","sheet"], how="left").with_columns([
            (pl.col("glue_glue1") / pl.col("sum_glue1_sheet")).fill_null(0.0).alias("we_ratio_glue1"),
            (pl.col("glue_glue2") / pl.col("sum_glue2_sheet")).fill_null(0.0).alias("we_ratio_glue2"),
        ])
        return df_join

    # ----------------------------------------------------------------
    # (7) append_glue_to_quotation: Quotation CSV に集約glueをjoin => CSV出力
    # ----------------------------------------------------------------
    def append_glue_to_quotation(
        self,
        df_glue_sheet: pl.DataFrame,
        out_csv: Path
    ) -> None:
        """
        Quotation CSV を ID で left join => ID ソート => CSV出力
        """
        df_q= self.loader.load_quotation_csv()
        df_joined= df_q.join(df_glue_sheet, on="ID", how="left").sort("ID")
        df_joined.write_csv(out_csv)
        print(f"[INFO] Quotation appended => {out_csv}, rows={df_joined.height}")

    # ----------------------------------------------------------------
    # (8) process_id_flow: IDごとの全フロー例
    # ----------------------------------------------------------------
    def process_id_flow(
        self,
        id_val: int,
        ink_cycle_val: float,
        track_val: float,
        crinkle_val: float,
        filenames: Dict[str,str],
        frame_size: int,
        out_dir: Path
    ) -> None:
        """
        ID 1件ぶん:
         1) calc_glue_for_id => (sheet, stripe) glue_glue1, glue_glue2 => sheet_stripe_{ID}.csv
         2) aggregate_glue_by_sheet => (sheet) => sheet_{ID}.csv
         3) Quotationにアペンド => updated_quotation_{ID}.csv
         4) ratio => (sheet, stripe) => ratio => ratio_{ID}.csv
        """
        df_glue_stripe= self.calc_glue_for_id(
            idx= id_val,
            filenames= filenames,
            ink_cycle_val= ink_cycle_val,
            track_val= track_val,
            crinkle_val= crinkle_val,
            frame_size= frame_size
        )
        if df_glue_stripe.is_empty():
            print(f"[WARN] ID={id_val} => no data, skip")
            return

        out_csv_wl= out_dir/ f"sheet_stripe_{id_val}.csv"
        df_glue_stripe.write_csv(out_csv_wl)
        print(f"[INFO] sheet_stripe => {out_csv_wl}")

        df_sheet= self.aggregate_glue_by_sheet(df_glue_stripe)
        out_csv_page= out_dir/ f"sheet_{id_val}.csv"
        df_sheet.write_csv(out_csv_page)
        print(f"[INFO] sheet => {out_csv_page}")

        out_csv_quote= out_dir/ f"updated_quotation_{id_val}.csv"
        self.append_glue_to_quotation(df_sheet, out_csv_quote)

        df_ratio= self.calc_ink_ratio_for_sheet_stripe(df_glue_stripe)
        out_csv_ratio= out_dir/ f"wl_ratio_{id_val}.csv"
        df_ratio.write_csv(out_csv_ratio)
        print(f"[INFO] ratio => {out_csv_ratio}")

        print(f"[INFO] ID={id_val} => flow done.\n")

    # ----------------------------------------------------------------
    # (9) main_process: 全体フロー (pen/book 判定, LUT, IDごと計算)
    # ----------------------------------------------------------------
    def main_process(self) -> None:
        """
        大枠の流れ:
         1) decide_mode_by_sheet => (mode, frame_size)
         2) prepare_lut_df => pivot => filename_glue1, glue2
         3) ここではIDごとループ => process_id_flow
        """
        mode, frame_size= self.decide_mode_by_sheet()
        print(f"[INFO] mode={mode}, frame_size={frame_size}")

        df_lut= self.prepare_lut_df(mode)
        out_dir= Path(self.config.output_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        df_lut.write_csv(out_dir/ "lut_pivot.csv")

        # 例: IDごとに loop
        for row in df_lut.iter_rows(named=True):
            idx= row["ID"]
            icycle= row.get("ink_cycle", None)
            track= row.get("tracking_marker", None)
            crinkle= row.get("read_crinkle", None)

            filenames= {}
            for k in self.config.readmode.keys():
                filenames[k] = row.get(f"filename_{k}", None)

            if icycle is None or track is None or crinkle is None:
                print(f"[WARN] ID={idx} => missing param, skip")
                continue

            self.process_id_flow(
                id_val= idx,
                ink_cycle_val= icycle,
                track_val= track,
                crinkle_val= crinkle,
                filenames= filenames,
                frame_size= frame_size,
                out_dir= out_dir
            )

        print("[INFO] main_process done.")