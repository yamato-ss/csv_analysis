
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb

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

def train_and_predict_lgb(df):
    df['台番号'] = pd.to_numeric(df['台番号'], errors='coerce')
    df['G数'] = pd.to_numeric(df['G数'], errors='coerce')
    df['末尾'] = df['台番号'] % 10
    df['曜日'] = df['日付'].dt.dayofweek
    df['スコア'] = df['差枚'] * (df['G数'] / df['G数'].mean())
    df['高設定'] = (df['差枚'] > 1000).astype(int)
    features = ['G数', '差枚', '曜日', '末尾', 'スコア', '機種名']
    df = df.dropna(subset=features)
    le = LabelEncoder()
    df['機種名'] = le.fit_transform(df['機種名'])
    X = df[features]
    y = df['高設定']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=True)
    model = lgb.LGBMClassifier()
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    report = classification_report(y_test, pred, output_dict=False)
    latest_date = df['日付'].max()
    predict_target = df[df['日付'] == latest_date].copy()
    predict_target['予測確率'] = model.predict_proba(predict_target[features])[:, 1]
    top_preds = predict_target.sort_values('予測確率', ascending=False).head(10)
    output = [f"🧠 LightGBM 狙い台予測結果（{latest_date.date()}）\n", report, "\n🎯 狙い台候補:"]
    output.append(top_preds[['機種名', '台番号', 'G数', '差枚', 'スコア', '予測確率']].to_string(index=False))
    return "\n".join(output)
