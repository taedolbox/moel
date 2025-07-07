import streamlit as st
# 필요한 모든 앱 함수들을 임포트합니다.
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.remote_assignment import remote_assignment_app
from app.wage_delay import wage_delay_app
from app.unemployment_recognition import unemployment_recognition_app

# app.questions 관련 임포트는 요청하신 구조에 없으므로 제외합니다.
# from app.questions import (
#     get_employment_questions,
#     get_self_employment_questions,
#     get_remote_assignment_questions,
#     get_wage_delay_questions,
#     get_daily_worker_eligibility_questions
# )

# 사이드바 관련 함수는 요청하신 구조에 없으므로 제외합니다.
# def update_selected_menu(filtered_menus, all_menus):
#     selected_menu = st.session_state.menu_selector
#     if selected_menu in filtered_menus:
#         st.session_state.selected_menu = selected_menu
#         menu_id = all_menus.index(selected_menu) + 1
#         st.query_params["menu"] = str(menu_id)

def main():
    st.set_page_config(
        page_title="실업급여 지원 시스템",
        page_icon="💼",
        layout="centered"
    )

    # 사용자님이 요청하신 모든 메뉴 항목을 포함합니다.
    menus = [
        "메뉴 선택",
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청 가능 시점",
        "일용직(건설일용포함)"
    ]

    # 각 메뉴 이름에 해당하는 함수를 매핑합니다.
    # '실업급여 신청 가능 시점'은 별도 앱이 없다면 st.info로 대체합니다.
    menu_functions = {
        "임금 체불 판단": wage_delay_app,
        "원거리 발령 판단": remote_assignment_app,
        "실업인정": unemployment_recognition_app,
        "조기재취업수당": early_reemployment_app,
        "실업급여 신청 가능 시점": lambda: st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 관련 기능이 구현되면 이곳에 표시됩니다."),
        "일용직(건설일용포함)": daily_worker_eligibility_app
    }

    # all_questions 딕셔너리 및 사이드바 검색 기능은 요청하신 구조에 없으므로 제외합니다.
    # all_questions = { ... }
    # with st.sidebar: ...

    # 1. 초기 메뉴 인덱스 결정 (URL 또는 세션 상태)
    menu_param_from_url = st.query_params.get("menu", None)

    if "current_menu_idx" not in st.session_state:
        if menu_param_from_url and menu_param_from_url.isdigit():
            parsed_menu_idx = int(menu_param_from_url) - 1
            if 0 <= parsed_menu_idx < len(menus):
                st.session_state.current_menu_idx = parsed_menu_idx
            else:
                st.session_state.current_menu_idx = 0
        else:
            st.session_state.current_menu_idx = 0

    # CSS 스타일 (제공해주신 그대로 유지합니다)
    # static/styles.css 파일이 없다면 이 부분은 오류를 일으킬 수 있습니다.
    try:
        with open("static/styles.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # static/styles.css 파일이 없을 경우를 대비하여 직접 CSS를 삽입합니다.
        st.markdown("""
        <style>
        /* 콤보박스 선택 영역 (현재 선택된 값 표시되는 부분) */
        div[data-baseweb="select"] > div:first-child {
            border: 2px solid #2196F3 !important; /* 기존 테두리 유지 */
            color: #2196F3 !important;            /* 기존 텍스트 색상 유지 */
            font-weight: 600 !important;
            background-color: #E3F2FD !important; /* 콤보박스 배경색 변경 (밝은 파랑) */
        }

        /* 콤보박스 내부 텍스트 (현재 선택된 값) */
        div[data-baseweb="select"] span {
            color: #2196F3 !important;
            font-weight: 600 !important;
        }

        /* 드롭다운 리스트 컨테이너 */
        div[data-baseweb="popover"] {
            z-index: 9999 !important; /* 다른 요소 위에 오도록 z-index 높임 */
            background-color: #FFFFFF !important; /* 드롭다운 배경색 하얀색으로 명확하게 */
            border: 1px solid #2196F3 !important; /* 테두리 추가 */
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important; /* 그림자 추가 */
        }

        /* 드롭다운 리스트 항목 */
        div[data-baseweb="select"] ul[role="listbox"] li {
            color: #2196F3 !important;
            font-weight: 600 !important;
            padding: 10px 15px !important; /* 패딩 조정 */
        }

        /* 드롭다운 리스트 항목 호버 시 */
        div[data-baseweb="select"] ul[role="listbox"] li:hover {
            background-color: #2196F3 !important;
            color: white !important;
        }

        /* 스크롤바 스타일링 (선택 사항, 깔끔하게 보이게) */
        div[data-baseweb="popover"]::-webkit-scrollbar {
            width: 8px;
        }
        div[data-baseweb="popover"]::-webkit-scrollbar-thumb {
            background-color: #bbdefb; /* 연한 파랑 */
            border-radius: 4px;
        }
        div[data-baseweb="popover"]::-webkit-scrollbar-track {
            background-color: #f1f1f1;
        }

        /* 다크 모드 스타일 (추가) */
        html[data-theme="dark"] div[data-baseweb="select"] > div:first-child {
            background-color: #31333F !important;
            color: #FAFAFA !important;
            border: 2px solid #4B4B4B !important;
        }
        html[data-theme="dark"] div[data-baseweb="select"] span {
            color: #FAFAFA !important;
        }
        html[data-theme="dark"] div[data-baseweb="popover"] {
            background-color: #262730 !important;
            border: 1px solid #4B4B4B !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        }
        html[data-theme="dark"] div[data-baseweb="select"] ul[role="listbox"] li {
            color: #FAFAFA !important;
        }
        html[data-theme="dark"] div[data-baseweb="select"] ul[role="listbox"] li:hover {
            background-color: #45475A !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)


    # 2. st.selectbox에서 값 변경 시 세션 상태 및 URL 업데이트
    def on_menu_change():
        selected_menu_name = st.session_state.main_menu_select_key
        st.session_state.current_menu_idx = menus.index(selected_menu_name)

        if st.session_state.current_menu_idx == 0:
            if "menu" in st.query_params:
                del st.query_params["menu"] # "메뉴 선택" 시 URL 파라미터 제거
        else:
            # 선택된 메뉴의 인덱스를 1을 더하여 URL 파라미터로 저장 (사람에게 친숙한 1부터 시작)
            st.query_params["menu"] = str(st.session_state.current_menu_idx + 1)

    # 메인 화면에 메뉴 선택 콤보박스 배치
    st.selectbox(
        "📋 메뉴 선택",
        menus,
        index=st.session_state.current_menu_idx, # 현재 세션 상태의 인덱스 사용
        key="main_menu_select_key", # 콜백 함수를 위한 키
        on_change=on_menu_change # 값 변경 시 on_change 콜백 함수 호출
    )

    # --- ★여기에 요청하신 공통 문구를 추가합니다 (모든 페이지에 고정)★ ---
    st.markdown(
        "<span style='font-size:22px; font-weight:600;'>🏗️ 조기재취업수당 요건 판단</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='font-size:18px; font-weight:700; margin-bottom:10px;'>ⓘ 실업급여 도우미는 참고용입니다. 실제 가능 여부는 고용센터 판단을 따릅니다.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---") # 공통 문구 아래 시각적 구분선 추가
    # --- 공통 문구 추가 종료 ---

    # 3. 세션 상태의 current_menu_idx에 따라 화면 출력
    selected_idx = st.session_state.current_menu_idx

    if selected_idx == 0:
        # "메뉴 선택" 시 보여줄 초기 화면 내용
        st.markdown(
            """
            <div style="padding: 20px; border-radius: 10px; background-color: #f0f8ff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #0d47a1; margin-bottom: 15px;">🌟 실업급여 지원 시스템에 오신 것을 환영합니다!</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #333333;">  이 시스템은 <b>실업급여 수급 자격</b> 및 <b>조기재취업수당</b>과 관련된 정보를 쉽고 빠르게 확인하실 수 있도록 돕습니다.
                    <br><br>
                    궁금한 기능을 위에 있는 <b>'📋 메뉴 선택' 콤보박스에서 선택</b>해 주세요.
                </p>
                <ul style="font-size: 15px; line-height: 1.8; margin-top: 15px; color: #333333;">
                    <li>🔹 <b>임금 체불 판단:</b> 임금 체불로 인한 이직 사유 가능성을 판단합니다.</li>
                    <li>🔹 <b>원거리 발령 판단:</b> 원거리 발령으로 인한 이직 사유 가능성을 판단합니다.</li>
                    <li>🔹 <b>실업인정:</b> 실업인정 신청 및 관련된 정보를 확인합니다.</li>
                    <li>🔹 <b>조기재취업수당:</b> 조기재취업수당 신청 가능 여부를 판단합니다.</li>
                    <li>🔹 <b>실업급여 신청 가능 시점:</b> 일반 실업급여 신청 가능 시점을 안내합니다.</li>
                    <li>🔹 <b>일용직(건설일용포함):</b> 일용직 근로자의 실업급여 신청 가능 시점을 판단합니다.</li>
                </ul>
                <p style="font-size: 14px; color: #555; margin-top: 20px;">
                    💡 <b>주의:</b> 본 시스템의 결과는 참고용이며, 최종적인 실업급여 수급 여부는 관할 고용센터의 판단에 따릅니다.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown("---") # 또 다른 시각적 구분선
    # 각 메뉴 항목에 해당하는 앱 함수를 호출합니다.
    elif selected_idx == menus.index("임금 체불 판단"):
        wage_delay_app()
    elif selected_idx == menus.index("원거리 발령 판단"):
        remote_assignment_app()
    elif selected_idx == menus.index("실업인정"):
        unemployment_recognition_app()
    elif selected_idx == menus.index("조기재취업수당"):
        early_reemployment_app()
    elif selected_idx == menus.index("실업급여 신청 가능 시점"):
        # '실업급여 신청 가능 시점'은 menu_functions에서 정의한 람다 함수를 직접 호출합니다.
        menu_functions["실업급여 신청 가능 시점"]()
    elif selected_idx == menus.index("일용직(건설일용포함)"):
        daily_worker_eligibility_app()

if __name__ == "__main__":
    main()
