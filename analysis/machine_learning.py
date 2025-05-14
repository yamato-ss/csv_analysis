
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import pandas as pd

def compute_high_setting_score(df):
    df['スコア'] = df['差枚'] * (df['G数'] / df['G数'].mean())
    df['スコア'] = df['スコア'].fillna(0)
    result = []
    for hall_name, group in df.groupby('ホール名'):
        result.append(f"🏢 ホール名: {hall_name}")
        latest_date = group['日付'].max()
        recent = group[group['日付'] == latest_date]
        top = recent.sort_values('スコア', ascending=False).head(10)
        result.append(f"[{latest_date.date()} 高設定スコア上位]")
        result.append(top[['機種名', '台番号', '差枚', 'G数', 'スコア']].to_string(index=False))
        result.append("")
    return "\n".join(result)

def predict_high_setting_xgb(df):
    if df is None or df.empty:
        return "❌ 先にCSVを読み込んでください。"

    try:
        df = df.copy()
        if "機種名コード" not in df.columns:
            df["機種名コード"] = LabelEncoder().fit_transform(df["機種名"])

        features = ["G数", "差枚", "曜日", "末尾", "スコア", "機種名コード"]
        X = df[features]
        y = df["高設定"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric="logloss", n_jobs=2)
        model.fit(X_train, y_train)

        df["予測確率"] = model.predict_proba(X)[:, 1]
        df["日付"] = pd.to_datetime(df["日付"])  # 念のため明示
        latest_date = df["日付"].max()

        recent = df[df["日付"].dt.date == latest_date.date()]
        print("最新日付:", latest_date)
        print("該当件数:", len(recent))
        print("全日付一覧:", df["日付"].dropna().sort_values().unique())

        if recent.empty:
            return f"⚠️ {latest_date.date()} のデータが存在しません。prepared_for_xgb.csv を確認してください。"

        top10 = recent.sort_values("予測確率", ascending=False).head(10)

        result = [f"🧠 XGBoost 狙い台予測（{latest_date.date()}）"]
        result.append(top10[["ホール名", "機種名", "台番号", "G数", "差枚", "スコア", "予測確率"]].to_string(index=False))
        return "\n".join(result)

    except Exception as e:
        return f"❌ 予測中にエラーが発生しました: {str(e)}"
