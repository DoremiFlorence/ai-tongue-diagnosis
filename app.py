"""python3 -m streamlit run app.py"""
"""中医舌诊 AI 诊断平台 - Streamlit 主应用。"""

import streamlit as st

from config.settings import SILICONFLOW_API_KEY
from core.tongue_analyzer import TongueAnalyzer
from core.diagnosis_engine import DiagnosisEngine
from core.report_generator import generate_diagnosis_report
from utils.image_utils import image_to_base64, validate_image
from utils.session_manager import (
    generate_session_id,
    save_session,
    load_session,
    list_sessions,
)
from models.schemas import SessionSchema

st.set_page_config(
    page_title="中医舌诊 AI 诊断平台",
    page_icon="👅",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #8B4513;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .analysis-box {
        background-color: #FFF8DC;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #8B4513;
    }
    .chat-user {
        background-color: #E3F2FD;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .chat-assistant {
        background-color: #FFF3E0;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态。"""
    if "session" not in st.session_state:
        st.session_state.session = None
    if "analyzer" not in st.session_state:
        st.session_state.analyzer = None
    if "engine" not in st.session_state:
        st.session_state.engine = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "image_analyzed" not in st.session_state:
        st.session_state.image_analyzed = False
    if "page" not in st.session_state:
        st.session_state.page = "main"
    if "api_key" not in st.session_state:
        st.session_state.api_key = SILICONFLOW_API_KEY or ""
    if "api_initialized" not in st.session_state:
        st.session_state.api_initialized = False


def get_api_key() -> str:
    """获取 API Key，优先从环境变量读取。"""
    return st.session_state.get("api_key", "") or SILICONFLOW_API_KEY or ""


def setup_api():
    """设置 API 客户端。"""
    api_key = get_api_key()
    if api_key and not st.session_state.api_initialized:
        try:
            st.session_state.analyzer = TongueAnalyzer(api_key)
            st.session_state.engine = DiagnosisEngine(api_key)
            st.session_state.api_initialized = True
            return True
        except Exception as e:
            st.error(f"API 初始化失败: {e}")
            return False
    return st.session_state.api_initialized


def main_page():
    """主诊断页面。"""
    st.markdown('<p class="main-header">🏥 中医舌诊 AI 诊断平台</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于人工智能的中医舌诊分析系统</p>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ 设置")

        env_api_configured = bool(SILICONFLOW_API_KEY)

        if env_api_configured:
            st.success("✅ API Key 已从环境变量加载")
            setup_api()
        else:
            api_key = st.text_input(
                "SiliconFlow API Key",
                type="password",
                value=st.session_state.api_key,
                help="请输入您的 SiliconFlow API Key，或在 .env 文件中配置",
            )
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                st.session_state.api_initialized = False

            if api_key:
                if setup_api():
                    st.success("✅ API 已连接")
                else:
                    st.error("❌ API 连接失败")

        st.divider()

        if st.button("📋 查看历史记录", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

        if st.button("🔄 开始新诊断", use_container_width=True):
            st.session_state.session = None
            st.session_state.messages = []
            st.session_state.image_analyzed = False
            st.rerun()

    if not st.session_state.get("api_key"):
        st.info("👈 请先在侧边栏输入您的 SiliconFlow API Key")
        st.markdown("""
        ### 使用说明
        1. 在侧边栏输入您的 SiliconFlow API Key
        2. 上传一张清晰的舌苔照片
        3. 系统将自动进行舌诊分析
        4. 您可以继续与 AI 进行问诊对话
        5. 生成并下载诊断报告
        """)
        return

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📷 上传舌苔图片")
        uploaded_file = st.file_uploader(
            "选择舌苔图片",
            type=["jpg", "jpeg", "png", "webp"],
            help="请上传清晰的舌苔正面照片",
        )

        if uploaded_file and not st.session_state.image_analyzed:
            image_bytes = uploaded_file.read()

            if not validate_image(image_bytes):
                st.error("图片格式无效，请重新上传")
                return

            st.image(image_bytes, caption="已上传的舌苔图片", use_container_width=True)

            if st.button("🔍 开始分析", type="primary", use_container_width=True):
                with st.spinner("正在分析舌苔图片，请稍候..."):
                    try:
                        image_base64 = image_to_base64(image_bytes)
                        analysis = st.session_state.analyzer.analyze_tongue_image(image_base64)

                        session = SessionSchema(
                            session_id=generate_session_id(),
                            initial_analysis=analysis,
                            conversation_history=[],
                        )
                        st.session_state.session = session
                        st.session_state.image_analyzed = True
                        st.session_state.messages = [
                            {"role": "assistant", "content": analysis}
                        ]
                        save_session(session)
                        st.rerun()

                    except Exception as e:
                        st.error(f"分析失败: {e}")

        elif st.session_state.image_analyzed and uploaded_file:
            st.image(uploaded_file, caption="已分析的舌苔图片", use_container_width=True)

    with col2:
        st.subheader("💬 诊断对话")

        if st.session_state.image_analyzed:
            chat_container = st.container(height=400)

            with chat_container:
                for msg in st.session_state.messages:
                    role = msg["role"]
                    content = msg["content"]
                    if role == "user":
                        st.markdown(f'<div class="chat-user">🧑 <b>您:</b><br>{content}</div>',
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="chat-assistant">👨‍⚕️ <b>中医专家:</b><br>{content}</div>',
                                    unsafe_allow_html=True)

            user_input = st.chat_input("请输入您的问题或症状描述...")

            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})

                with st.spinner("思考中..."):
                    try:
                        history = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[1:-1]
                        ]
                        response = st.session_state.engine.continue_conversation(
                            user_input,
                            history,
                            st.session_state.session.initial_analysis,
                        )
                        st.session_state.messages.append({"role": "assistant", "content": response})

                        st.session_state.session.conversation_history = [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages[1:]
                        ]
                        save_session(st.session_state.session)
                        st.rerun()

                    except Exception as e:
                        st.error(f"对话失败: {e}")

            st.divider()

            col_a, col_b = st.columns(2)

            with col_a:
                if st.button("📊 生成诊断报告", use_container_width=True):
                    with st.spinner("正在生成报告..."):
                        try:
                            history = [
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.messages[1:]
                            ]
                            final_diagnosis = st.session_state.engine.generate_final_diagnosis(
                                history,
                                st.session_state.session.initial_analysis,
                            )
                            st.session_state.session.final_diagnosis = final_diagnosis
                            st.session_state.session.recommendations = final_diagnosis
                            save_session(st.session_state.session)
                            st.rerun()

                        except Exception as e:
                            st.error(f"生成报告失败: {e}")

            with col_b:
                if st.session_state.session and st.session_state.session.final_diagnosis:
                    try:
                        pdf_bytes = generate_diagnosis_report(
                            st.session_state.session.initial_analysis,
                            st.session_state.session.final_diagnosis,
                        )
                        st.download_button(
                            "📥 下载 PDF 报告",
                            data=pdf_bytes,
                            file_name=f"tongue_diagnosis_{st.session_state.session.session_id}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.warning(f"PDF 生成失败: {e}")

        else:
            st.info("👈 请先上传舌苔图片并点击分析")

    # 诊断报告单独展示区域
    if st.session_state.session and st.session_state.session.final_diagnosis:
        st.divider()
        st.subheader("📋 诊断报告")
        st.markdown(
            f'<div class="analysis-box">{st.session_state.session.final_diagnosis}</div>',
            unsafe_allow_html=True,
        )


def history_page():
    """历史记录页面。"""
    st.markdown('<p class="main-header">📋 诊断历史记录</p>', unsafe_allow_html=True)

    if st.button("← 返回主页", use_container_width=False):
        st.session_state.page = "main"
        st.rerun()

    st.divider()

    sessions = list_sessions()

    if not sessions:
        st.info("暂无历史记录")
        return

    for s in sessions:
        with st.expander(f"📅 {s['created_at'][:19]} - {'✅ 已完成' if s['has_diagnosis'] else '⏳ 进行中'}"):
            if st.button(f"查看详情", key=f"view_{s['session_id']}"):
                session = load_session(s["session_id"])
                if session:
                    st.markdown("**初始分析:**")
                    st.write(session.initial_analysis)

                    if session.final_diagnosis:
                        st.markdown("**最终诊断:**")
                        st.write(session.final_diagnosis)


def main():
    """主函数。"""
    init_session_state()

    if st.session_state.page == "history":
        history_page()
    else:
        main_page()


if __name__ == "__main__":
    main()
