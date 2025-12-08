-- coding: utf-8 --
import streamlit as st import google.generativeai as genai import tempfile import os

--- 1. 页面配置 ---
st.set_page_config(page_title="AI 语音提词器", layout="wide")

注入美学样式
st.markdown(""" <style> .stApp { background-color: #F2F0E9; color: #000000; } * { font-family: 'Times New Roman', Times, serif !important; } h1, h2, h3 { color: #000000 !important; } .teleprompter-text h1 { font-size: 50px !important; line-height: 1.4; } blockquote { border-left: 3px solid #000; background-color: transparent; } </style> """, unsafe_allow_html=True)

--- 2. 侧边栏 ---
with st.sidebar: st.header("⚙️ 设置") # 优先读取 Secrets if "GOOGLE_API_KEY" in st.secrets: api_key = st.secrets["GOOGLE_API_KEY"] else: api_key = st.text_input("请输入 Google API Key", type="password")

--- 3. 主程序 ---
st.title("🎙️ AI 口播提词器") st.markdown("录制你的口播草稿，AI 将自动生成带情绪指导的 iPad 提词卡。")

audio_value = st.audio_input("点击录音")

if audio_value and api_key: genai.configure(api_key=api_key)

elif audio_value and not api_key: AIzaSyBMt_E2oF2eyfkxPdlKXuNG2igimv8x11g("👈 请先在左侧填入 API Key")
