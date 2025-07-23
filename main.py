import streamlit as st
import os
import time

# 필요한 앱 함수들만 임포트
from app.daily_worker_eligibility import daily_worker_eligibility_app
from app.early_reemployment import early_reemployment_app
from app.unemployment_recognition import unemployment_recognition_app

def load_css(file_name):
    """CSS 파일을 읽어 Streamlit에 적용합니다."""
    current_dir = os.path.dirname(__file__)
    css_path = os.path.join(current_dir, file_name)
    with open(css_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="실업급여 지원 시스템",
        page_icon="💼",
        layout="centered"
    )

    # 캐싱 방지 위해 타임스탬프 추가
    cache_buster = int(time.time())

    # 외부 CSS 파일 로드 및 인라인 CSS 추가
    with st.container():
        load_css('static/styles.css')
        st.markdown(f"""
        <link rel="stylesheet" href="/static/styles.css?v={cache_buster}">
        <style>
            /* Manage app 버튼 숨기기 */
            .stAppDeployButton, [data-testid="stAppDeployButton"] {{
                display: none !important;
                visibility: hidden !important;
            }}
            /* 콤보박스 스타일 강화 */
            div[data-baseweb="select"] > div:first-child,
            [data-testid="stSelectbox"], [data-testid="stSelectbox"] > div,
            [data-testid="stSelectbox"] [role="combobox"],
            [class*="st-emotion-cache"][data-testid="stSelectbox"],
            [class*="st-emotion-cache"] [role="combobox"] {{
                border: 2px solid #2196F3 !important;
                color: #2196F3 !important;
                font-weight: 600 !important;
                background-color: #E3F2FD !important;
                z-index: 2 !important;
                border-radius: 4px !important;
                box-sizing: border-box !important;
            }}
            div[data-baseweb="select"] span, [data-testid="stSelectbox"] span,
            [class*="st-emotion-cache"] span {{
                color: #2196F3 !important;
                font-weight: 600 !important;
            }}
        </style>
        <div class="custom-header">실업급여 도우미</div>
        <script>
            console.log("Custom header element:", document.querySelector(".custom-header"));
            console.log("stAppHeader element:", document.querySelector(".stAppHeader"));
            console.log("stToolbar element:", document.querySelector("[data-testid='stToolbar']"));
            console.log("stMainMenu element:", document.querySelector("[data-testid='stMainMenu']"));
            console.log("stAppDeployButton element:", document.querySelector("[data-testid='stAppDeployButton']"));
            console.log("Selectbox element:", document.querySelector("[data-testid='stSelectbox']"));
            if (!document.querySelector(".custom-header")) {{
                console.error("Custom header not found in DOM");
            }} else {{
                const header = document.querySelector(".custom-header");
                console.log("Custom header styles:", getComputedStyle(header));
                console.log("Custom header position:", header.getBoundingClientRect());
            }}
            if (document.querySelector(".stAppHeader")) {{
                console.log("stAppHeader styles:", getComputedStyle(document.querySelector(".stAppHeader")));
            }}
            if (document.querySelector("[data-testid='stToolbar']")) {{
                console.log("stToolbar styles:", getComputedStyle(document.querySelector("[data-testid='stToolbar']")));
            }}
            if (document.querySelector("[data-testid='stMainMenu']")) {{
                console.log("stMainMenu styles:", getComputedStyle(document.querySelector("[data-testid='stMainMenu']")));
            }}
            if (document.querySelector("[data-testid='stAppDeployButton']")) {{
                console.log("stAppDeployButton styles:", getComputedStyle(document.querySelector("[data-testid='stAppDeployButton']")));
            }}
            if (document.querySelector("[data-testid='stSelectbox']")) {{
                console.log("Selectbox styles:", getComputedStyle(document.querySelector("[data-testid='stSelectbox']")));
            }}
        </script>
        """, unsafe_allow_html=True)

    # 각 메뉴에 연결될 함수 매핑
    menu_functions = {
        "실업인정": unemployment_recognition_app,
        "조기재취업수당": early_reemployment_app,
        "일용직(건설일용포함)": daily_worker_eligibility_app
    }

    # 메뉴와 표시될 텍스트 제목
    menu_text_titles = {
        "메뉴 선택": "실업급여 지원 시스템",
        "실업인정": "실업인정",
        "조기재취업수당": "조기재취업수당 요건 판단",
        "일용직(건설일용포함)": "일용직(건설일용포함)"
    }

    # 메뉴 목록
    menus = list(menu_text_titles.keys())

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

    # 2. st.selectbox에서 값 변경 시 세션 상태 및 URL 업데이트
    def on_menu_change():
        selected_menu_name = st.session_state.main_menu_select_key
        st.session_state.current_menu_idx = menus.index(selected_menu_name)

        if st.session_state.current_menu_idx == 0:
            if "menu" in st.query_params:
                del st.query_params["menu"]
        else:
            st.query_params["menu"] = str(st.session_state.current_menu_idx + 1)

    # 메뉴 선택 콤보박스 배치
    with st.container():
        st.selectbox(
            "📋 메뉴 선택",
            menus,
            index=st.session_state.current_menu_idx,
            key="main_menu_select_key",
            on_change=on_menu_change
        )

    # --- 콤보박스와 아래 콘텐츠 구분선 ---
    st.markdown("---")

    # 3. 세션 상태의 current_menu_idx에 따라 화면 출력
    selected_idx = st.session_state.current_menu_idx
    selected_menu_name = menus[selected_idx]

    # 메뉴 제목 표시
    display_text_title = menu_text_titles.get(selected_menu_name, selected_menu_name)

    st.markdown(
        f"<span style='font-size:22px; font-weight:600;'>🏗️ {display_text_title}</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='font-size:18px; font-weight:700; margin-bottom:10px;'>ⓘ 실업급여 도우미는 참고용입니다. 실제 가능 여부는 고용센터 판단을 따릅니다.</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    if selected_idx == 0:
        # "메뉴 선택" 시 초기 화면 내용
        st.markdown(
            """
            <div style="padding: 20px; border-radius: 10px; background-color: #f0f8ff; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                <h3 style="color: #0d47a1; margin-bottom: 15px;">🌟 환영합니다! 아래에서 궁금한 기능을 선택해 주세요.</h3>
                <p style="font-size: 16px; line-height: 1.6; color: #333333;"> 이 시스템은 <b>실업급여 수급 자격</b> 및 <b>조기재취업수당</b>과 관련된 정보를 쉽고 빠르게 확인하실 수 있도록 돕습니다.
                    <br><br>
                    <span style="font-weight: bold; color: #e91e63;">'📋 메뉴 선택' 콤보박스에서 기능을 선택해주세요!</span>
                </p>
                <ul style="font-size: 15px; line-height: 1.8; margin-top: 15px; color: #333333;">
                    <li>🔹 <b>실업인정:</b> 실업인정 신청 및 관련된 정보를 확인합니다.</li>
                    <li>🔹 <b>조기재취업수당:</b> 조기재취업수당 신청 가능 여부를 판단합니다.</li>
                    <li>🔹 <b>일용직(건설일용포함):</b> 일용직 근로자의 실업급여 신청 가능 시점을 판단합니다.</li>
                </ul>
                <p style="font-size: 14px; color: #555; margin-top: 20px;">
                    💡 <b>주의:</b> 본 시스템의 결과는 참고용이며, 최종적인 실업급여 수급 여부는 관할 고용센터의 판단에 따릅니다.
                </p>
            </div>
            """, unsafe_allow_html=True
        )
        st.markdown("---")
    else:
        # 선택된 메뉴에 해당하는 함수 호출
        if selected_menu_name in menu_functions:
            menu_functions[selected_menu_name]()
        else:
            st.error("선택된 메뉴에 해당하는 페이지를 찾을 수 없습니다.")
            st.info("다시 메뉴를 선택해주세요.")

if __name__ == "__main__":
    main()
