# main.py

import streamlit as st
# urllib.parse는 이제 직접적으로 사용되지 않습니다.
# from urllib.parse import urlencode, parse_qs

# app 폴더 내 모듈들을 임포트합니다.
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

    # 커스텀 CSS 적용
    try:
        with open("static/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("경고: 'static/styles.css' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")

    st.title("💼 실업급여 도우미")

    # 모든 하위 메뉴를 단일 리스트로 정의
    all_sub_menus = [
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청가능 시점",
        "일용직(건설일용포함)"
    ]

    # --- URL 쿼리 파라미터에서 현재 메뉴 상태를 가져오고, 유효성을 검사합니다. ---
    # st.query_params는 앱이 재실행될 때마다 현재 URL의 파라미터를 반영합니다.
    current_selection = st.query_params.get('menu', [None])[0]
    
    # URL 파라미터가 없거나, 유효한 메뉴 목록에 없는 값이라면 기본 메뉴를 설정합니다.
    if current_selection not in all_sub_menus:
        current_selection = "임금 체불 판단" # 기본값 설정

    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")
        processed_search_query = search_query.lower() if search_query else ""

        # 각 하위 메뉴에 연결된 질문 정의 (검색 기능 유지를 위해 필요)
        questions_map = {
            "임금 체불 판단": get_wage_delay_questions(),
            "원거리 발령 판단": get_remote_assignment_questions(),
            "실업인정": [],
            "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
            "실업급여 신청 가능 시점": [],
            "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
        }

        st.markdown("### 📌 메뉴 선택")

        for sub_menu_item in all_sub_menus:
            # 하위 메뉴가 검색어와 일치하는지 또는 관련 질문이 일치하는지 확인
            sub_menu_matched_by_search = (
                processed_search_query in sub_menu_item.lower() or
                any(processed_search_query in q.lower() for q in questions_map.get(sub_menu_item, []))
            )

            # 현재 `current_selection`과 일치하는지 확인
            is_selected = current_selection == sub_menu_item
            
            # HTML 버튼 스타일을 인라인으로 정의
            button_style = f"""
                width: 100%;
                text-align: left;
                background-color: {'#e0f7fa' if is_selected else ('#fff3cd' if sub_menu_matched_by_search and processed_search_query else '#f0f2f6')};
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
                transition: background-color 0.2s, border-color 0.2s, box-shadow 0.2s;
            """
            
            # 여기서 st.button을 다시 사용하고, 클릭 시 st.experimental_set_query_params로 URL을 명시적으로 변경합니다.
            # 이 방법이 URL과 앱 상태 동기화에 더 강력합니다.
            if st.button(sub_menu_item, key=f"sidebar_btn_{sub_menu_item}", 
                         type="primary" if is_selected else "secondary"): # 선택된 버튼 시각적으로 강조
                st.experimental_set_query_params(menu=sub_menu_item)
                st.experimental_rerun() # 변경된 URL로 앱을 재실행하여 페이지를 다시 로드합니다.

        # 검색된 메뉴 강조를 위한 CSS 추가 (선택적)
        if processed_search_query:
            st.markdown(f"""
                <style>
                    /* 검색된 메뉴에만 적용될 스타일 */
                    [data-testid="stSidebar"] button[key*="sidebar_btn_"] {{
                        background-color: var(--search-highlight-bg, #fff3cd);
                    }}
                </style>
            """, unsafe_allow_html=True)


    st.markdown("---")

    # --- 메인 콘텐츠 표시 로직 ---
    # `current_selection`은 이미 위에서 URL 파라미터 값으로 설정되었으므로 바로 사용합니다.
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
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")


    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
