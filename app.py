import streamlit as st
import google.generativeai as genai
import os

st.title("🔧 故障诊断模式")

# 1. 检查库的版本
st.write(f"**当前 google-generativeai 库版本:** `{genai.__version__}`")
st.info("如果版本低于 0.5.0，绝对无法使用 1.5-flash 模型。")

# 2. 检查 API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ 后台没有检测到 API Key，请去 Settings -> Secrets 检查。")
else:
    st.success(f"✅ 检测到 API Key (末尾四位): ...{api_key[-4:]}")
    
    # 3. 尝试连接 Google 并列出模型
    genai.configure(api_key=api_key)
    
    st.write("---")
    st.write("### 正在向 Google 查询可用模型列表...")
    
    try:
        available_models = []
        # 列出所有支持生成内容的模型
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        if available_models:
            st.success("🎉 连接成功！你的 Key 是有效的。")
            st.write("你的账号可以使用以下模型：")
            st.code("\n".join(available_models))
            
            st.write("---")
            if "models/gemini-1.5-flash" in available_models:
                st.balloons()
                st.write("✅ **好消息：列表中包含 gemini-1.5-flash！** (说明之前是代码拼写或缓存问题)")
            else:
                st.warning("⚠️ **坏消息：列表中没有 Flash 模型。** 请尝试使用列表里存在的模型名字（比如 gemini-pro）修改代码。")
        else:
            st.warning("连接成功，但没有找到任何可用模型。")
            
    except Exception as e:
        st.error(f"❌ 连接失败，可能是 Key 无效或网络问题。报错信息：\n{e}")
