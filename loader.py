import pandas as pd
import numpy as np

df = None

def analyze_csv(file):
    global df
    try:
        uploaded_df = pd.read_csv(file.name, low_memory=False)
        if "スコア" in uploaded_df.columns and "曜日" in uploaded_df.columns:
            df = uploaded_df.copy()
        else:
            uploaded_df["日付"] = pd.to_datetime(uploaded_df["ファイル名"].str.extract(r"(\\d{4}-\\d{2}-\\d{2})")[0], errors="coerce")
            uploaded_df["台番号"] = pd.to_numeric(uploaded_df["台番号"], errors="coerce")
            uploaded_df["末尾"] = uploaded_df["台番号"] % 10
            uploaded_df["曜日"] = uploaded_df["日付"].dt.dayofweek
            uploaded_df["スコア"] = uploaded_df["差枚"] * (uploaded_df["G数"] / uploaded_df["G数"].mean())
            uploaded_df["高設定"] = (uploaded_df["差枚"] > 1000).astype(int)
            df = uploaded_df.copy()
        return f"[csv_analysis] CSV読込成功: {file.name}（{len(df)}件）"
    except Exception as e:
        return f"分析中にエラー: {str(e)}"
    
def get_df():
    global df
    return df

def get_halls():
    if df is not None and "ホール名" in df.columns:
        return sorted(df["ホール名"].dropna().unique().tolist())
    return []

def get_latest_machines(hall_name):
    if df is None or hall_name is None:
        return []

    latest_date = df[df["ホール名"] == hall_name]["日付"].max()
    filtered = df[(df["ホール名"] == hall_name) & (df["日付"] == latest_date)]

    machine_counts = (
        filtered.groupby("機種名")["台番号"]
        .nunique()
        .reset_index(name="台数")
        .sort_values("台数", ascending=False)
    )

    return [f"{row['機種名']}（{row['台数']}台）" for _, row in machine_counts.iterrows()]

def parse_probability_column(series):
    def extract_denominator(x):
        try:
            if isinstance(x, str) and '/' in x:
                return float(x.split('/')[1])
            else:
                return float(x)
        except:
            return np.nan
    return series.apply(extract_denominator)

def clean_numeric_columns(df):
    numeric_cols = ['G数', '差枚', 'BB', 'RB', 'ART']
    fraction_cols = ['合成確率', 'BB確率', 'RB確率', 'ART確率']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(',', '', regex=False)
                .str.replace('+', '', regex=False)
                .str.replace('−', '-', regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in fraction_cols:
        if col in df.columns:
            df[col] = parse_probability_column(df[col])

    return df

def load_and_prepare(file):
    try:
        uploaded_df = pd.read_csv(file.name, low_memory=False)

        if "スコア" in uploaded_df.columns and "曜日" in uploaded_df.columns:
            print("[csv_analysis] prepared_for_xgb.csv 構造を検出")
            df = uploaded_df.copy()
        else:
            print("[csv_analysis] raw構造と判定、前処理を実行")
            # TODO:prophet_dashboardのcombine_and_preprocessの機能を呼び出す形にしたい
            uploaded_df = clean_numeric_columns(uploaded_df)
            uploaded_df["日付"] = pd.to_datetime(uploaded_df["ファイル名"].str.extract(r"(\d{4}-\d{2}-\d{2})")[0], errors="coerce")
            uploaded_df["台番号"] = pd.to_numeric(uploaded_df["台番号"], errors="coerce")
            uploaded_df["末尾"] = uploaded_df["台番号"] % 10
            uploaded_df["曜日"] = uploaded_df["日付"].dt.dayofweek
            uploaded_df["スコア"] = uploaded_df["差枚"] * (uploaded_df["G数"] / uploaded_df["G数"].mean())
            uploaded_df["高設定"] = (uploaded_df["差枚"] > 1000).astype(int)
            df = uploaded_df.copy()

        print(f"[csv_analysis] CSV読込成功: {file.name}（{len(df)}件）")
        return df

    except Exception as e:
        return f"分析中にエラー: {str(e)}"
