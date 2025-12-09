import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 影子写手", layout="wide")

# --- 2. 注入“沉浸式”视觉样式 (CSS) ---
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

    /* 标题样式 (分析报告用) */
    h2 {
        color: #1a1a1a !important;
        font-size: 32px !important;
        border-bottom: 2px solid #000;
        padding-bottom: 10px;
        margin-top: 40px !important;
    }

    /* --- 核心：提词器大字报样式 --- */
    /* 只有用 # 开头的文字才会变大，方便朗读 */
    .stMarkdown h1 {
        font-size: 65px !important; /* 字号加大到 65px */
        line-height: 1.4 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        margin-bottom: 40px !important;
        text-align: left;
    }

    /* 动作指导 (引用块) */
    .stMarkdown blockquote {
        font-size: 24px !important;
        color: #666666 !important;
        border-left: 6px solid #d4af37 !important;
        background-color: rgba(255,255,255,0.6) !important;
        padding: 20px !important;
        font-style: italic !important;
        margin-bottom: 10px !important;
    }

    /* 按钮样式优化 */
    .stButton button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        font-size: 20px !important;
        padding: 10px 30px !important;
        border-radius: 30px !important;
        border: none !important;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #333333 !important;
    }

    /* 隐藏顶部红条 */
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
    
    st.info("💡 提示：AI 会学习你的语气，生成带有你个人风格的【逐字稿】。")

# --- 4. 主程序 ---
st.title("🗣️ AI 影子写手 (风格克隆版)")
st.markdown("像你一样说话，但说得更漂亮。")

# 录音组件
audio_value = st.audio_input("点击录音 (随便聊聊你的想法)")

if audio_value:
    st.success("✅ 录音已捕获！点击下方按钮开始生成逐字稿。")
    
    if st.button("✍️ 生成我的口播稿", type="primary"):
        
        if not api_key:
            st.warning("请先在左侧填入 Google API Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("正在学习你的语气并撰写稿件... (Gemini 2.5)"):
            try:
                # 1. 保存音频
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(audio_value.read())
                    tmp_path = tmp.name

                # 2. 上传音频
                myfile = genai.upload_file(tmp_path)
                
                # 3. 核心 Prompt (已更新为风格克隆+逐字稿模式)
                prompt = """
                你是一位顶级演讲撰稿人。请仔细听这段录音，完成以下两个任务：

                **任务一：风格学习 (Style Analysis)**
                1.
