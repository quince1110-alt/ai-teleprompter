import streamlit as st
import google.generativeai as genai
import tempfile
import os

st.set_page_config(page_title="AI 提词器", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #F2F0E9; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

  st.title("🎙️ AI 口播提词器")

audio_value = st.audio_input("点击录音")

if audio_value and api_key:
    genai.configure(api_key=api_key)
    with st.spinner("AI 正在思考..."):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(audio_value.read())
                tmp_path = tmp.name

            myfile = genai.upload_file(tmp_path)
            
            prompt = "请将这段音频内容改写为适合 iPad 投屏的提词卡。要求：用 --- 分页，用 # 做大标题，用 > 做动作提示。"

            model = genai.GenerativeModel("gemini-1.5-flash")
            result = model.generate_content([prompt, myfile])
            
            st.markdown(result.text)
            os.remove(tmp_path)
        except Exception as e:
            st.error(e)

elif audio_value and not api_key:
    AIzaSyBMt_E2oF2eyfkxPdlKXuNG2igimv8x11g("请在左侧填入 Key")

