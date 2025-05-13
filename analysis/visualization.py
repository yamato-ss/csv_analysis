
import matplotlib.pyplot as plt
import io
from PIL import Image
from ..utils import get_japanese_font

jp_font = get_japanese_font()

def plot_machine_trend_graph(df):
    trend = df.groupby(['ホール名', '日付', '機種名'])['差枚'].mean().reset_index()
    for hall_name, group in trend.groupby('ホール名'):
        recent_dates = group['日付'].dropna().unique()
        recent_dates = sorted(recent_dates)[-10:]
        recent = group[group['日付'].isin(recent_dates)]
        pivot = recent.pivot(index='日付', columns='機種名', values='差枚').fillna(0)
        top_machines = pivot.mean().sort_values(ascending=False).head(3).index
        plot_df = pivot[top_machines]
        fig, ax = plt.subplots(figsize=(8, 4))
        plot_df.plot(ax=ax)
        ax.set_title(f"{hall_name} - 上位3機種の差枚推移", fontproperties=jp_font)
        ax.set_ylabel("平均差枚", fontproperties=jp_font)
        ax.set_xlabel("日付", fontproperties=jp_font)
        ax.legend(prop=jp_font)
        ax.grid(True)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return Image.open(buf).convert("RGB")

def plot_score_trend(df):
    df['スコア'] = df['差枚'] * (df['G数'] / df['G数'].mean())
    df = df.dropna(subset=['スコア'])
    target_group = df.groupby(['ホール名', '台番号'])
    most_active = target_group.size().sort_values(ascending=False).head(1).index[0]
    subset = df[(df['ホール名'] == most_active[0]) & (df['台番号'] == most_active[1])]
    subset = subset.sort_values('日付')
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(subset['日付'], subset['スコア'])
    ax.set_title(f"{most_active[0]} - 台番 {most_active[1]} のスコア推移", fontproperties=jp_font)
    ax.set_xlabel("日付", fontproperties=jp_font)
    ax.set_ylabel("スコア", fontproperties=jp_font)
    ax.grid(True)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")

def plot_hall_score_dist(df):
    df['スコア'] = df['差枚'] * (df['G数'] / df['G数'].mean())
    df = df.dropna(subset=['スコア'])
    hall_scores = df.groupby('ホール名')['スコア'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    hall_scores.plot(kind='bar', ax=ax)
    ax.set_title("ホールごとの平均スコア", fontproperties=jp_font)
    ax.set_ylabel("平均スコア", fontproperties=jp_font)
    ax.set_xlabel("ホール名", fontproperties=jp_font)
    plt.xticks(rotation=45, ha='right', fontproperties=jp_font)
    ax.grid(True)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")
