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

    /* 标题样式 */
    h2 {
        color: #1a1a1a !important;
        font-size: 36px !important;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        margin-top: 40px !important;
    }

    /* 重点强调 */
    strong {
        color: #8B4513 !important;
        font-weight: 900 !important;
    }

    /* --- 提词卡片样式 --- */
    p, li {
        font-size: 22px !important;
        line-height: 1.6 !important;
        color: #333 !important;
    }

    ul {
        background-color: rgba(255,255,255,0.4);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    
    /* 按钮样式优化 */
    .stButton button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        font-size: 20px !important;
        padding: 10px 30px !important;
        border-radius: 30px !important;
        border: none !important;
    }
    .stButton button:hover {
        background-color: #333333 !important;
    }

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
    
    st.info("💡 操作指南：\n1. 点击录音\n2. 录完后点击“生成报告”按钮")

# --- 4. 主程序 ---
st.title("🎬 AI 视频导演")
st.markdown("捕捉瞬间的灵感，即刻生成专业的拍摄脚本。")

# 录音组件
audio_value = st.audio_input("点击录音")

# 只有当录音存在时，才显示“生成按钮”
if audio_value:
    st.success("✅ 录音已保存！请点击下方按钮开始分析。")
    
    # --- 新增：手动触发按钮 ---
    if st.button("🎬 生成导演分析报告", type="primary"):
        
        if not api_key:
            st.warning("请先在左侧填入 Google API Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("导演正在回放你的录音，分析情绪与逻辑... (Gemini 2.5)"):
            try:
                #
