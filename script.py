import gradio as gr
from .loader import *
from .utils import get_japanese_font
from .analysis.basic_stats import *
from .analysis.visualization import *
from .analysis.machine_learning import *
from .analysis.forecasting import *
import re

jp_font = get_japanese_font()

def clean_machine_name(name):
    return re.sub(r'（\d+台）$', '', name)

def setup():
    print("[csv_analysis] 拡張機能が読み込まれました（Prophet UI対応）")

def forecast_wrapper(hall_name, machine_dropdown_value, days):
    df = get_df()
    if df is None:
        return "❌ 先にCSVを読み込んでください。"
    target = df[df["ホール名"] == hall_name]
    # 分解して機種名のみ取り出す
    machine_name = clean_machine_name(machine_dropdown_value)
    return forecast_machine_with_prophet(target, machine_name, days)

def batch_wrapper(days):
    df = get_df()
    if df is None:
        return "❌ 先にCSVを読み込んでください。"
    return batch_forecast_all(df, days)

def load_and_update(file):
    msg = analyze_csv(file)
    return msg, gr.update(choices=get_halls())

def ui():
    with gr.Blocks() as block:
        with gr.Row():
            file_input = gr.File(label="CSVファイルをアップロード")
            load_button = gr.Button("読み込み")
        load_output = gr.Textbox(label="読み込み結果")

        hall_dropdown = gr.Dropdown(label="ホール名", choices=[], interactive=True)
        machine_dropdown = gr.Dropdown(label="機種名（最新のみ）", choices=[], interactive=True)
        days_input = gr.Slider(label="予測日数", minimum=3, maximum=14, step=1, value=7)

        with gr.Row():
            predict_button = gr.Button("Prophetによる差枚予測")
            batch_button = gr.Button("全ホール一括予測（保存）")

        predict_image = gr.Image(label="予測グラフ")
        batch_output = gr.Textbox(label="一括実行ログ", lines=15)

        load_button.click(load_and_update, inputs=file_input, outputs=[load_output, hall_dropdown])
        hall_dropdown.change(lambda h: gr.update(choices=get_latest_machines(h)), inputs=hall_dropdown, outputs=machine_dropdown)
        predict_button.click(forecast_wrapper, inputs=[hall_dropdown, machine_dropdown, days_input], outputs=predict_image)
        batch_button.click(batch_wrapper, inputs=days_input, outputs=batch_output)

    return block
