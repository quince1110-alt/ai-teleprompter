import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 视频导演", layout="wide")

# --- 2. 注入“导演级”视觉样式 (CSS) ---
st.markdown("""
<style>
    /* 全局背景：高级米色 */
    .stApp {
        background-color: #F2F0E9;
    }
    
    /* 字体：衬线体，剧本感 */
    * {
        font-family: 'Times New Roman', 'Songti SC', serif !important;
    }

    /* 标题 (## 🎬 导演分析报告) */
    h2 {
        color: #1a1a1a !important;
        font-size: 36px !important;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        margin-top: 40px !important;
    }

    /* 重点强调 (加粗部分) */
    strong {
        color: #8B4513 !important; /* 导演批注用深棕色 */
        font-weight: 900 !important;
    }

    /* --- 核心：提词卡片区域样式 --- */
    
    /* 识别“【卡片”开头的文字，让它变得巨大 */
    p, li {
        font-size: 22px !important;
        line-height: 1.6 !important;
        color: #333 !important;
    }

    /* 让列表项更清晰 */
    ul {
        background-color: rgba(255,255,255,0.4);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 隐藏不需要的元素 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏 ---
with st.sidebar:
    st.header("⚙️ 设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")
    
    st.info("💡 AI 导演正在待命：它将分析你的语感，并生成引导式提词卡。")

# --- 4. 主程序 ---
st.title("🎬 AI 视频导演")
st.markdown("捕捉瞬间的灵感，即刻生成专业的拍摄脚本。")

audio_value = st.audio_input("点击录音")

if audio_value and api_key:
    genai.configure(api_key=api_key)
