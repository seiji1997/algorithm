#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
calculator.py

IDごとに (sheet, stripe) 別の糊(glue)を計算し、それを (sheet) 単位に集約。
最終的に、すべてのIDの集約結果をまとめて Quotation CSV に 1度だけアペンドする。

ステップ:
 1) decide_mode_by_sheet: pen/book 判定
 2) prepare_lut_df: LUT突き合わせ => filenames( glue1, glue2 )
 3) compute_glue_for_id: Parquet→(sheet, stripe)→glue
 4) aggregate_glue_by_sheet: (sheet,stripe)->(sheet)
 5) main_process:
    - pen/book 判定
    - LUT pivot => IDごとに "compute_glue_for_id"+"aggregate" 実行
    - 全ID分の結果をまとめ concat => pivot(必要なら)
    - Quotation に1度だけ join => updated_quotation.csv
"""

import polars as pl
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List

from loader import Loader, Config

class Calculator:
    """
    改修版: ID単位で計算するが Quotation への出力は最後に1度だけ。
    """

    def __init__(self, config: Config, loader: Loader):
        self.config = config
        self.loader = loader

    # (1) pen/book 判定
    def decide_mode_by_sheet(self) -> Tuple[str, int]:
        """
        ruler_data_path を見て、sheetユニーク数=3 => pen /4 => book
        """
        data_dir = Path(self.config.ruler_data_path)
        files = list(data_dir.glob("*.parquet"))
        if not files:
            raise FileNotFoundError(f"No .parquet found in {data_dir}")

        df_sample = self.loader.load_ruler_parquet(files[0])
        unique_sheets = df_sample["sheet"].unique().to_list()
        if len(unique_sheets)==3:
            return ("pen", self.config.pen)
        elif len(unique_sheets)==4:
            return ("book", self.config.book)
        else:
            raise ValueError("sheet unique != 3 or 4")

    # (2) LUT突き合わせ => pivot => filename_glue1, glue2
    def prepare_lut_df(self, mode: str) -> pl.DataFrame:
        """
        Quotation+Condition => cross join => filter => pivot => "filename_glue1","filename_glue2"
        戻り値: df (ID, ink_cycle, tracking_marker, read_crinkle, filename_glue1, filename_glue2)
        """
        df_q = self.loader.load_quotation_csv()
        df_c = self.loader.load_condition_csv()

        # merge
        df_m = df_q.join(
            df_c, on=["condition_temp","condition_time"], how="left"
        ).rename({
            "scotch_temp":"tape",
            "scotch_time":"stapler_temp"
        })

        # rename Quotation's tape => "quo_tape"
        df_m = df_m.rename({"tape":"quo_tape"})

        df_lut = self.loader.load_lut_csv()
        df_lut = df_lut.rename({"tape":"lut_tape"})

        df_cross = df_m.join(df_lut, how="cross")
        df_match = df_cross.filter(
            (pl.col("ink_cycle")>= pl.col("inkcycle_start")) &
            (pl.col("ink_cycle")<= pl.col("inkcycle_end")) &
            (
                (pl.col("lut_tape")==0.0) |
                (pl.col("lut_tape")==pl.col("quo_tape"))
            ) &
            pl.col("readmode").is_in(list(self.config.readmode.values()))
        )

        # pivot => readmode => filename_glue1, glue2
        df_pivot = df_match.pivot(
            index=["ID","ink_cycle","tracking_marker","read_crinkle"],
            columns="readmode",
            values="filename",
            aggregate_function="first"
        )

        rename_map= {}
        for k,v in self.config.readmode.items():
            rename_map[v]= f"filename_{k}"
        df_pivot= df_pivot.rename(rename_map)
        return df_pivot

    # (3) Parquet => glue
    def compute_glue_from_parquet(
        self,
        parquet_path: Path,
        ink_cycle_val: float,
        track_val: float,
        crinkle_val: float,
        frame_size: int
    )-> pl.DataFrame:
        """
        Parquet => (sheet,stripe,ink,ruler) => 2点補間 => glue
        """
        df_raw= self.loader.load_ruler_parquet(parquet_path)
        df_lower= (
            df_raw.filter(pl.col("ink")<= ink_cycle_val)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").max().alias("ink_lower"),
                pl.col("ruler").take(pl.col("ink").arg_max()).alias("ruler_lower")
            ])
        )
        df_upper= (
            df_raw.filter(pl.col("ink")>= ink_cycle_val)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").min().alias("ink_upper"),
                pl.col("ruler").take(pl.col("ink").arg_min()).alias("ruler_upper")
            ])
        )
        df_join= df_lower.join(df_upper, on=["sheet","stripe"], how="inner")

        def interp(row: dict):
            i_l= row["ink_lower"]
            r_l= row["ruler_lower"]
            i_u= row["ink_upper"]
            r_u= row["ruler_upper"]
            if i_l> i_u: return None
            if abs(i_u - i_l)<1e-12:
                val= r_l
            else:
                ratio= (ink_cycle_val - i_l)/(i_u - i_l)
                val= r_l + (r_u - r_l)* ratio
            return (val* track_val* crinkle_val)/ frame_size

        df_join= df_join.with_columns(
            pl.struct(["ink_lower","ruler_lower","ink_upper","ruler_upper"]).apply(interp).alias("glue")
        )
        df_join= df_join.filter(pl.col("glue").is_not_null())
        return df_join.select(["sheet","stripe","glue"])

    # (4) calc_glue_for_id => glue1, glue2 => outer join => (sheet, stripe)
    def calc_glue_for_id(
        self,
        idx: int,
        filenames: Dict[str, str],
        ink_cycle_val: float,
        track_val: float,
        crinkle_val: float,
        frame_size: int
    )-> pl.DataFrame:
        """
        1) filename_glue1 => rename(glue-> glue_glue1)
        2) filename_glue2 => rename(glue-> glue_glue2)
        => outer join => (sheet,stripe, glue_glue1,glue_glue2)
        => ID列付加 => return
        """
        data_dir= Path(self.config.ruler_data_path)
        df_list= []
        for k in self.config.readmode.keys():  # e.g. glue1, glue2
            fname= filenames.get(k, None)
            if fname:
                df_one= self.compute_glue_from_parquet(
                    parquet_path= (data_dir/fname),
                    ink_cycle_val= ink_cycle_val,
                    track_val= track_val,
                    crinkle_val= crinkle_val,
                    frame_size= frame_size
                ).rename({"glue": f"glue_{k}"})
                df_list.append(df_one)
            else:
                # 空
                schema= [("sheet",pl.Int64),("stripe",pl.Int64),(f"glue_{k}",pl.Float64)]
                df_list.append(pl.DataFrame(schema=schema))

        if not df_list:
            return pl.DataFrame()

        df_merged= df_list[0]
        for dfx in df_list[1:]:
            df_merged= df_merged.join(dfx, on=["sheet","stripe"], how="outer")

        df_merged= df_merged.with_columns(pl.lit(idx).alias("ID"))

        final_cols= ["ID","sheet","stripe"]
        for k in self.config.readmode.keys():
            final_cols.append(f"glue_{k}")
        return df_merged.select(final_cols).sort(["ID","sheet","stripe"])

    # (5) aggregate_glue_by_sheet => (sheet) 集約
    def aggregate_glue_by_sheet(self, df_glue_stripe: pl.DataFrame)-> pl.DataFrame:
        """
        (ID,sheet,stripe,glue_glue1,glue_glue2) => groupby(sheet) => mean
        => (ID,sheet, glue_glue1_sheet, glue_glue2_sheet)
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

    # calc_ink_ratio_for_sheet_stripe => optional (使うなら)
    def calc_ink_ratio_for_sheet_stripe(self, df_glue_stripe: pl.DataFrame)-> pl.DataFrame:
        """
        ratio= glue_glueX / sum per sheet
        """
        df_sum= (
            df_glue_stripe
            .groupby(["ID","sheet"], maintain_order=True)
            .agg([
                pl.col("glue_glue1").sum().alias("sum_glue1"),
                pl.col("glue_glue2").sum().alias("sum_glue2")
            ])
        )
        df_join= df_glue_stripe.join(df_sum, on=["ID","sheet"], how="left").with_columns([
            (pl.col("glue_glue1")/ pl.col("sum_glue1")).fill_null(0.0).alias("ratio_glue1"),
            (pl.col("glue_glue2")/ pl.col("sum_glue2")).fill_null(0.0).alias("ratio_glue2")
        ])
        return df_join

    def main_process(self)-> None:
        """
        全ID分を計算→最後に1度だけ Quotation と join => updated_quotation.csv
        フロー:
          1) pen/book 判定 => frame_size
          2) LUT => pivot => filename_glueX
          3) IDループ => calc_glue_for_id -> aggregate_glue_by_sheet -> store
          4) after loop => concat => pivot => join Quotation => 1回だけCSV
        """
        mode, frame_size= self.decide_mode_by_sheet()
        print(f"[INFO] mode={mode}, frame_size={frame_size}")

        df_lut= self.prepare_lut_df(mode)
        # => (ID,ink_cycle,tracking_marker,read_crinkle, filename_glue1, filename_glue2,...)

        out_dir= Path(self.config.output_path)
        out_dir.mkdir(parents=True, exist_ok=True)

        # IDごとの集約結果を貯める
        aggregated_list= []

        # IDループ
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

            # (sheet, stripe) => glue
            df_glue= self.calc_glue_for_id(
                idx= idx,
                filenames= filenames,
                ink_cycle_val= icycle,
                track_val= track,
                crinkle_val= crinkle,
                frame_size= frame_size
            )
            if df_glue.is_empty():
                continue

            # (sheet)集約
            df_sheet= self.aggregate_glue_by_sheet(df_glue)
            # => (ID, sheet, glue_glue1_sheet, glue_glue2_sheet)
            aggregated_list.append(df_sheet)

        # すべての ID の集約結果を concat
        if not aggregated_list:
            print("[INFO] No data => skip updated_quotation.csv")
            return

        df_all= pl.concat(aggregated_list, how="vertical")

        # もし "sheet" を pivot して "glue_glue1_sheet0" などの形式にしたいなら:
        df_melt= df_all.melt(
            id_vars=["ID","sheet"],
            value_vars=["glue_glue1_sheet","glue_glue2_sheet"]
        )
        df_pivot= df_melt.pivot(
            index=["ID"],
            columns=["variable","sheet"],
            values="value",
            aggregate_function="first"
        )
        # rename => glue_glue1_sheet0, etc.
        new_cols= []
        for (var,sh) in df_pivot.columns:
            new_cols.append(f"{var}_sheet{sh}")
        df_pivot.columns= new_cols

        # Quotation と 1回だけ join => updated_quotation.csv
        df_q= self.loader.load_quotation_csv()
        df_joined= df_q.join(df_pivot, on="ID", how="left").sort("ID")

        out_csv= out_dir/ "updated_quotation.csv"
        df_joined.write_csv(out_csv)
        print(f"[INFO] output => {out_csv}")