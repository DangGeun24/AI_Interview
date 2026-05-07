import streamlit as st
import uuid
from datetime import datetime, timedelta

# 기본 페이지 세팅
st.set_page_config(page_title="AI 면접관 & 이력서 첨삭", layout="wide", page_icon="")

# UI 스타일링 및 테마 설정
st.markdown('''
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@200..900&display=swap');

/* 다크 그린 테마 변수 */
:root {
    --bg-color: #252620;
    --sidebar-bg: #3C3D37;
    --accent-color: #697565;
    --text-color: #FFFFFF;
    --font-stack: 'Noto Serif KR', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
}

/* 전체 폰트 및 배경색 강제 적용 */
footer { display: none !important; }
h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown p, .stMarkdown div, .stButton button {
    font-family: var(--font-stack) !important;
}

.stApp, header, .stHeader, [data-testid="stHeader"], [data-testid="stAppViewContainer"] {
    background-color: var(--bg-color) !important;
}

/* 시스템 아이콘은 폰트 깨지지 않게 보호 */
[data-testid="stIcon"], .stIcon, .material-icons, svg, i, span:has(svg), [class^="st-ae"], [class^="st-af"] {
    font-family: inherit !important;
    font-feature-settings: normal !important;
}

/* 탭 하이라이트 & 라디오 버튼 색상 커스텀 */
[data-baseweb="tab-highlight"] { background-color: var(--accent-color) !important; }
[data-testid="stRadioButton"] div[role="radiogroup"] div[aria-checked="true"] > div {
    background-color: var(--accent-color) !important;
}

/* 입력창 포커스 효과 */
div[data-baseweb="input"] > div { border-color: rgba(255, 255, 255, 0.2) !important; }
div[data-baseweb="input"] > div:focus-within {
    border-color: var(--accent-color) !important;
    box-shadow: 0 0 0 1px var(--accent-color) !important;
}

/* 텍스트 가독성 향상 */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp p, .stApp li, .stMarkdown, .stMarkdown div {
    color: var(--text-color) !important;
    -webkit-font-smoothing: antialiased;
}

/* 왼쪽 사이드바 스타일링 */
[data-testid="stSidebar"] { background-color: var(--sidebar-bg) !important; }
[data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: var(--text-color) !important;
}

/* 버튼 디자인 통일 */
.stButton > button, div[data-testid="stFormSubmitButton"] > button {
    background-color: var(--accent-color) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    width: 100% !important;
}
[data-testid="stSidebar"] div[data-testid="stPopover"] > div > button {
    background-color: var(--accent-color) !important;
    color: #FFFFFF !important;
    border-radius: 10px !important;
    height: 38px !important;
    justify-content: center !important;
}

/* 알림/성공 박스 라운딩 */
div[data-testid="stNotification"] {
    background-color: var(--sidebar-bg) !important;
    color: var(--text-color) !important;
    border-radius: 15px !important;
}
</style>
''', unsafe_allow_html=True)

# 세션 상태 관리 (State Init)
if "users" not in st.session_state: st.session_state["users"] = {"test": "1234"}
if "current_user" not in st.session_state: st.session_state["current_user"] = None
if "is_logged_in" not in st.session_state: st.session_state["is_logged_in"] = False
if "page" not in st.session_state: st.session_state["page"] = "home"
if "sessions" not in st.session_state: st.session_state["sessions"] = {}
if "current_session_id" not in st.session_state: st.session_state["current_session_id"] = None

# 세션 관리 관련 유틸 함수들
def create_session(title="새로운 대화", initial_type="resume"):
    session_id = str(uuid.uuid4())
    st.session_state["sessions"][session_id] = {
        "id": session_id,
        "title": title,
        "active_mode": initial_type,
        "status": "active",
        "deleted_at": None,
        "resume_data": None,
        "resume_messages": [],
        "interview_messages": [],
        "interview_style": "일반 면접",
        "created_at": datetime.now().isoformat()
    }
    return session_id

def delete_session(session_id):
    st.session_state["sessions"][session_id]["status"] = "trashed"
    st.session_state["sessions"][session_id]["deleted_at"] = datetime.now().isoformat()
    if st.session_state["current_session_id"] == session_id:
        st.session_state["current_session_id"] = None; st.session_state["page"] = "home"

def restore_session(session_id):
    st.session_state["sessions"][session_id]["status"] = "active"
    st.session_state["sessions"][session_id]["deleted_at"] = None

def hard_delete_session(session_id):
    if session_id in st.session_state["sessions"]: del st.session_state["sessions"][session_id]

def go_to_page(page_name, session_id=None):
    st.session_state["page"] = page_name
    if session_id: st.session_state["current_session_id"] = session_id
    elif page_name == "home": st.session_state["current_session_id"] = None

def save_title(session_id):
    new_title = st.session_state[f"title_input_{session_id}"]
    if new_title.strip(): st.session_state["sessions"][session_id]["title"] = new_title
    st.session_state[f"editing_{session_id}"] = False

# 삭제 컨펌 모달
@st.dialog("⚠️ 대화 삭제")
def delete_confirmation_dialog(session_id):
    st.write("정말 삭제하시겠습니까?")
    c1, c2 = st.columns(2)
    if c1.button("확인", type="primary"): delete_session(session_id); st.rerun()
    if c2.button("취소"): st.rerun()

# 사이드바 레이아웃
with st.sidebar:
    st.title("AI Interviewer")
    if not st.session_state["is_logged_in"]:
        st.warning("로그인이 필요합니다.")
    else:
        st.subheader("Menu")
        if st.button("🏠 홈", use_container_width=True): go_to_page("home"); st.rerun()
        st.markdown("---")
        
        with st.expander("🗑️ 휴지통 (2일 보관)"):
            trashed = [s for s in st.session_state["sessions"].values() if s["status"] == "trashed"]
            for ts in trashed:
                st.write(f"📄 {ts['title']}")
                c1, c2 = st.columns(2)
                if c1.button("복구", key=f"res_{ts['id']}"): restore_session(ts['id']); st.rerun()
                if c2.button("영구삭제", key=f"hdel_{ts['id']}"): hard_delete_session(ts['id']); st.rerun()

        # 대화 리스트 뿌려주기
        st.subheader("진행 중인 대화")
        active = [s for s in st.session_state["sessions"].values() if s["status"] == "active"]
        active.sort(key=lambda x: x["created_at"], reverse=True)
        for s in active:
            mode = s.get("active_mode", "resume")
            icon = "💬" if mode == "interview" else "📝"
            label = f"{icon} {s['title']}"
            if s["id"] == st.session_state.get("current_session_id"): label = f"🔥 {s['title']} (현재)"
            
            if st.session_state.get(f"editing_{s['id']}", False):
                st.text_input("수정", value=s["title"], key=f"title_input_{s['id']}", on_change=save_title, args=(s["id"],), label_visibility="collapsed")
            else:
                c1, c2 = st.columns([0.8, 0.2])
                if c1.button(label, key=f"open_{s['id']}", use_container_width=True):
                    go_to_page("session_view", s["id"]); st.rerun()
                with c2.popover("\u200B"):
                    if st.button("✏️ 수정", key=f"ed_{s['id']}"): st.session_state[f"editing_{s['id']}"] = True; st.rerun()
                    if st.button("🗑️ 삭제", key=f"dl_{s['id']}"): delete_confirmation_dialog(s["id"])

        st.markdown("---")
        st.write(f"✅ {st.session_state['current_user']}님")
        if st.button("로그아웃"): st.session_state["is_logged_in"] = False; st.session_state["current_user"] = None; st.rerun()

# 메인 뷰 로직
if not st.session_state["is_logged_in"]:
    st.title("AI 면접관 & 이력서 첨삭")
    st.markdown("서비스를 이용하시려면 로그인해주세요.")
    col_login, _ = st.columns([1, 1])
    with col_login:
        t1, t2 = st.tabs(["로그인", "회원가입"])
        with t1:
            with st.form("l_form"):
                l_id = st.text_input("아이디")
                l_pw = st.text_input("비밀번호", type="password")
                if st.form_submit_button("로그인", use_container_width=True, type="primary"):
                    if l_id in st.session_state["users"] and st.session_state["users"][l_id] == l_pw:
                        st.session_state["is_logged_in"] = True; st.session_state["current_user"] = l_id; st.rerun()
                    else: st.error("아이디나 비밀번호가 틀렸어요.")
        with t2:
            with st.form("r_form"):
                r_id = st.text_input("새 아이디")
                r_pw = st.text_input("새 비밀번호", type="password")
                if st.form_submit_button("회원가입", use_container_width=True):
                    st.session_state["users"][r_id] = r_pw; st.success("가입 완료! 로그인을 해주세요."); st.rerun()

else:
    # 로그인 완료 후 화면
    page = st.session_state["page"]
    
    # 명령어 내비게이션 처리
    def process_command(p):
        if "면접보기" in p.replace(" ", ""):
            new_id = create_session(f"AI모의면접_{datetime.now().strftime('%H%M')}", "interview")
            go_to_page("session_view", new_id); return True
        return False

    if page == "home":
        # 대시보드 성격의 홈 화면
        st.title(f"환영합니다, {st.session_state['current_user']}님! 👋")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("#### 💬 AI 모의 면접\n실전 같은 면접 경험을 제공합니다.")
            if st.button("새 AI 모의 면접 시작", type="primary"):
                go_to_page("session_view", create_session(f"AI모의면접_{datetime.now().strftime('%H%M')}", "interview")); st.rerun()
        with c2:
            st.success("#### 📝 이력서 첨삭\nAI와 대화하며 이력서를 완성해보세요.")
            if st.button("새 첨삭 시작"):
                go_to_page("session_view", create_session(f"첨삭_{datetime.now().strftime('%H%M')}", "resume")); st.rerun()

    elif page == "session_view":
        # 개별 세션 (첨삭/면접) 뷰
        curr = st.session_state["sessions"].get(st.session_state["current_session_id"])
        if not curr: st.warning("세션을 찾을 수 없어요."); go_to_page("home"); st.rerun()
        
        # 상단 탭으로 모드 전환
        st.write("")
        m1, m2, _ = st.columns([0.2, 0.2, 0.6])
        current_mode = curr.get("active_mode", "resume")
        if m1.button("📝 이력서 첨삭", use_container_width=True, type="secondary" if current_mode == "interview" else "primary"):
            curr["active_mode"] = "resume"; st.rerun()
        if m2.button("💬 AI 모의 면접", use_container_width=True, type="secondary" if current_mode == "resume" else "primary"):
            curr["active_mode"] = "interview"; st.rerun()
        
        st.markdown("---")

        if curr.get("active_mode", "resume") == "resume":
            # 이력서 채팅 모드
            st.title("📝 이력서 첨삭")
            st.info("""
            💡 이력서 첨삭 이용 가이드
            1. 고민되는 경험이나 문구를 채팅창에 편하게 말씀해 주세요.
            2. AI의 질문에 답변한 후 '이력서 수정해줘'라고 입력하면 최종 수정안을 제시해 드립니다.
            3. 첨삭이 완료되면 상단 'AI 모의 면접' 버튼 클릭 혹은 '면접 시작'을 입력하여 즉시 면접을 볼 수 있습니다!
            """)
            
            if not curr.get("resume_messages"):
                curr["resume_messages"] = [{"role": "assistant", "content": "안녕하세요! 어떤 경험을 이력서에 녹여내고 싶으신가요? 고민되는 부분을 말씀해 주시면 함께 수정안을 만들어 볼게요."}]
            
            for m in curr.get("resume_messages", []):
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("고민 상담 또는 '이력서 수정해줘'라고 입력하세요", accept_file=True, file_type=['pdf', 'txt', 'docx']):
                if p.text and ("면접시작" in p.text.replace(" ", "") or "면접보자" in p.text.replace(" ", "")):
                    curr["active_mode"] = "interview"; st.rerun()
                
                if not process_command(p.text if p.text else ""):
                    user_content = ""
                    if p.files: user_content += f"📄 [파일 첨부: {p.files[0].name}]\n\n"
                    if p.text: user_content += p.text

                    curr.setdefault("resume_messages", []).append({"role": "user", "content": user_content})
                    with st.chat_message("user"): st.markdown(user_content)
                    with st.chat_message("assistant"):
                        with st.spinner("AI 컨설턴트가 생각 중..."):
                            if p.text and "수정" in p.text:
                                res = "말씀하신 내용을 반영하여 이력서 문구를 수정해 보았습니다.\n\n[수정안]\n'단순 기술 도입에 그치지 않고, MSA 환경에서 캐싱 전략을 최적화하여 응답 속도를 40% 개선하며 팀의 생산성을 높였습니다.'\n\n이 문구는 어떠신가요? 면접을 바로 보시려면 상단 'AI 모의 면접' 버튼을 클릭하거나 '면접 시작'이라고 말씀해 주세요!"
                                curr["resume_data"] = "MSA 환경에서 캐싱 전략을 최적화하여 응답 속도를 40% 개선"
                            elif p.text and ("역할" in p.text or "경험" in p.text):
                                res = "그 경험에서 본인이 맡았던 구체적인 역할은 무엇이었나요? 더 임팩트 있는 문구로 다듬어 드릴게요!"
                            else:
                                res = f"{p.text if p.text else '이력서'}에 대해 더 자세히 알고 싶습니다. 그 경험이 지원하시는 직무와 어떤 연관이 있다고 생각하시나요?"
                            st.markdown(res); curr.setdefault("resume_messages", []).append({"role": "assistant", "content": res})
                st.rerun()

        elif curr.get("active_mode", "resume") == "interview":
            # AI 모의 면접 모드
            st.title("💬 AI 모의 면접")
            col1, col2 = st.columns(2)
            with col1: ui = st.radio("📍 인터페이스", ["텍스트", "음성(준비중)"], horizontal=True)
            with col2:
                style = st.radio("🔥 스타일", ["일반 면접", "압박 면접"], 
                                 index=0 if curr.get("interview_style") == "일반 면접" else 1, horizontal=True)
                curr["interview_style"] = style
            
            if not curr.get("interview_messages"):
                curr["interview_messages"] = [{"role": "assistant", "content": f"안녕하세요! AI 모의 면접을 시작합니다. {style} 모드로 진행하겠습니다. 준비되셨다면 자기소개부터 부탁드립니다."}]

            for m in curr.get("interview_messages", []):
                with st.chat_message(m["role"]): st.markdown(m["content"])
            
            if p := st.chat_input("면접 답변을 입력하세요", accept_file=True, file_type=['pdf', 'txt', 'docx']):
                if not process_command(p.text if p.text else ""):
                    user_content = ""
                    if p.files: user_content += f"📄 [파일 첨부: {p.files[0].name}]\n\n"
                    if p.text: user_content += p.text

                    curr.setdefault("interview_messages", []).append({"role": "user", "content": user_content})
                    with st.chat_message("user"): st.markdown(user_content)
                    with st.chat_message("assistant"):
                        with st.spinner(f"AI 면접관이 {style} 질문을 생성 중입니다..."):
                            resume_info = curr.get("resume_data", "")
                            if style == "압박 면접":
                                if resume_info:
                                    res = f"이력서에서 언급하신 {resume_info} 이 성과는 사실 본인만의 노력이라기보다 팀 시스템의 덕이 아닐까요? 구체적으로 어떤 기술적 결정을 본인이 직접 내렸는지 증명해 보세요."
                                else:
                                    res = "방금 답변하신 내용은 다소 뻔한 대답이네요. 만약 상황이 훨씬 더 나빴다면 본인은 어떤 책임을 졌을 것 같습니까?"
                            else: # 일반 면접
                                if resume_info:
                                    res = f"첨삭된 이력서의 {resume_info} 성과가 매우 인상적입니다! 백엔드 개발자로서 이 성과를 내기 위해 가장 고심했던 설계적 포인트는 무엇인가요?"
                                else:
                                    res = f"{p.text if p.text else '본인의 경험'}이 향후 우리 회사에서 어떻게 쓰일 수 있을까요? 본인의 강점을 섞어서 편하게 말씀해 주세요."
                            st.markdown(res); curr.setdefault("interview_messages", []).append({"role": "assistant", "content": res})
                st.rerun()
