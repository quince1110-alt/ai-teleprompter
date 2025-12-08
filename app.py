import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- Part 1: 页面基础设置 ---
st.set_page_config(page_title="AI 提词器", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #F2F0E9; }
</style>
""", unsafe_allow_html=True)

# --- Part 2: 侧边栏 ---
with st.sidebar:
    st.header("设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

# --- Part 3: 主程序 ---
st.title("🎙️ AI 口播提词器")
st.markdown("录制你的口播草稿，AI 将自动生成带情绪指导的 iPad 提词卡。")

audio_value = st.audio_input("点击录音")

if audio_value and api_key:
    genai.configure(api_key=api_key)
    with st.spinner("AI (Gemini 2.5) 正在思考..."):
        try:
            # 保存临时录音文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(audio_value.read())
                tmp_path = tmp.name

            # 上传给 Google
            myfile = genai.upload_file(tmp_path)
            
            # 核心 Prompt
            prompt = "请将这段音频内容改写为适合 iPad 投屏的提词卡。要求：用 --- 分页，用 # 做大标题，用 > 做动作提示。"

            # 【已修复】使用你账号列表里存在的最新模型
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            result = model.generate_content([prompt, myfile])
            
            # 显示结果
            st.markdown(result.text)
            
            # 删除临时文件
            os.remove(tmp_path)
        except Exception as e:
            st.error(f"发生错误: {e}")

elif audio_value and not api_key:
   AIzaSyBMt_E2oF2eyfkxPdlKXuNG2igimv8x11g("请在左侧填入 Key")
