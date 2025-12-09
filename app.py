import streamlit as st
import google.generativeai as genai
import tempfile
import os
import re

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 影子写手", layout="wide")

# --- 2. CSS 样式配置 ---
# 基础样式：强制米色背景，修复手机端看不清的问题
BASE_CSS = """
<style>
    /* 强制全局背景色 */
    .stApp {
        background-color: #F2F0E9 !important;
    }
    
    /* 强制全局文字颜色为深黑 (修复 iOS 暗黑模式 BUG) */
    html, body, [class*="css"], .stMarkdown, .stMarkdown p {
        color: #1a1a1a !important; 
    }
    
    /* 标题颜色 */
    h1, h2, h3 {
        color: #000000 !important;
        font-family: 'Times New Roman', 'Songti SC', serif !important;
    }

    /* 按钮样式 */
    .stButton button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border-radius: 30px !important;
        width: 100%;
        border: none !important;
        padding: 10px 0 !important;
    }
    .stButton button:hover {
        background-color: #333333 !important;
    }
    
    /* 调整 Tab 标签页的样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e0e0d0;
        border-radius: 10px 10px 0 0;
        padding: 0 20px;
        color: #333;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a1a1a;
        color: white;
    }

    /* 隐藏顶部红条 */
    header, footer {visibility: hidden;}
</style>
"""

# 提词器专用样式：超大字号
TELEPROMPTER_CSS = """
<style>
    /* 只有在提词模式下，# 开头的标题才会变得巨大 */
    .stMarkdown h1 {
        font-size: 60px !important;
        line-height: 1.4 !important;
        margin-bottom: 30px !important;
        font-weight: 800 !important;
    }
    
    /* 动作指导样式 */
    .stMarkdown blockquote {
        font-size: 24px !important;
        color: #666666 !important;
        border-left: 6px solid #d4af37 !important;
        background-color: rgba(255,255,255,0.6) !important;
        padding: 15px !important;
        font-style: italic !important;
    }
</style>
"""

# 注入基础样式
st.markdown(BASE_CSS, unsafe_allow_html=True)

# --- 3. 核心提示词 (Prompt) ---
PROMPT = """
你是一位金牌口播修稿师。请听录音，完成以下任务：

**任务目标：**
将用户的语音内容，改写为一篇**可以直接照着念的完美逐字稿**。
1. **风格克隆**：保留用户的个人语感（幽默/犀利/亲切），但**剔除所有废话、口癖和逻辑跳跃**。
2. **视觉断句**：为了方便提词器阅读，**请强制换行**。每行不要超过 15 个字。哪怕一句话没说完，只要意群到了就换行。

**结构要求：**
1. **黄金三秒**：开场第一句话必须抓人。
2. **核心干货**：中间逻辑分点清晰。
3. **金句结尾**：最后一句要升华或引导互动。

**输出格式 (Markdown):**

## 📝 风格诊断
* **情绪:** [例如：自信笃定]
* **建议:** [例如：保持语速]

---

## 🎥 拍摄逐字稿

**【Part 1：黄金开场】**
> [动作指导]
# 这里写第一句台词(用#开头)

**【Part 2：核心内容】**
> [动作指导]
# 正文内容开始(用#开头)
# 记得强制换行

**【Part 3：强力结尾】**
> [动作指导]
# 结尾金句(用#开头)
"""

# --- 4. 侧边栏逻辑 ---
with st.sidebar:
    st.header("⚙️ 设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

# --- 5. 主程序逻辑 ---
st.title("🗣️ AI 影子写手")
st.write("保留你的风格，剔除你的废话。")

audio_value = st.audio_input("点击录音")

# 初始化 session_state
if 'result_text' not in st.session_state:
    st.session_state.result_text = None

if audio_value:
    st.info("✅ 录音完成！")
    
    if st.button("✨ 生成我的完美口播稿", type="primary"):
        if not api_key:
            st.error("请先在左侧填入 Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("AI 正在精修文案..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(audio_value.read())
                    tmp_path = tmp.name

                myfile = genai.upload_file(tmp_path)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                # 获取结果并存入 session
                response = model.generate_content([PROMPT, myfile])
                st.session_state.result_text = response.text
                
                os.remove(tmp_path)
            except Exception as e:
                st.error(f"出错: {e}")

# --- 6. 结果展示区 (双模式切换) ---
if st.session_state.result_text:
    st.divider()
    
    # 使用 Tabs 标签页来区分两个功能
    tab1, tab2 = st.tabs(["📺 提词器模式", "📝 整理润色版 (可复制)"])
    
    # --- Tab 1: 提词器 (大字号) ---
    with tab1:
        st.caption("💡 提示：将 iPad 横屏，字体会自动变大。")
        # 注入大字号 CSS
        st.markdown(TELEPROMPTER_CSS, unsafe_allow_html=True)
        # 显示原始 Markdown (#号会被渲染为大标题)
        st.markdown(st.session_state.result_text)
        
    # --- Tab 2: 润色版 (纯文本 + 复制按钮) ---
    with tab2:
        st.caption("💡 提示：点击代码框右上角的“复制”图标，即可一键复制全文。")
        
        # 1. 文本清洗：去掉 # 号，去掉动作指导，去掉多余空行
        clean_text = st.session_state.result_text
        # 去掉 markdown 标题符 #
        clean_text = re.sub(r'^#\s+', '', clean_text, flags=re.MULTILINE)
        # 去掉动作指导 > [xxx]
        clean_text = re.sub(r'>\s*\[.*?\]', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'>\s*\(.*?\)', '', clean_text, flags=re.MULTILINE)
        # 去掉 "## 🎥 拍摄逐字稿" 这种大标题，只保留正文
        clean_text = re.sub(r'##.*', '', clean_text)
        # 去掉 "【Part 1...】" 这种标记
        clean_text = re.sub(r'\*\*【.*?】\*\*', '', clean_text)
        # 去除多余空行，让排版更紧凑
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()
        
        # 2. 显示一键复制框
        # st.code 是 Streamlit 自带“复制按钮”的组件，我们把语言设为 None，它就变成了纯文本框
        st.code(clean_text, language=None)
        
        # 3. 如果用户还需要手动编辑，提供一个文本框
        st.text_area("手动微调区", value=clean_text, height=300)
