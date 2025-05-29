# main.py
import streamlit as st
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app
from app.realjob_application import realjob_application_app
from app.questions import (
    get_employment_questions,
    get_self_employment_questions,
    get_remote_assignment_questions,
    get_wage_delay_questions,
    get_daily_worker_eligibility_questions
)

# 페이지 설정을 가장 먼저 호출
st.set_page_config(page_title="실업급여 지원 시스템", page_icon="💼", layout="wide")

# Font Awesome CDN 로드 및 CSS 로드
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    """,
    unsafe_allow_html=True
)

with open("static/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
    # 사이드바 상태 초기화
    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = True

    # 커스텀 HTML 버튼을 사이드바 상단 오른쪽에 배치
    with st.sidebar:
        # 클릭 상태를 처리하기 위한 키
        if 'toggle_clicked' not in st.session_state:
            st.session_state.toggle_clicked = False

        # 버튼 텍스트와 아이콘 설정
        button_icon = "fa-chevron-right" if not st.session_state.sidebar_visible else "fa-chevron-left"
        button_text = "메뉴 열기" if not st.session_state.sidebar_visible else "메뉴 닫기"

        # 커스텀 HTML 버튼 생성 (Font Awesome 아이콘 사용)
        st.markdown(
            f"""
            <div class="sidebar-toggle-container">
                <button id="sidebar-toggle" onclick="streamlitCallback('toggle_clicked', true)">
                    <i class="fas {button_icon} toggle-icon"></i>
                    <span class="toggle-text">{button_text}</span>
                </button>
            </div>
            <script>
                function streamlitCallback(key, value) {{
                    window.parent.postMessage({{
                        type: "streamlit:setComponentValue",
                        key: key,
                        value: value
                    }}, "*");
                }}
            </script>
            """,
            unsafe_allow_html=True
        )

        # 버튼 클릭 이벤트 처리
        if st.session_state.toggle_clicked:
            st.session_state.sidebar_visible = not st.session_state.sidebar_visible
            st.session_state.toggle_clicked = False  # 클릭 상태 초기화
            st.rerun()

    # CSS로 사이드바 표시/숨김 제어
    sidebar_display = "block" if st.session_state.sidebar_visible else "none"
    st.markdown(
        f"""
        <style>
        .css-1v0mbdj {{ /* 사이드바 클래스 */
            display: {sidebar_display} !important;
            transition: all 0.3s ease; /* 부드러운 전환 효과 */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("💼 실업급여 도우미")

    # 사이드바 내용 (토글 상태에 따라 표시)
    if st.session_state.sidebar_visible:
        with st.sidebar:
            st.markdown("### 🔍 검색")
            search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")

            # Menu and question definitions
            menus = {
                "수급자격": ["임금 체불 판단", "원거리 발령 판단"],
                "실업인정": ["실업인정", "실업인정 신청"],
                "취업촉진수당": ["조기재취업수당"],
                "실업급여 신청가능 시점": ["실업급여 신청 가능 시점", "일용직(건설일용포함)"]
            }
            all_questions = {
                "임금 체불 판단": get_wage_delay_questions(),
                "원거리 발령 판단": get_remote_assignment_questions(),
                "실업인정": [],
                "실업인정 신청": [],
                "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
                "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
            }

            # Filter menus based on search query
            filtered_menus = {}
            if search_query:
                search_query = search_query.lower()
                for main_menu, sub_menus in menus.items():
                    filtered_sub_menus = [
                        sub for sub in sub_menus
                        if search_query in sub.lower() or
                        any(search_query in q.lower() for q in all_questions.get(sub, []))
                    ]
                    if filtered_sub_menus or search_query in main_menu.lower():
                        filtered_menus[main_menu] = filtered_sub_menus
            else:
                filtered_menus = menus

            # Main menu selection with default value
            menu = st.selectbox(
                "📌 메뉴를 선택하세요",
                list(filtered_menus.keys()),
                key="main_menu",
                index=0 if filtered_menus else None
            )

            # Sub menu selection with default value
            sub_menu = None
            if menu and filtered_menus.get(menu):
                sub_menu = st.radio(
                    "📋 하위 메뉴",
                    filtered_menus[menu],
                    key="sub_menu",
                    index=0
                )
            elif not filtered_menus:
                st.warning("검색 결과에 해당하는 메뉴가 없습니다.")

    st.markdown("---")

    # Call functions based on menu selection with sidebar adjustment
    if menu and sub_menu:
        if menu == "수급자격":
            if sub_menu == "임금 체불 판단":
                wage_delay_app()
            elif sub_menu == "원거리 발령 판단":
                remote_assignment_app()
        elif menu == "실업인정":
            if sub_menu == "실업인정":
                unemployment_recognition_app()
            elif sub_menu == "실업인정 신청":
                st.sidebar.empty()  # "실업인정 신청" 시 사이드바 비우기
                realjob_application_app()
        elif menu == "취업촉진수당":
            if sub_menu == "조기재취업수당":
                early_reemployment_app()
        elif menu == "실업급여 신청가능 시점":
            if sub_menu == "실업급여 신청 가능 시점":
                st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 자세한 내용은 고용센터에 문의하세요.")
            elif sub_menu == "일용직(건설일용포함)":
                daily_worker_eligibility_app()
    else:
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")

    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
