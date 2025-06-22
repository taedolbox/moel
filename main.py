# main.py

import streamlit as st
from urllib.parse import urlencode, parse_qs # URL 파싱을 위한 모듈 추가

from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app
from app.questions import (
    get_employment_questions,
    get_self_employment_questions,
    get_remote_assignment_questions,
    get_wage_delay_questions,
    get_daily_worker_eligibility_questions
)

def main():
    st.set_page_config(page_title="실업급여 지원 시스템", page_icon="💼", layout="centered")

    # Apply custom CSS
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    st.title("💼 실업급여 도우미")

    # --- URL 쿼리 파라미터에서 현재 메뉴 상태 가져오기 ---
    query_params = st.query_params
    initial_selection = query_params.get('menu', [None])[0] # 'menu' 파라미터 값 가져오기

    if 'current_selected_sub_menu' not in st.session_state:
        st.session_state.current_selected_sub_menu = initial_selection

    # 만약 URL 파라미터가 있고, 현재 세션 상태와 다르면 세션 상태 업데이트
    if initial_selection and st.session_state.current_selected_sub_menu != initial_selection:
        st.session_state.current_selected_sub_menu = initial_selection

    # Sidebar search functionality
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")

        # Menu and question definitions
        menus = {
            "수급자격": ["임금 체불 판단", "원거리 발령 판단"],
            "실업인정": ["실업인정"],
            "취업촉진수당": ["조기재취업수당"],
            "실업급여 신청가능 시점": ["실업급여 신청 가능 시점", "일용직(건설일용포함)"]
        }
        all_questions = {
            "임금 체불 판단": get_wage_delay_questions(),
            "원거리 발령 판단": get_remote_assignment_questions(),
            "실업인정": [],
            "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
            "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
        }

        # Filter menus based on search query
        filtered_menus = {}
        if search_query:
            search_query = search_query.lower()
            for main_menu, sub_menus in menus.items():
                filtered_sub_menus = []
                for sub in sub_menus:
                    if search_query in sub.lower() or any(search_query in q.lower() for q in all_questions.get(sub, [])):
                        filtered_sub_menus.append(sub)
                if filtered_sub_menus or search_query in main_menu.lower():
                    filtered_menus[main_menu] = filtered_sub_menus
        else:
            filtered_menus = menus

        # Display all main menus and their sub-menus directly
        st.markdown("### 📌 메뉴 선택")

        for main_menu, sub_menus in filtered_menus.items():
            if sub_menus:
                st.markdown(f"#### {main_menu}")
                for sub_menu_item in sub_menus:
                    # 버튼 클릭 시 session_state 업데이트 및 URL 파라미터 변경
                    is_selected = st.session_state.current_selected_sub_menu == sub_menu_item
                    button_label = f"**{sub_menu_item}**" if is_selected else sub_menu_item # 선택된 버튼 강조
                    
                    if st.button(button_label, key=f"btn_{main_menu}_{sub_menu_item}"):
                        st.session_state.current_selected_sub_menu = sub_menu_item
                        # URL 파라미터 업데이트 (한글 인코딩 처리)
                        st.query_params['menu'] = sub_menu_item
                        st.experimental_rerun() # URL 변경 적용을 위해 재실행
            elif search_query and search_query in main_menu.lower():
                if st.button(main_menu, key=f"btn_only_{main_menu}"):
                    st.session_state.current_selected_sub_menu = None
                    # URL 파라미터에서 'menu' 제거
                    if 'menu' in st.query_params:
                        del st.query_params['menu']
                    st.experimental_rerun()

    st.markdown("---")

    # Use the value from session state to determine which app to show
    current_selection = st.session_state.current_selected_sub_menu

    # Call functions based on the current selection
    if current_selection == "임금 체불 판단":
        wage_delay_app()
    elif current_selection == "원거리 발령 판단":
        remote_assignment_app()
    elif current_selection == "실업인정":
        unemployment_recognition_app()
    elif current_selection == "조기재취업수당":
        early_reemployment_app()
    elif current_selection == "실업급여 신청 가능 시점":
        st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 자세한 내용은 고용센터에 문의하세요.")
    elif current_selection == "일용직(건설일용포함)":
        daily_worker_eligibility_app()
    else:
        # Only show this message if nothing is selected initially or if selection is cleared
        if not st.session_state.current_selected_sub_menu and not search_query:
            st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")

    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
