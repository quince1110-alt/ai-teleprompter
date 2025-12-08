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
        width: 100%;
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
    
    # --- 按钮区域 ---
    if st.button("🎬 生成导演分析报告", type="primary"):
        
        if not api_key:
            st.warning("请先在左侧填入 Google API Key")
            st.stop()

        genai.configure(api_key=api_key)
        
        with st.spinner("导演正在回放你的录音，分析情绪与逻辑... (Gemini 2.5)"):
            try:
                # --- 注意：这里的代码必须缩进，不能顶格 ---
                
                # 1. 保存音频
                with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
                    tmp.write(audio_value.read())
                    tmp_path = tmp.name

                # 2. 上传音频
                myfile = genai.upload_file(tmp_path)
                
                # 3. 核心 Prompt
                prompt = """
                你是一位金牌短视频导演。请仔细听这段录音，严格按照以下流程进行处理：

                **Process:**
                1.  **听觉分析 (Audio Analysis):** 仔细听说话人的语调、重音、语速变化和情绪状态。
                2.  **逻辑提炼 (Logic Extraction):** 剔除口癖（呃、然后、那个）、重复和无效废话，提取核心观点。
                3.  **结构化重组 (Restructuring):** 将内容重组为适合短视频的“钩子-干货-结尾”结构。

                **Output Format (请严格按照以下 Markdown 格式输出，不要改变标题层级):**

                ## 🎬 导演分析报告

                **1. 语感与人设诊断:**
                * **当前状态:** [描述你听到的情绪]
                * **建议镜头表现:** [给出一个具体的建议]

                ## 2. 拍摄提词卡 (Teleprompter Cards)
                *(Note: 这里不要写逐字稿！只写引导性的关键词和逻辑点)*

                **【卡片 1：黄金前三秒 (The Hook)】**
                * **引导动作:** [例如：直视镜头，甚至可以皱眉]
                * **关键台词/问题:** [提炼出一个能抓住观众注意力的问题]

                **【卡片 2：核心观点 (The Point)】**
                * **逻辑关键词:** [列出3-5个核心词]
                * **引导话术:** "试着解释一下为什么 [关键词] 很重要..."
                * **情绪提示:** [例如：这里需要真诚一点]

                **【卡片 3：案例/证据 (The Proof)】**
                * **素材回忆:** [提取音频中提到的例子或故事]
                * **引导:** "讲讲那个关于 [具体例子] 的故事，不用太细，突出结果就行。"

                **【卡片 4：结尾与行动 (Call to Action)】**
                * **金句提炼:** [升华出一句简短有力的金句]
                * **动作:** [引导用户做什么]

                ---
                **Director's Note:** [简短的导演批注]
                """

                # 4. 调用模型
                model = genai.GenerativeModel("gemini-2.5-flash")
                result = model.generate_content([prompt, myfile])
                
                # 5. 显示结果
                st.divider()
                st.markdown(result.text)
                
                # 6. 清理
                os.remove(tmp_path)

            except Exception as e:
                st.error(f"发生错误: {e}")
