import streamlit as st
import google.generativeai as genai
import tempfile
import os
import re

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="AI 影子写手", layout="wide")

# --- 2. CSS 样式配置 ---
BASE_CSS = """
<style>
    /* 全局样式：米色背景，深色文字 */
    .stApp { background-color: #F2F0E9 !important; }
    html, body, [class*="css"], .stMarkdown, .stMarkdown p { color: #1a1a1a !important; }
    h1, h2, h3 { color: #000000 !important; font-family: 'Times New Roman', 'Songti SC', serif !important; }

    /* 按钮样式 */
    .stButton button {
        background-color: #1a1a1a !important; color: #ffffff !important;
        border-radius: 30px !important; width: 100%; border: none !important; padding: 10px 0 !important;
    }
    .stButton button:hover { background-color: #333333 !important; }
    
    /* 优化 Tab 样式 */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px; background-color: #e0e0d0; border-radius: 10px 10px 0 0; color: #333;
    }
    .stTabs [aria-selected="true"] { background-color: #1a1a1a; color: white; }

    header, footer {visibility: hidden;}
</style>
"""

# 提词器专用大字号样式
TELEPROMPTER_CSS = """
<style>
    /* 提词模式下，# 开头的标题变大 */
    .stMarkdown h1 { font-size: 60px !important; line-height: 1.4 !important; margin-bottom: 30px !important; font-weight: 800 !important; }
    /* 动作指导 */
    .stMarkdown blockquote { font-size: 24px !important; color: #666; border-left: 6px solid #d4af37 !important; background-color: rgba(255,255,255,0.6) !important; padding: 15px !important; font-style: italic !important; }
</style>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)

# --- 3. 核心提示词 (Prompt) ---
# 这里的指令专门针对“朴实、去口癖、结构化”进行了优化
PROMPT = """
你是一位金牌内容编辑。请听录音，基于作者的原意，整理出一篇**朴实、自然、没有口癖**的口播文案。

**核心要求：**
1. **去水词**：完全删掉“呃、然后、那个”等废话。
2. **留风格**：保留作者说话的语气（比如幽默或真诚），不要改成死板的书面语，要像在聊天。
3. **朴实感**：文案不要花俏，不要用生僻词，要接地气。

**输出结构（必须包含以下三部分）：**
1. **黄金三秒**：提炼最抓人的一句话开场。
2. **核心内容**：整理中间的干货逻辑，润色为通顺的口语表达。
3. **收束文案**：结尾总结，引导行动。

**Output Format (Markdown):**
为了同时满足“阅读”和“提词”，请每一句口播词都用 `#` 开头。
(动作指导用 `>` 开头)

示例格式：
## 📝 风格诊断
* **情绪:** [描述]

---

## 🎥 口播文案

**【Part 1：黄金三秒】**
> [动作指导]
# 这里写第一句台词。

**【Part 2：核心内容】**
> [动作指导]
# 这里是润色后的正文。
# 每一句都要用一级标题符号开头。
# 即使是长句子，也要按意群切分。

**【Part 3：收束文案】**
> [动作指导]
# 这里写结尾。
"""

# --- 4. 侧边栏 ---
with st.sidebar:
    st.header("⚙️ 设置")
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        api_key = st.text_input("输入 Google API Key", type="password")

# --- 5. 主程序 ---
st.title("🗣️ AI 影子写手")
st.write("保留风格，剔除废话，生成朴实好用的口播稿。")

audio_value = st.audio_input("点击录音")

if 'result_text' not in st.session_state:
    st.session_state.result_text = None

if audio_value:
    st.info("✅ 录音完成！")
    
    if st.button("✨ 一键整理润色", type="primary"):
        if not api_key:
            st.error("请先在左侧填入 Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("AI 正在去口癖、理逻辑..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(audio_value.read())
                    tmp_path = tmp.name

                myfile = genai.upload_file(tmp_path)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                response = model.generate_content([PROMPT, myfile])
                st.session_state.result_text = response.text
                
                os.remove(tmp_path)
            except Exception as e:
                st.error(f"出错: {e}")

# --- 6. 结果展示区 (默认显示润色版) ---
if st.session_state.result_text:
    st.divider()
    
    # 交换了顺序：润色版在前，提词器在后
    tab1, tab2 = st.tabs(["📝 整理润色版 (默认)", "📺 提词器模式"])
    
    # --- Tab 1: 润色版 (自动合并段落 + 一键复制) ---
    with tab1:
        st.caption("💡 已自动去除格式，合并为通顺段落，点击右上角图标即可复制。")
        
        # 文本清洗逻辑：把提词器的格式还原成正常文章
        raw_text = st.session_state.result_text
        
        # 1. 去掉 Markdown 标题符 (# )
        clean_text = re.sub(r'^#\s+', '', raw_text, flags=re.MULTILINE)
        # 2. 去掉动作指导 (> [...])
        clean_text = re.sub(r'>\s*\[.*?\]', '', clean_text, flags=re.MULTILINE)
        clean_text = re.sub(r'>\s*\(.*?\)', '', clean_text, flags=re.MULTILINE)
        # 3. 去掉结构标记 (如 **【Part 1...】**)
        clean_text = re.sub(r'\*\*【.*?】\*\*', '\n', clean_text)
        # 4. 关键步骤：把断开的短句合并成段落 (去除单次换行，保留双次换行)
        # 逻辑：如果一行结束不是句号/叹号/问号，说明这句话没说完，把换行符删掉拼起来
        # 但为了简单有效，我们先把多余空行去掉
        clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()
        
        # 显示复制框
        st.code(clean_text, language=None)
        
        # 可编辑区域
        st.text_area("手动微调", value=clean_text, height=400)
        
    # --- Tab 2: 提词器 (大字号) ---
    with tab2:
        st.caption("💡 iPad 横屏使用体验更佳")
        # 注入大字号 CSS
        st.markdown(TELEPROMPTER_CSS, unsafe_allow_html=True)
        # 显示原始 Markdown (保留 # 号和换行，方便朗读)
        st.markdown(st.session_state.result_text)
