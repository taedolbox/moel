# main.py

import streamlit as st
from urllib.parse import unquote_plus # unquote_plus 함수 임포트 확인

# app 폴더 내 모듈 임포트 확인
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

    try:
        with open("static/styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("경고: 'static/styles.css' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")

    st.title("💼 실업급여 도우미")

    all_sub_menus = [
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청가능 시점",
        "일용직(건설일용포함)"
    ]

    # --- URL 쿼리 파라미터에서 현재 메뉴 상태를 가져오고, 유효성을 검사합니다. ---
    # st.query_params는 항상 현재 URL을 반영합니다.
    raw_current_selection = st.query_params.get('menu', None)
    
    current_selection = None
    if raw_current_selection:
        current_selection = unquote_plus(raw_current_selection) # URL에서 가져온 값을 여기서 디코딩

    if current_selection not in all_sub_menus:
        current_selection = "임금 체불 판단" # 유효하지 않으면 기본값 설정

    # Sidebar
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")
        processed_search_query = search_query.lower() if search_query else ""

        questions_map = {
            "임금 체불 판단": get_wage_delay_questions(),
            "원거리 발령 판단": get_remote_assignment_questions(),
            "실업인정": [],
            "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
            "실업급여 신청가능 시점": [],
            "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
        }

        st.markdown("### 📌 메뉴 선택")

        for sub_menu_item in all_sub_menus:
            sub_menu_matched_by_search = (
                processed_search_query in sub_menu_item.lower() or
                any(processed_search_query in q.lower() for q in questions_map.get(sub_menu_item, []))
            )

            is_selected = current_selection == sub_menu_item
            
            # HTML 버튼 스타일을 인라인으로 정의
            button_background = '#e0f7fa' if is_selected else ('#fff3cd' if sub_menu_matched_by_search and processed_search_query else '#f0f2f6')
            button_color = '#007bff' if is_selected else '#333333'
            button_border = '1px solid #007bff' if is_selected else '1px solid #ddd'
            button_font_weight = 'bold' if is_selected else 'normal'
            button_box_shadow = '0 0 5px rgba(0, 123, 255, 0.3)' if is_selected else 'none'

            # --- 핵심 변경 부분: st.button과 st.experimental_set_query_params/rerun 사용 ---
            # 여기서 st.button을 사용하고, 클릭 시 st.experimental_set_query_params로 URL을 명시적으로 변경합니다.
            # 이 방법이 URL과 앱 상태 동기화에 더 강력합니다.
            
            # 버튼 클릭 시에만 URL 변경 로직을 실행하도록 합니다.
            # is_selected 상태를 사용하여 버튼의 시각적 강조는 그대로 유지합니다.
            if st.button(
                sub_menu_item, 
                key=f"sidebar_btn_{sub_menu_item}",
                # 선택된 버튼에 대한 스타일링은 Streamlit 자체 버튼 기능으로 대체될 수 있습니다.
                # 그러나 사용자 정의 스타일을 유지하려면, 버튼 클릭 후 URL 변경 및 재실행으로 CSS가 다시 적용되도록 합니다.
            ):
                # 다른 쿼리 파라미터가 있다면 유지하면서 'menu'만 변경
                # 현재 쿼리 파라미터를 딕셔너리로 복사
                updated_params = {k: v for k, v in st.query_params.items()}
                updated_params['menu'] = sub_menu_item
                
                st.experimental_set_query_params(**updated_params)
                st.experimental_rerun() # 변경된 URL로 앱을 재실행하여 페이지를 다시 로드합니다.
            
            # 버튼 아래에 커스텀 스타일을 적용하기 위해 빈 markdown 요소를 추가할 수 있습니다.
            # 그러나 st.button은 직접적인 CSS 클래스나 인라인 스타일링이 어렵습니다.
            # 따라서 이전의 HTML 버튼 방식의 스타일링을 유지하려면, st.button 대신 다시 HTML 마크다운 방식을 사용해야 합니다.
            # 현재 코드 (이전 답변의 HTML 버튼 방식)가 URL을 변경하지 않았다면, 문제는 배포 환경 캐싱입니다.

    st.markdown("---")

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
