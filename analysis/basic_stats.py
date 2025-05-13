
def analyze_by_weekday(df):
    weekday_labels = ['月', '火', '水', '木', '金', '土', '日']
    df['曜日'] = df['日付'].dt.dayofweek.map(lambda x: weekday_labels[x] if pd.notnull(x) else '')
    df['勝ち'] = df['差枚'] > 0
    stats = df.groupby(['ホール名', '曜日', '機種名'])['勝ち'].mean().reset_index()
    stats.columns = ['ホール名', '曜日', '機種名', '勝率']
    result = []
    for hall_name, group in stats.groupby('ホール名'):
        result.append(f"🏢 ホール名: {hall_name}")
        top10 = group.sort_values('勝率', ascending=False).head(10)
        result.append(top10.to_string(index=False))
        result.append("")
    return "\n".join(result)

def analyze_machine_trend(df):
    trend = df.groupby(['ホール名', '日付', '機種名'])['差枚'].mean().reset_index()
    result = []
    for hall_name, group in trend.groupby('ホール名'):
        result.append(f"🏢 ホール名: {hall_name}")
        recent_dates = group['日付'].dropna().unique()
        recent_dates = sorted(recent_dates)[-10:]
        recent = group[group['日付'].isin(recent_dates)]
        pivot = recent.pivot(index='日付', columns='機種名', values='差枚').fillna(0)
        top_machines = pivot.mean().sort_values(ascending=False).head(3).index
        display_df = pivot[top_machines]
        result.append("[平均差枚推移 上位機種（最近10日）]")
        result.append(display_df.to_string())
        result.append("")
    return "\n".join(result)

def perform_analysis(df):
    result = []
    positive_df = df[df['差枚'] > 1000].copy()
    positive_df = positive_df.sort_values(['ホール名', '機種名', '台番号', '日付'])
    positive_df['間隔'] = positive_df.groupby(['ホール名', '機種名', '台番号'])['日付'].diff().dt.days
    positive_df = positive_df[positive_df['間隔'].notna()]
    positive_df = positive_df[positive_df['間隔'] <= 60]
    debug_summary = positive_df['間隔'].describe().to_string()
    result.append("[debug] プラス差枚の出現間隔（日数）:\n" + debug_summary)
    周期傾向 = positive_df.groupby(['ホール名', '機種名', '台番号'])['間隔'].mean().reset_index()
    result.append("\n[狙い目候補（周期的に出やすい台）]:")
    result.append(周期傾向.sort_values('間隔').head(10).to_string(index=False))
    return "\n".join(result)

def analyze_high_win_freq(df):
    win_df = df[df['差枚'] > 1000]
    result = []
    for hall_name, group in win_df.groupby('ホール名'):
        result.append(f"🏢 ホール名: {hall_name}")
        freq = group.groupby(['機種名', '台番号']).size().reset_index(name='出現回数')
        top10 = freq.sort_values('出現回数', ascending=False).head(10)
        result.append("[差枚+1000以上 出現頻度トップ10]")
        result.append(top10.to_string(index=False))
        result.append("")
    return "\n".join(result)

def analyze_tail_numbers(df):
    df['台番号'] = pd.to_numeric(df['台番号'], errors='coerce')
    df = df[df['台番号'].notna()]
    df['末尾'] = df['台番号'].astype(int) % 10
    win_df = df[df['差枚'] > 1000]
    result = []
    for hall_name, group in win_df.groupby('ホール名'):
        result.append(f"🏢 ホール名: {hall_name}")
        tail_counts = group['末尾'].value_counts().sort_index()
        result.append("🔢 末尾別 +1000枚 出現回数:")
        result.append(tail_counts.to_string())
        result.append("")
    return "\n".join(result)

def analyze_consecutive_hits(df):
    df['台番号'] = pd.to_numeric(df['台番号'], errors='coerce')
    df = df[df['台番号'].notna()]
    win_df = df[df['差枚'] > 1000]
    result = []
    for hall_name, group in win_df.groupby(['ホール名', '日付']):
        hall, date = hall_name
        group = group.sort_values('台番号')
        numbers = group['台番号'].astype(int).tolist()
        streaks = []
        current_streak = [numbers[0]] if numbers else []
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i - 1] + 1:
                current_streak.append(numbers[i])
            else:
                if len(current_streak) >= 3:
                    streaks.append(current_streak[:])
                current_streak = [numbers[i]]
        if len(current_streak) >= 3:
            streaks.append(current_streak)
        if streaks:
            result.append(f"🏢 {hall} ({date.date()}): 3連番以上の出現")
            for s in streaks:
                result.append(f"  → {s}")
            result.append("")
    if not result:
        return "3連番以上の出現は確認されませんでした。"
    return "\n".join(result)
