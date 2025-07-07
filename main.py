import streamlit as st

# 필요한 모든 앱 함수들을 임포트합니다.
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

def update_selected_menu(filtered_menus, all_menus):
    """
    사이드바 라디오 버튼 선택 시 세션 상태 및 쿼리 파라미터 업데이트
    """
    selected_menu = st.session_state.menu_selector
    if selected_menu in filtered_menus:
        st.session_state.selected_menu = selected_menu
        # URL 쿼리 파라미터 업데이트 (메뉴 ID는 1부터 시작)
        menu_id = all_menus.index(selected_menu) + 1
        st.query_params["menu"] = str(menu_id)
    else:
        # 검색 등으로 인해 선택된 메뉴가 필터링된 목록에 없을 경우 처리
        st.session_state.selected_menu = None
        if "menu" in st.query_params:
            del st.query_params["menu"]

def main():
    st.set_page_config(
        page_title="실업급여 지원 시스템",
        page_icon="💼",
        layout="centered" # 페이지 내용을 중앙에 정렬
    )

    # CSS 적용 (static/styles.css 파일이 존재해야 합니다)
    try:
        with open("static/styles.css", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # static/styles.css 파일이 없을 경우를 대비하여 직접 CSS를 삽입합니다.
        # 이 CSS는 콤보박스와 다크 모드 스타일을 포함합니다.
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


    # 전체 메뉴 목록 (순서 중요)
    # "메뉴 선택"을 포함하여 총 7개의 메뉴 항목을 콤보박스에 표시합니다.
    all_menus = [
        "메뉴 선택", # 초기 화면을 위한 메뉴
        "임금 체불 판단",
        "원거리 발령 판단",
        "실업인정",
        "조기재취업수당",
        "실업급여 신청 가능 시점",
        "일용직(건설일용포함)"
    ]

    # 각 메뉴에 연결될 함수 매핑
    menu_functions = {
        "임금 체불 판단": wage_delay_app,
        "원거리 발령 판단": remote_assignment_app,
        "실업인정": unemployment_recognition_app,
        "조기재취업수당": early_reemployment_app,
        "실업급여 신청 가능 시점": lambda: st.info("이곳은 일반 실업급여 신청 가능 시점 안내 페이지입니다. 관련 기능이 구현되면 이곳에 표시됩니다."),
        "일용직(건설일용포함)": daily_worker_eligibility_app
    }

    # 검색 기능 및 질문 데이터 (questions.py에 정의되어야 함)
    all_questions = {
        "임금 체불 판단": get_wage_delay_questions(),
        "원거리 발령 판단": get_remote_assignment_questions(),
        "실업인정": [], # 실업인정 관련 질문이 있다면 여기에 추가
        "조기재취업수당": get_employment_questions() + get_self_employment_questions(),
        "실업급여 신청 가능 시점": [], # 일반 실업급여 질문이 있다면 여기에 추가
        "일용직(건설일용포함)": get_daily_worker_eligibility_questions()
    }

    # --- 사이드바 시작 ---
    with st.sidebar:
        st.markdown("### 🔍 검색")
        search_query = st.text_input("메뉴 또는 질문을 검색하세요", key="search_query")

        filtered_menus = all_menus
        if search_query:
            search_query = search_query.lower()
            filtered_menus = [
                menu for menu in all_menus
                if search_query in menu.lower() or
                any(search_query in q.lower() for q in all_questions.get(menu, []))
            ]

        # 세션 상태 초기화 및 URL 쿼리 파라미터 처리
        if "selected_menu" not in st.session_state:
            url_menu_id = st.query_params.get("menu", None)
            default_menu = None
            if url_menu_id and url_menu_id.isdigit():
                try:
                    menu_idx = int(url_menu_id) - 1
                    if 0 <= menu_idx < len(all_menus):
                        default_menu = all_menus[menu_idx]
                except ValueError:
                    pass
            # URL 파라미터가 유효하면 해당 메뉴로, 아니면 필터링된 메뉴의 첫 번째 항목으로 설정
            st.session_state.selected_menu = default_menu if default_menu in all_menus else (filtered_menus[0] if filtered_menus else None)

        if filtered_menus:
            # st.radio는 기본적으로 on_change를 통해 값을 즉시 업데이트하므로,
            # 별도의 if selected_menu != st.session_state.selected_menu: 로직은 필요 없습니다.
            st.radio(
                "📋 메뉴", # 사이드바의 라디오 버튼 메뉴
                filtered_menus,
                index=filtered_menus.index(st.session_state.selected_menu)
                if st.session_state.selected_menu in filtered_menus else 0, # 현재 선택된 메뉴가 필터링된 목록에 없으면 첫 항목 선택
                key="menu_selector",
                on_change=lambda: update_selected_menu(filtered_menus, all_menus) # 콜백 함수 호출
            )
        else:
            st.warning("검색 결과에 해당하는 메뉴가 없습니다.")
            st.session_state.selected_menu = None # 검색 결과 없으면 선택된 메뉴 초기화

        st.markdown("---")
        st.markdown("[📌 고용센터 찾기](https://www.work24.go.kr/cm/c/d/0190/retrieveInstSrchLst.do)")
    # --- 사이드바 끝 ---

    # --- ★여기에 요청하신 공통 문구를 추가합니다 (모든 페이지에 고정)★ ---
    # 사이드바 아래, 메인 콘텐츠 시작 부분에 고정적으로 표시됩니다.
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

    # 선택된 메뉴에 따라 해당 함수 호출하여 내용 표시
    if st.session_state.selected_menu == "메뉴 선택":
        # "메뉴 선택" 시 보여줄 초기 화면 내용 (이전에 요청하셨던 상세 환영 메시지)
        st.markdown(
            """
            <div style="padding: 20px; border-radius: 10px; background-color: #f0f8ff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #0d47a1; margin-bottom: 15px;">🌟 실업급여 지원 시스템에 오신 것을 환영합니다!</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #333333;">  이 시스템은 <b>실업급여 수급 자격</b> 및 <b>조기재취업수당</b>과 관련된 정보를 쉽고 빠르게 확인하실 수 있도록 돕습니다.
                    <br><br>
                    궁금한 기능을 왼쪽에 있는 <b>'📋 메뉴' 라디오 버튼에서 선택</b>해 주세요.
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
    elif st.session_state.selected_menu:
        # 선택된 메뉴에 해당하는 함수를 호출합니다.
        menu_functions[st.session_state.selected_menu]()
    else:
        # 메뉴가 선택되지 않았거나 검색 결과가 없는 경우의 기본 화면
        # 이 경우는 '메뉴 선택' 초기 화면과 유사하게 처리하거나, 간략한 안내를 할 수 있습니다.
        st.info("왼쪽 사이드바에서 메뉴를 선택하거나 검색어를 입력하세요.")


if __name__ == "__main__":
    main()
