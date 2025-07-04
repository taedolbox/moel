import streamlit as st
from datetime import datetime, timedelta
from app.eligibility_logic import check_conditions  # 조건 판단 함수 임포트

def daily_worker_eligibility_app():
    st.markdown("<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>", unsafe_allow_html=True)

    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date

    # 달력 날짜 리스트 생성
    cal_dates = []
    current = first_day_prev_month
    while current <= last_day:
        cal_dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)

    # 세션 상태 초기화
    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []

    # JS에서 날짜 리스트로 받기 위해 JSON 문자열
    calendar_dates_json = cal_dates

    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # streamlit.components.v1.html() 호출 시 선택된 날짜 전달
    selected_dates_str = ",".join([d[5:10].replace("-", "/") for d in st.session_state.selected_dates_list])  # mm/dd 형식

    # HTML + JS (중략)...
    # 여기서 toggleDate 함수 내에서 선택한 날짜들을 window.parent.postMessage()를 통해 Streamlit으로 전달
    # Streamlit에서는 st.experimental_get_query_params() 또는 st.session_state 업데이트 등으로 받아 처리

    # 아래는 대략적 예시입니다.
    calendar_html = f"""
    <div id="calendar-container"></div>
    <p id="selectedDatesText">선택된 날짜들: {selected_dates_str}</p>
    <div id="resultContainer"></div>

    <script>
    const CALENDAR_DATES = {calendar_dates_json};
    const FOURTEEN_DAYS_START = "{fourteen_days_prior_start}";
    const FOURTEEN_DAYS_END = "{fourteen_days_prior_end}";

    let selectedDates = new Set();

    function toggleDate(element) {{
        const date = element.getAttribute('data-date');
        if (selectedDates.has(date)) {{
            selectedDates.delete(date);
            element.classList.remove('selected');
        }} else {{
            selectedDates.add(date);
            element.classList.add('selected');
        }}
        updateSelectedDatesText();
        sendSelectedDatesToStreamlit();
    }}

    function updateSelectedDatesText() {{
        document.getElementById('selectedDatesText').innerText = "선택된 날짜들: " + Array.from(selectedDates).join(', ');
    }}

    function sendSelectedDatesToStreamlit() {{
        const datesArray = Array.from(selectedDates);
        // Streamlit에 메시지 보내기 (postMessage 활용)
        window.parent.postMessage({{type:'selected_dates', dates:datesArray}}, '*');
    }}

    // Streamlit 메시지 수신 이벤트
    window.addEventListener('message', event => {{
        if(event.data.type === 'set_selected_dates'){{
            selectedDates = new Set(event.data.dates);
            updateCalendarUI();
            updateSelectedDatesText();
        }}
    }});

    function updateCalendarUI() {{
        // 달력 UI 업데이트 (선택된 날짜 표시)
    }}

    // 페이지 로드 시 달력 렌더링 및 이벤트 연결 등 (생략)

    </script>
    """

    # streamlit.components.v1.html(calendar_html, height=600, scrolling=False)

    # Streamlit 쪽에서 postMessage 수신을 받아 날짜 리스트 갱신 필요 (서버-클라이언트 통신)

    # 날짜 선택에 따라 조건 판단 함수 호출 및 결과 표시
    # st.markdown()에 조건 판단 결과 출력



