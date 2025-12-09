import streamlit as st
import google.generativeai as genai
import tempfile
import os

# 1. 页面设置
st.set_page_config(page_title="AI 影子写手", layout="wide")

# 2. 样式设置 (已简化)
st.markdown("""
<style>
.stApp {background-color: #F2F0E9;}
h1 {font-size: 50px !important; line-height: 1.4 !important;}
blockquote {border-left: 5px solid #d4af37; background-color: #f9f9f9; padding: 10px;}
</style>
""", unsafe_allow_html=True)

# 3. 核心提示词
PROMPT = """
你是一位演讲撰稿人。请听录音，模仿用户的语言风格，将内容改写为一篇适合朗读的逐字稿。
要求：
1. 黄金三秒开场。
2. 核心内容分点。
3. 结尾金句。
格式要求：台词用 # 开头，动作指导用 > 开头。
"""

# 4. 侧边栏设置
with st.sidebar:
    st.header("设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

# 5. 主程序
st.title("AI 影子写手")
st.write("录制你的草稿，生成完美逐字稿。")

audio_value = st.audio_input("点击录音")

if audio_value:
    st.info("录音已完成，请点击下方按钮。")
    
    if st.button("生成文案", type="primary"):
        if not api_key:
            st.error("请在左侧填入 Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("AI 正在写作..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(audio_value.read())
                    tmp_path = tmp.name

                myfile = genai.upload_file(tmp_path)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                result = model.generate_content([PROMPT, myfile])
                
                st.markdown("---")
                st.markdown(result.text)
                
                os.remove(tmp_path)
            except Exception as e:
                st.error(f"出错: {e}")
