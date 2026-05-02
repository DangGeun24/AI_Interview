import streamlit as st
import uuid
from datetime import datetime, timedelta

st.set_page_config(page_title="AI 압박 면접관", layout="wide")

st.markdown("""
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
    <style>
        html, body, [class*="css"]  {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Apple Color Emoji", "Segoe UI Emoji" !important;
        }
        .sidebar-title { color: #020617 !important; font-weight: 800; font-size: 1.5rem; margin-bottom: 20px; }
        div[data-testid="stVerticalBlockBorderControl"] { border: none !important; background-color: transparent !important; margin-bottom: -15px !important; }
        div[data-testid="stSidebar"] .stButton > button { background-color: transparent !important; border: none !important; text-align: left !important; color: #1E293B !important; font-weight: 500; }
        div[data-testid="stSidebar"] .stButton > button:hover { background-color: #E2E8F0 !important; }
        div[data-testid="stSidebar"] .stButton > button[kind="primary"] { background-color: #0F172A !important; color: white !important; height: 48px !important; font-weight: 600; border-radius: 8px !important; }
        button[data-testid="sidebar-close-button"], div[data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}
    st.session_state["current_session"] = None
    st.session_state["trash_bin"] = {} 

@st.dialog("기록 삭제")
def delete_confirm_dialog(session_id):
    st.write("🛑 해당 면접 세션을 삭제하시겠습니까?")
    st.caption("삭제된 기록은 휴지통에 보관되며 2일 뒤 영구 삭제됩니다.")
    c1, c2 = st.columns(2)
    if c1.button("삭제 승인", use_container_width=True, type="primary"):

        chat_data = st.session_state["chat_sessions"].pop(session_id)
        chat_data["deleted_at"] = datetime.now()
        st.session_state["trash_bin"][session_id] = chat_data
        
        st.session_state["current_session"] = None
        st.rerun()
    if c2.button("취소", use_container_width=True):
        st.rerun()

with st.sidebar:
    st.markdown('<div class="sidebar-title">📑 AI 면접 컨설턴트</div>', unsafe_allow_html=True)
    
    if st.button("➕ 새로운 대화 시작", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state["chat_sessions"][new_id] = {
            "title": "새 대화", 
            "messages": [],
            "status": "chatting",
            "mode": None
        }
        st.session_state["current_session"] = new_id
        st.rerun()

    now = datetime.now()

    expired = [k for k, v in st.session_state["trash_bin"].items() if now - v["deleted_at"] > timedelta(days=2)]
    for k in expired: del st.session_state["trash_bin"][k]

    if st.session_state["trash_bin"]:
        with st.expander("🗑️ 휴지통 (2일 보관)"):
            for tid, tdata in list(st.session_state["trash_bin"].items()):
                col_t1, col_t2 = st.columns([8, 2])
                col_t1.caption(f"{tdata['title']}")
                if col_t2.button("🔙", key=f"res_{tid}", help="복구"):
                    st.session_state["chat_sessions"][tid] = tdata
                    del st.session_state["trash_bin"][tid]
                    st.rerun()

    st.divider()
    st.caption("📋 진행 중인 대화")
    
    for sid, sinfo in list(st.session_state["chat_sessions"].items()):
        if not sinfo["messages"] and sid != st.session_state["current_session"]: continue
        is_active = (sid == st.session_state["current_session"])
        
        col_t, col_i = st.columns([8.5, 1.5])
        with col_t:
            prefix = "⏺️ " if is_active else "⚪ "
            if st.button(f"{prefix}{sinfo['title']}", key=f"btn_{sid}", use_container_width=True):
                st.session_state["current_session"] = sid
                st.rerun()
        with col_i:

            with st.popover("⚙️"):
                st.caption("세션 설정")

                new_title = st.text_input("제목 변경", value=sinfo["title"], key=f"in_{sid}")
                if st.button("저장", key=f"sv_{sid}", use_container_width=True):
                    st.session_state["chat_sessions"][sid]["title"] = new_title
                    st.rerun()
                st.divider()
                if st.button("삭제", key=f"dl_{sid}", type="primary", use_container_width=True):
                    delete_confirm_dialog(sid)

if st.session_state["current_session"]:
    current_chat = st.session_state["chat_sessions"][st.session_state["current_session"]]
    st.title("⚖️ 실전 압박 면접실")

    for i, msg in enumerate(current_chat["messages"]):
        avatar = "👤" if msg["role"] == "user" else "🧑‍💼"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg.get("show_download"):
                st.download_button(
                    label="📥 수정된 이력서 다운로드",
                    data="수정된 이력서의 가상 내용입니다.", 
                    file_name="수정본_이력서.txt",
                    key=f"dl_btn_{i}"
                )

    status = current_chat.get("status")

    if status == "choosing":
        st.write("---")
        c1, c2 = st.columns(2)
        if c1.button("📝 이력서 첨삭 받기", use_container_width=True):
            current_chat["status"] = "correction"
            current_chat["messages"].append({"role": "assistant", "content": "첨삭 모드입니다. 수정하고 싶은 부분을 말씀해 주시면 즉시 반영하겠습니다."})
            st.rerun()
        if c2.button("🎤 바로 모의 면접 시작", use_container_width=True):
            current_chat["status"] = "mode_select"
            st.rerun()

    elif status == "correction":
        if st.button("🎤 첨삭 완료! 이제 면접 보기", use_container_width=True):
            current_chat["status"] = "mode_select"
            st.rerun()

    elif status == "mode_select":
        st.info("면접 성향을 선택하십시오.")
        m1, m2 = st.columns(2)
        if m1.button("😊 일반 면접", use_container_width=True):
            current_chat["status"], current_chat["mode"] = "interview", "normal"
            current_chat["messages"].append({"role": "assistant", "content": "일반 면접을 시작합니다. 긴장을 풀고 답변하십시오."})
            st.rerun()
        if m2.button("🔥 압박 면접", use_container_width=True):
            current_chat["status"], current_chat["mode"] = "interview", "pressure"
            current_chat["messages"].append({"role": "assistant", "content": "실전 압박 면접을 시작합니다. 귀하의 역량을 증명하십시오."})
            st.rerun()

    elif status == "interview":
        if st.button("🛑 면접 종료", use_container_width=True):
            current_chat["status"] = "choosing"
            current_chat["messages"].append({"role": "assistant", "content": "면접을 종료합니다. 추가 작업을 선택하십시오."})
            st.rerun()

    if status != "mode_select":
        if prompt := st.chat_input("메시지를 입력하거나 서류를 제출하십시오.", accept_file=True, file_type=['pdf', 'txt']):
            if prompt["files"]:
                file_name = prompt["files"][0].name
                current_chat["messages"].append({"role": "user", "content": f"📄 **이력서 제출:** {file_name}"})
                current_chat["messages"].append({"role": "assistant", "content": f"제출하신 **{file_name}**을 분석했습니다. 무엇을 도와드릴까요?"})
                current_chat["status"] = "choosing"
                current_chat["title"] = f"分析: {file_name}"
                st.rerun()
            elif prompt.text:
                current_chat["messages"].append({"role": "user", "content": prompt.text})
                if status == "correction" and ("다운" in prompt.text or "파일" in prompt.text):
                    current_chat["messages"].append({
                        "role": "assistant", 
                        "content": "요청하신 대로 내용을 수정하여 파일을 생성했습니다. 아래 버튼을 클릭하십시오.",
                        "show_download": True
                    })
                else:
                    res = "진행 중인 단계에 맞춰 답변해 드리겠습니다."
                    if status == "interview": res = "답변 감사합니다. 다음 질문입니다."
                    elif status == "correction": res = "어떤 부분을 더 고쳐드릴까요?"
                    current_chat["messages"].append({"role": "assistant", "content": res})
                st.rerun()
else:
    st.info("왼쪽 사이드바에서 새로운 대화를 시작하십시오.")