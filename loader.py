import pandas as pd
import numpy as np

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
    df = pd.read_csv(file.name, low_memory=False)
    df = clean_numeric_columns(df)
    df['日付'] = pd.to_datetime(df['ファイル名'].str.extract(r'(\d{4}-\d{2}-\d{2})')[0], errors='coerce')
    return df
