import streamlit as st
import google.generativeai as genai
import tempfile
import os

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 提词器", layout="wide")

# --- 2. 注入“美颜”样式 (CSS) ---
# 这里是控制字号和颜色的关键，不要改动里面的 px 数值
st.markdown("""
<style>
    /* 全局背景色：高级米色 */
    .stApp {
        background-color: #F2F0E9;
    }
    
    /* 强制使用衬线字体，更有电影剧本感 */
    * {
        font-family: 'Times New Roman', serif !important;
    }

    /* 【核心台词】样式：字号 60px，行高 1.3，深黑色 */
    .stMarkdown h1 {
        font-size: 60px !important;
        line-height: 1.3 !important;
        color: #1a1a1a !important;
        font-weight: 800 !important;
        margin-bottom: 30px !important;
        margin-top: 20px !important;
    }

    /* 【动作指导】样式：字号 24px，灰色，左侧有竖线 */
    .stMarkdown blockquote {
        font-size: 24px !important;
        color: #666666 !important;
        border-left: 5px solid #d4af37 !important; /* 金色竖线 */
        background-color: rgba(255,255,255,0.5) !important;
        padding: 15px !important;
        font-style: italic !important;
    }
    
    /* 分割线样式 */
    hr {
        margin-top: 50px !important;
        margin-bottom: 50px !important;
        border-color: #000000 !important;
        opacity: 0.1;
    }
    
    /* 隐藏顶部红条和菜单，让界面更干净 */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏设置 ---
with st.sidebar:
    st.header("⚙️ 设置")
    # 自动读取后台 Key，读取不到才显示输入框
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")
    
    st.info("💡 提示：录音结束后，AI 会自动生成大字号提词卡。")

# --- 4. 主程序逻辑 ---
st.title("🎙️ AI 口播提词器 (iPad 版)")

audio_value = st.audio_input("点击录音")

if audio_value and api_key:
    genai.configure(api_key=api_key)
    
    # 显示一个加载动画
    with st.spinner("AI (Gemini 2.5) 正在把你的话变成剧本..."):
        try:
            # 1. 处理音频文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                tmp.write(audio_value.read())
                tmp_path = tmp.name

            # 2. 上传给 Google
            myfile = genai.upload_file(tmp_path)
            
            # 3. 核心指令 (Prompt)
            # 注意：这里我们强制 AI 用 # (一级标题) 来写台词，这样 CSS 才能把字放大
            prompt = """
            你是一位专业编剧。请将这段语音内容改写为【提词器专用稿】。
            
            格式严格要求：
            1. 每一屏内容之间用 `---` 分隔。
            2. 【口播台词】必须使用Markdown的一级标题 `#` 开头。这是最重要的，否则字会很小。
            3. 【动作/表情】必须使用引用符号 `>` 开头，放在台词上方。
            4. 去掉所有废话，只输出内容。
            """

            # 4. 调用最新模型 (Gemini 2.5 Flash)
            model = genai.GenerativeModel("gemini-2.5-flash")
            result = model.generate_content([prompt, myfile])
            
            # 5. 展示结果
            st.divider()
            st.markdown(result.text)
            
            # 6. 清理垃圾
            os.remove(tmp_path)

        except Exception as e:
            st.error(f"出错了: {e}")

elif audio_value and not api_key:
    st.warning("请在左侧填入 API Key")
