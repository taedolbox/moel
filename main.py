# main.py

import streamlit as st
from urllib.parse import urlencode, parse_qs

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
    initial_selection = query_params.get('menu', [None])[0]

    if 'current_selected_sub_menu' not in st.session_state:
        st.session_state.current_selected_sub_menu = initial_selection

    # 만약 URL 파라미터가 있고, 현재 세션 상태와 다르면 세션 상태 업데이트
    if initial_selection and st.session_state.current_selected_sub_menu != initial_selection:
        st.session_state.current_selected_sub_menu = initial_selection
        # URL 변경에 따른 재실행은 버튼 클릭 시에만 하므로 여기서는 불필요

    # Sidebar search functionality
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")
        # 검색어는 소문자로 변환하여 비교 준비
        processed_search_query = search_query.lower() if search_query else ""

        # Menu and question definitions (전체 메뉴를 정의)
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

        # Display all main menus and their sub-menus directly
        st.markdown("### 📌 메뉴 선택")

        for main_menu, sub_menus in menus.items(): # 필터링하지 않은 전체 menus 사용
            st.markdown(f"#### {main_menu}")
            
            # 메인 메뉴가 검색어와 일치하는지 확인
            main_menu_matched_by_search = processed_search_query in main_menu.lower()

            for sub_menu_item in sub_menus:
                # 하위 메뉴가 검색어와 일치하는지 또는 관련 질문이 일치하는지 확인
                sub_menu_matched_by_search = (
                    processed_search_query in sub_menu_item.lower() or
                    any(processed_search_query in q.lower() for q in all_questions.get(sub_menu_item, []))
                )

                # 현재 선택된 메뉴인지 확인
                is_selected = st.session_state.current_selected_sub_menu == sub_menu_item
                
                # 검색되었거나 선택된 메뉴를 강조 표시
                button_label = sub_menu_item
                if is_selected:
                    button_label = f"<span style='color:#007bff; font-weight:bold;'>{button_label}</span>" # 선택된 메뉴는 파란색 볼드
                if sub_menu_matched_by_search and not is_selected: # 검색은 되었으나 선택은 안된 경우
                    button_label = f"<span style='background-color:#fff3cd; padding:0.2em; border-radius:3px;'>{button_label}</span>" # 검색된 메뉴는 배경색으로 강조
                
                # st.button 대신 st.markdown을 사용하여 HTML을 직접 렌더링하고, 클릭 시 로직 처리
                # st.button은 HTML 마크다운을 직접 렌더링하지 않으므로, 링크와 세션 상태를 활용
                # Streamlit의 한계로 버튼처럼 보이게 하면서 클릭 시 URL 변경까지 하려면 더 복잡해집니다.
                # 여기서는 '선택' 상태와 '검색' 강조를 시각적으로 보여주고, 클릭 시 URL을 변경합니다.

                st.markdown(f"""
                    <a href="?menu={sub_menu_item}" target="_self" style="text-decoration: none;">
                        <button style="
                            width: 100%;
                            text-align: left;
                            background-color: {'#e0f7fa' if is_selected else ('#fff3cd' if sub_menu_matched_by_search else '#f0f2f6')};
                            color: {'#007bff' if is_selected else '#333333'};
                            border: {'1px solid #007bff' if is_selected else '1px solid #ddd'};
                            border-radius: 5px;
                            padding: 8px 12px;
                            margin-bottom: 5px;
                            cursor: pointer;
                            font-weight: {'bold' if is_selected else 'normal'};
                            white-space: normal;
                            word-wrap: break-word;
                            box-shadow: {'0 0 5px rgba(0, 123, 255, 0.3)' if is_selected else 'none'};
                        ">
                            {sub_menu_item}
                        </button>
                    </a>
                """, unsafe_allow_html=True)
                
                # 버튼을 통해 세션 상태를 업데이트하는 대신, URL 파라미터를 직접 사용하여 상태를 관리
                # 이 방식은 Streamlit 앱이 URL 변경을 감지하고 자동으로 재실행되므로
                # st.session_state를 업데이트하는 로직은 URL 초기 로드 시에만 필요해집니다.
                # (URL이 변경되면 앱이 처음부터 다시 로드되는 것처럼 동작하기 때문)


    st.markdown("---")

    # URL 쿼리 파라미터에서 직접 현재 선택된 메뉴를 가져와 사용
    # 버튼 클릭 시 URL이 변경되고 앱이 재실행되므로,
    # 이 시점에서 st.query_params는 항상 최신 상태를 반영합니다.
    current_selection = st.query_params.get('menu', [None])[0]

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
        # 초기 상태이거나 'menu' 파라미터가 없을 때만 안내 메시지 표시
        if not current_selection and not search_query:
            st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")

    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
