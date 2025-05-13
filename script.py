import gradio as gr
from .loader import load_and_prepare
from .utils import get_japanese_font
from .analysis.basic_stats import *
from .analysis.visualization import *
from .analysis.machine_learning import *

df = None
jp_font = get_japanese_font()

def analyze_csv(file):
    global df
    df = load_and_prepare(file)
    return f"[csv_analysis] CSV読込成功: {file.name}"

def setup():
    print("[csv_analysis] 拡張機能が読み込まれました。")

def ui():
    with gr.Blocks() as block:
        with gr.Row():
            file_input = gr.File(label="CSVファイルをアップロード")
            load_button = gr.Button("読み込み")
        load_output = gr.Textbox(label="読み込み結果")

        load_button.click(analyze_csv, inputs=file_input, outputs=load_output)

        # 分析ボタン（詳細は省略。必要に応じて追加）
        # 例:
        # analyze_button = gr.Button("分析実行")
        # analyze_button.click(perform_analysis, outputs=...)

    return block
