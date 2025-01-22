#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
手順:
 1) load_df_from_parquet     : Parquet ロード => (sheet, stripe, ink, ruler) ...
 2) select_ink_records       : ink の範囲 [ink_min..ink_max] 抽出
 3) compute_average_ruler    : (sheet, stripe) 別に ruler 平均 (debug用)
 4) interpolate_ink_cycle    : 二点補間 => interp_ruler
 5) compute_margin           : tracked_ruler, noised_ruler
 6) compute_glue             : glue= noised_ruler / frame_size
 7) aggregate_glue_by_sheet  : sheet別に glue を集約
 8) append_for_quotation     : 途中結果を (ID,sheet,glue_sheet) にまとめて保存
 9) compute_stripe_ratio     : stripe比率= glue/sum(glue) => CSV
"""

import polars as pl
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

###############################
# 二点補間のヘルパー
###############################
def two_point_interpolation(
    ink_l: float, ruler_l: float,
    ink_u: float, ruler_u: float,
    target_ink: float
)-> float:
    """
    下側 (ink_l, ruler_l) & 上側 (ink_u, ruler_u) で二点補間:
      if target_ink== ink_l => ruler_l
      if target_ink== ink_u => ruler_u
      else => ratio= (target_ink- ink_l)/(ink_u- ink_l)
    例外:
      ink_l > ink_u => RuntimeError
      ink_l == ink_u => RuntimeError
    """
    if ink_l> ink_u:
        logging.error(f"two_point_interpolation: ink_l({ink_l})> ink_u({ink_u}) => invalid")
        raise RuntimeError("two_point_interpolation: ink_l>ink_u")

    if target_ink == ink_l:
        return ruler_l
    if target_ink == ink_u:
        return ruler_u
    if ink_l == ink_u:
        logging.error(f"two_point_interpolation: ink_l==ink_u=={ink_l}")
        raise RuntimeError("two_point_interpolation: no range")

    ratio= (target_ink- ink_l)/(ink_u- ink_l)
    if ratio<0 or ratio>1:
        logging.error(f"two_point_interpolation: ratio={ratio}, target_ink={target_ink}, range=({ink_l},{ink_u})")
        raise RuntimeError("target_ink not in [ink_l..ink_u]")

    return ruler_l + (ruler_u- ruler_l)* ratio


class FinalCalculatorRenamed:
    """
    ID単位で 1)~9) ステップを実行 -> すべて完了後に final_quotation.csv 出力。
    rename対応: sheet,stripe,ink,ruler,glue, etc.
    """

    def __init__(self):
        # Quotation用最終集約 => (ID, sheet, glue_sheet)
        self.quotation_data_list= []

    ###############################
    # 1) parquetロード => (sheet,stripe,ink,ruler)
    ###############################
    def load_df_from_parquet(self, parquet_path: Path)-> pl.DataFrame:
        df= pl.read_parquet(str(parquet_path))
        return df

    ###############################
    # 2) ink範囲で抽出
    ###############################
    def select_ink_records(self, df: pl.DataFrame, ink_min: float, ink_max: float)-> pl.DataFrame:
        df_sel= df.filter(
            (pl.col("ink")>= ink_min) & (pl.col("ink")<= ink_max)
        )
        return df_sel

    ###############################
    # 3) (sheet,stripe) => ruler平均
    ###############################
    def compute_average_ruler(self, df: pl.DataFrame)-> pl.DataFrame:
        df_avg= df.groupby(["sheet","stripe"]).agg(
            pl.col("ruler").mean().alias("mean_ruler")
        )
        return df_avg

    ###############################
    # 4) 二点補間 => interp_ruler
    ###############################
    def interpolate_ink_cycle(
        self,
        df_sel: pl.DataFrame,
        target_ink: float
    )-> pl.DataFrame:
        """
        下側 => ink<= target_ink の最大 => (ink_lower,ruler_lower)
        上側 => ink>= target_ink の最小 => (ink_upper,ruler_upper)
        => row iteration => interp_ruler
        """
        df_lower= (
            df_sel.filter(pl.col("ink")<= target_ink)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").max().alias("ink_lower"),
                pl.col("ruler").take(pl.col("ink").arg_max()).alias("ruler_lower")
            ])
        )
        df_upper= (
            df_sel.filter(pl.col("ink")>= target_ink)
            .groupby(["sheet","stripe"], maintain_order=True)
            .agg([
                pl.col("ink").min().alias("ink_upper"),
                pl.col("ruler").take(pl.col("ink").arg_min()).alias("ruler_upper")
            ])
        )
        df_join= df_lower.join(df_upper, on=["sheet","stripe"], how="inner")

        rows= df_join.iter_rows(named=True)
        new_data= {
            "sheet":[],
            "stripe":[],
            "interp_ruler":[]
        }
        for r in rows:
            l_ink= r["ink_lower"]
            l_ruler= r["ruler_lower"]
            u_ink= r["ink_upper"]
            u_ruler= r["ruler_upper"]
            try:
                val= two_point_interpolation(l_ink, l_ruler, u_ink, u_ruler, target_ink)
            except RuntimeError as e:
                logging.error(f"[interpolate_ink_cycle] => skip row {e}")
                continue

            new_data["sheet"].append(r["sheet"])
            new_data["stripe"].append(r["stripe"])
            new_data["interp_ruler"].append(val)

        df_out= pl.DataFrame(new_data)
        return df_out

    ###############################
    # 5) margin計算 => tracked_ruler, noised_ruler
    ###############################
    def compute_margin(
        self,
        df: pl.DataFrame,
        tracking_marker: float,
        read_crinkle: float
    )-> pl.DataFrame:
        """
        tracked_ruler= interp_ruler*(1+ tracking_marker)
        noised_ruler= tracked_ruler + read_crinkle
        """
        df2= df.with_columns([
            (pl.col("interp_ruler")*(1+ tracking_marker)).alias("tracked_ruler"),
            (pl.col("interp_ruler")*(1+ tracking_marker)+ read_crinkle).alias("noised_ruler")
        ])
        return df2

    ###############################
    # 6) glue= noised_ruler / frame_size
    ###############################
    def compute_glue(
        self,
        df: pl.DataFrame,
        frame_size: float
    )-> pl.DataFrame:
        df_glue= df.with_columns(
            (pl.col("noised_ruler")/ frame_size).alias("glue")
        )
        return df_glue

    ###############################
    # 7) sheet別に glue集約 => glue_sheet
    ###############################
    def aggregate_glue_by_sheet(
        self,
        df: pl.DataFrame
    )-> pl.DataFrame:
        df_page= (
            df.groupby("sheet")
              .agg(pl.col("glue").mean().alias("glue_sheet"))
        )
        return df_page

    ###############################
    # 8) Quotation用 => (ID, sheet, glue_sheet)
    ###############################
    def append_for_quotation(
        self,
        df_sheet: pl.DataFrame,
        id_val: int
    ):
        df_app= df_sheet.with_columns(pl.lit(id_val).alias("ID"))
        self.quotation_data_list.append(df_app)

    ###############################
    # 9) stripe比率 => CSV
    ###############################
    def compute_stripe_ratio(self, df: pl.DataFrame, out_csv: Path):
        """
        sum(glue)= total => ratio= glue/total
        => out_csv
        """
        total= df["glue"].sum()
        if total<=0:
            ratio_list= [0.0]* len(df)
        else:
            ratio_list= df["glue"]/ total
        df_ratio= df.with_column(pl.Series("stripe_ratio", ratio_list))
        df_ratio.write_csv(out_csv)

    ###############################
    # 全ID後 => final_quotation.csv
    ###############################
    def finalize_quotation_csv(self, out_csv: Path):
        if not self.quotation_data_list:
            logging.warning("No data => skip final Quotation CSV.")
            return
        df_all= pl.concat(self.quotation_data_list, how="vertical")
        df_all.write_csv(out_csv)
        logging.info(f"[finalize_quotation_csv] => {out_csv}")

    ###############################
    # main_process => IDごと => steps(1~9)
    ###############################
    def main_process(self, df_lut: pl.DataFrame):
        """
        df_lut columns:
          "ID","parquet_path","ink_min","ink_max","target_ink",
          "tracking_marker","read_crinkle","frame_size"
        """
        for row in df_lut.iter_rows(named=True):
            id_val= row["ID"]
            pq_path= Path(row["parquet_path"])
            i_min= row["ink_min"]
            i_max= row["ink_max"]
            tgt_ink= row["target_ink"]
            track= row["tracking_marker"]
            crinkle= row["read_crinkle"]
            fsize= row["frame_size"]

            # step1
            df_load= self.load_df_from_parquet(pq_path)
            # step2
            df_sel= self.select_ink_records(df_load, i_min, i_max)
            # step3
            df_avg= self.compute_average_ruler(df_sel)  # debug
            # step4 => interpolation
            df_intp= self.interpolate_ink_cycle(df_sel, tgt_ink)
            # step5 => margin
            df_margin= self.compute_margin(df_intp, track, crinkle)
            # step6 => glue
            df_glue= self.compute_glue(df_margin, fsize)
            # step7 => aggregate
            df_sheet= self.aggregate_glue_by_sheet(df_glue)
            # step8 => append => Quotation
            self.append_for_quotation(df_sheet, id_val)
            # step9 => stripe ratio => CSV
            ratio_csv= Path(f"stripe_ratio_{id_val}.csv")
            self.compute_stripe_ratio(df_glue, ratio_csv)

        # 全部終わったら final Quotation
        self.finalize_quotation_csv(Path("final_quotation.csv"))
        logging.info("[main_process] All done => final_quotation.csv")