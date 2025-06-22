# main.py

import streamlit as st
from urllib.parse import urlencode, parse_qs

# 모듈 임포트 경로 변경: 상대 경로로 임포트합니다.
from .daily_worker_eligibility import daily_worker_eligibility_app
from .early_reemployment import early_reemployment_app
from .remote_assignment import remote_assignment_app
from .wage_delay import wage_delay_app
from .unemployment_recognition import unemployment_recognition_app
from .questions import (
    get_employment_questions,
    get_self_employment_questions,
    get_remote_assignment_questions,
    get_wage_delay_questions,
    get_daily_worker_eligibility_questions
)

def main():
    st.set_page_config(page_title="실업급여 지원 시스템", page_icon="💼", layout="centered")

    # 커스텀 CSS 적용 (static/styles.css 파일이 app/app.py와 같은 레벨의 static/ 폴더에 있다고 가정)
    try:
        with open("static/styles.css") as f: # 경로 확인: main.py 기준이 아니라, 스트림릿 앱 실행 위치 기준입니다.
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("경고: 'static/styles.css' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")

    st.title("💼 실업급여 도우미")

    # --- URL 쿼리 파라미터에서 현재 메뉴 상태 가져오기 ---
    query_params = st.query_params
    
    # 모든 하위 메뉴를 단일 리스트로 정의
    all_sub_menus = [
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청 가능 시점",
        "일용직(건설일용포함)"
    ]

    # 'menu' 파라미터 값 가져오기. 기본값은 첫 번째 하위 메뉴로 설정 (원하는 초기값으로 변경 가능)
    # URL 파라미터가 없거나 유효하지 않은 경우, '임금 체불 판단'을 기본으로 합니다.
    initial_selection = query_params.get('menu', [None])[0]
    if initial_selection not in all_sub_menus:
        initial_selection = "임금 체불 판단" # 유효하지 않은 파라미터면 기본값으로

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

            # 현재 URL의 'menu' 파라미터와 일치하는지 확인
            is_selected = initial_selection == sub_menu_item
            
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
            
            st.markdown(f"""
                <a href="?menu={sub_menu_item}" target="_self" style="text-decoration: none; display: block; margin-bottom: 5px;">
                    <button style="{button_style}">
                        {sub_menu_item}
                    </button>
                </a>
                <style>
                    /* Streamlit 버튼 기본 호버 스타일 제거 및 커스텀 호버 스타일 적용 */
                    button[data-baseweb="button"]:hover {{
                        background-color: transparent !important;
                        border-color: transparent !important;
                    }}
                    a:hover button {{
                        background-color: #e9ecef !important;
                        border-color: #bbbbbb !important;
                    }}
                </style>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # URL 쿼리 파라미터에서 현재 선택된 메뉴를 가져와 사용
    current_selection = query_params.get('menu', [None])[0]
    if current_selection not in all_sub_menus:
        current_selection = "임금 체불 판단" # 유효하지 않은 파라미터면 기본값으로

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
        # URL 파라미터가 비어있거나 유효하지 않을 때 초기 안내 메시지 표시
        # 이 else 블록은 위에 current_selection 기본값 설정으로 인해 사실상 실행되지 않을 가능성이 높습니다.
        # 하지만 혹시 모를 상황을 대비하여 유지합니다.
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하여 원하는 정보를 찾아보세요.")


    st.markdown("---")
    st.caption("ⓒ 2025 실업급여 도우미는 도움을 드리기 위한 목적입니다. 실제 가능 여부는 고용센터의 판단을 기준으로 합니다.")
    st.markdown("[나의 지역 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)에서 자세한 정보를 확인하세요.")

if __name__ == "__main__":
    main()
