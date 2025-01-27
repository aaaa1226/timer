import streamlit as st
import time
from datetime import datetime, timedelta
from math import pi, cos, sin
import openai

# OpenAI API key
openai.api_key = st.secrets["APIKEY"]

# タイトル
st.title("勉強時間計測アプリ")

# モード選択
mode = st.radio("モードを選択してください", ["ストップウォッチ", "タイマー"])

# 勉強科目と分野の入力
topic = st.text_input("教科を入力してください")
field = st.text_input("分野を入力してください")

# 目標勉強時間の設定
goal_time = st.number_input("1日の目標勉強時間 (時間)", min_value=0, max_value=24, step=1, value=0)
st.write(f"今日の目標: {goal_time} 時間")

# 時間記録
data = st.session_state.get("data", [])
if "data" not in st.session_state:
    st.session_state["data"] = []

def format_time(seconds):
    """Convert seconds to hh:mm:ss."""
    return str(timedelta(seconds=int(seconds)))

if mode == "ストップウォッチ":
    if st.button("スタート"):
        start_time = time.time()
        while True:
            elapsed = time.time() - start_time
            st.metric("経過時間", format_time(elapsed))
            time.sleep(1)
            if st.button("ストップ"):
                st.session_state["data"].append((topic, field, elapsed))
                break

elif mode == "タイマー":
    hours = st.number_input("時間", min_value=0, max_value=40, step=1)
    minutes = st.number_input("分", min_value=0, max_value=59, step=1)
    seconds = st.number_input("秒", min_value=0, max_value=59, step=1)
    total_seconds = int(hours * 3600 + minutes * 60 + seconds)

    if st.button("スタート"):
        end_time = datetime.now() + timedelta(seconds=total_seconds)
        while True:
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining <= 0:
                st.write("タイマー終了！")
                break
            st.metric("残り時間", format_time(remaining))
            time.sleep(1)

# データを表示
if st.button("記録を表示"):
    st.write("勉強記録:")
    for record in st.session_state["data"]:
        st.write(f"教科: {record[0]}, 分野: {record[1]}, 時間: {format_time(record[2])}")
