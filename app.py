import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 影子写手", layout="wide")

# --- 2. 注入 CSS 样式 (已简化，防止报错) ---
st.markdown("""
<style>
    .stApp {background-color: #F2F0E9;}
    * {font-family: 'Times New Roman', 'Songti SC', serif !important;}
    h2 {color: #1a1a1a !important; border-bottom: 2px solid #000; padding-bottom: 10px; margin-top: 40px !important;}
    .stMarkdown h1 {font-size: 65px !important; line-height: 1.4 !important; color: #000 !important; font-weight: 800 !important;}
    .stMarkdown blockquote {font-size: 24px !important; color: #666; border-left: 6px solid #d4af37 !important; background-color: rgba(255,255,255,0.6) !important; padding: 20px !important; font-style: italic !important;}
    .stButton button {background-color: #1a1a1a !important; color: #fff !important; width: 100%; border-radius: 30px !important;}
    header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. 定义核心提示词 (放在变量里，更安全) ---
PROMPT_CONTENT = """
你是一位顶级演讲撰稿人。请听录音，完成任务：
1. **风格学习**: 捕捉说话人的情绪（兴奋/冷静）和语言风格（幽默/严谨）。
2. **撰写逐字稿**: 基于录音内容，**模仿用户风格**，改写为一篇可以直接照着念的逐字稿。

**输出格式 (Markdown):**

## 📝 风格分析
* **情绪:** [描述]
* **建议:** [描述]

---

## 🎥 拍摄逐字稿

**【Part 1：黄金三秒】**
> (动作指导)
# 这里写第一句台词(一级标题)。

**【Part 2：核心内容】**
> (动作指导)
# 这里写正文内容。
# 每一句都要用 # 开头。

**【Part 3：结尾】**
> (动作指导)
# 金句收尾。
"""

# --- 4. 侧边栏设置 ---
with st.sidebar:
    st.header("⚙️ 设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

# --- 5. 主程序 ---
st.title("🗣️ AI 影子写手 (风格克隆版)")
st.markdown("像你一样说话，但说得更漂亮。")

audio_value = st.audio_input("点击录音")

if audio_value:
    st.success("
