# app/daily_worker_eligibility.py

import streamlit as st
from datetime import datetime, timedelta
import json

def daily_worker_eligibility_app():
    st.markdown(
        "<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>",
        unsafe_allow_html=True
    )

    # 세션 상태 초기화
    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []
    if 'js_message' not in st.session_state:
        st.session_state.js_message = ""

    # 한국표준시 현재 날짜
    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    # 달력 날짜 생성: 신청일 기준 직전 달 1일부터 신청일까지
    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date
    cal_dates = []
    current_date = first_day_prev_month
    while current_date <= last_day:
        cal_dates.append(current_date)
        current_date += timedelta(days=1)

    calendar_groups = {}
    for date in cal_dates:
        year_month = date.strftime("%Y-%m")
        if year_month not in calendar_groups:
            calendar_groups[year_month] = []
        calendar_groups[year_month].append(date)

    # CSS로 입력 필드 숨김
    st.markdown("""
    <style>
    input[data-testid="stTextInput"] {
        display: none !important;
    }
    label[for="js_message"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")
    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")

    # 달력 HTML 생성
    calendar_html = """
    <div id="calendar-container">
    """

    for ym, dates in calendar_groups.items():
        year, month = ym.split("-")
        calendar_html += f"""
        <h4>{year}년 {month}월</h4>
        <div class="calendar">
            <div class="day-header">일</div>
            <div class="day-header">월</div>
            <div class="day-header">화</div>
            <div class="day-header">수</div>
            <div class="day-header">목</div>
            <div class="day-header">금</div>
            <div class="day-header">토</div>
        """
        first_day_of_month = dates[0]
        start_day_offset = (first_day_of_month.weekday() + 1) % 7
        for _ in range(start_day_offset):
            calendar_html += '<div class="empty-day"></div>'
        for date in dates:
            day_num = date.day
            date_str = date.strftime("%m/%d")
            is_selected = " selected" if date_str in st.session_state.selected_dates_list else ""
            calendar_html += f'''
            <div class="day{is_selected}" data-date="{date_str}" onclick="toggleDate(this)">{day_num}</div>
            '''
        calendar_html += "</div>"

    calendar_html += f"""
    </div>
    <p id="selectedDatesText"></p>
    <div id="resultContainer"></div>

    <style>
    .calendar {{
        display: grid;
        grid-template-columns: repeat(7, 40px);
        grid-gap: 5px;
        margin-bottom: 20px;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .day-header, .empty-day {{
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        font-weight: bold;
        color: #555;
    }}
    .day-header {{
        background-color: #e0e0e0;
        border-radius: 5px;
        font-size: 14px;
    }}
    .empty-day {{
        background-color: transparent;
        border: none;
    }}
    .day {{
        width: 40px;
        height: 40px;
        line-height: 40px;
        text-align: center;
        border: 1px solid #ddd;
        border-radius: 5px;
        cursor: pointer;
        user-select: none;
        transition: background-color 0.1s ease, border 0.1s ease;
        font-size: 16px;
        color: #333;
    }}
    .day:hover {{
        background-color: #f0f0f0;
    }}
    .day.selected {{
        border: 2px solid #2196F3;
        background-color: #2196F3;
        color: white;
        font-weight: bold;
    }}
    h4 {{
        margin: 10px 0 5px 0;
        font-size: 1.2em;
        color: #333;
        text-align: center;
    }}
    #selectedDatesText {{
        margin-top: 15px;
        font-size: 0.9em;
        color: #666;
    }}
    #resultContainer {{
        margin-top: 20px;
        padding: 15px;
        background-color: #f9f9f9;
        border-radius: 8px;
        font-size: 1em;
        color: #333;
        overflow: visible; 
        white-space: pre-wrap;
    }}
    #calendar-container {{
        overflow: visible;
    }}
    </style>

    <script>
    const CALENDAR_DATES = {calendar_dates_json};
    const FOURTEEN_DAYS_START = "{fourteen_days_prior_start}";
    const FOURTEEN_DAYS_END = "{fourteen_days_prior_end}";

    // 선택 날짜 저장 (localStorage와 부모창에 postMessage)
    function saveToLocalStorage(data) {{
        localStorage.setItem('selectedDates', JSON.stringify(data));
        window.parent.postMessage(JSON.stringify(data), '*');
    }}

    // 조건 판단 및 결과 표시 함수
    function calculateAndDisplayResult(selected) {{
        const totalDays = CALENDAR_DATES.length;
        const threshold = totalDays / 3;
        const workedDays = selected.length;

        // 14일 범위 필터링
        const fourteenDays = CALENDAR_DATES.filter(date => 
            date >= FOURTEEN_DAYS_START && date <= FOURTEEN_DAYS_END
        );

        // 조건 2 체크: 14일 동안 근무일 없음 확인
        // selected에는 mm/dd 형태, fourteenDays는 yyyy-mm-dd
        // 날짜 포맷 맞추기 위해 mm/dd로 변환 후 포함 여부 판단
        const fourteenDays_mmdd = fourteenDays.map(d => {
            const parts = d.split("-");
            return (parts[1].padStart(2,"0") + "/" + parts[2].padStart(2,"0"));
        });
        const noWork14Days = fourteenDays_mmdd.every(date => !selected.includes(date));

        // 조건 텍스트 상시 표시
        const cond1Desc = "조건 1 → 신청일이 속한 달의 직전 달 첫날부터 신청일까지 근무일 수가 전체 기간의 1/3 미만이어야 함.";
        const cond2Desc = "조건 2 → 건설일용근로자만 해당, 신청일 직전 14일간(신청일 제외) 근무 사실이 없어야 함.";

        // 조건 1 충족 여부
        const cond1Result = workedDays < threshold;
        const cond1Text = cond1Result 
            ? "✅ 조건 1 충족: 근무일 수가 기준 미만입니다." 
            : "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.";

        // 조건 2 충족 여부
        const cond2Text = noWork14Days
            ? `✅ 조건 2 충족: 신청일 직전 14일간(${FOURTEEN_DAYS_START} ~ ${FOURTEEN_DAYS_END}) 무근무`
            : `❌ 조건 2 불충족: 신청일 직전 14일간(${FOURTEEN_DAYS_START} ~ ${FOURTEEN_DAYS_END}) 내 근무기록이 존재`;

        // 조건 2 미충족 안내
        let cond2Guide = "";
        if (!noWork14Days) {{
            const nextPossibleDate = new Date(FOURTEEN_DAYS_END);
            nextPossibleDate.setDate(nextPossibleDate.getDate() + 14);
            const nextDateStr = nextPossibleDate.toISOString().split('T')[0];
            cond2Guide = `조건 2를 충족하려면 오늘 이후에 근로제공이 없는 경우 ${nextDateStr} 이후에 신청하면 조건 2를 충족할 수 있습니다.`;
        }}

        // 최종 판단
        const generalWorkerText = cond1Result ? "✅ 신청 가능" : "❌ 신청 불가능";
        let constructionWorkerText = "";
        if (cond1Result && noWork14Days) {{
            constructionWorkerText = "✅ 신청 가능";
        }} else if (!cond1Result && !noWork14Days) {{
            constructionWorkerText = "❌ 신청 불가능 (조건 1, 2 모두 불충족)";
        }} else if (!cond1Result) {{
            constructionWorkerText = "❌ 신청 불가능 (조건 1 불충족)";
        }} else {{
            constructionWorkerText = "❌ 신청 불가능 (조건 2 불충족)";
        }}

        // 결과 HTML 구성
        const resultHtml = `
조건 판단
${cond1Desc}
${cond2Desc}

${cond1Text}
${cond2Text}
${cond2Guide ? cond2Guide + "\\n" : ""}

📌 최종 판단
일반일용근로자: ${generalWorkerText}
건설일용근로자: ${constructionWorkerText}
        `;

        document.getElementById('resultContainer').innerText = resultHtml;
    }}

    // 날짜 선택 토글
    function toggleDate(element) {{
        element.classList.toggle('selected');
        const selected = [];
        const days = document.getElementsByClassName('day');
        for (let i = 0; i < days.length; i++) {{
            if (days[i].classList.contains('selected')) {{
                selected.push(days[i].getAttribute('data-date'));
            }}
        }}
        saveToLocalStorage(selected);
        calculateAndDisplayResult(selected);
        document.getElementById('selectedDatesText').innerText = "선택한 날짜: " + selected.join(', ') + " (" + selected.length + "일)";
    }}

    // 페이지 로드 시 초기화 및 선택 상태 표시
    window.onload = function() {{
        const initialDates = "{','.join(st.session_state.selected_dates_list)}";
        let initialSelected = [];
        if (initialDates) {{
            initialSelected = initialDates.split(',').filter(date => date);
            const days = document.getElementsByClassName('day');
            for (let i = 0; i < days.length; i++) {{
                if (initialSelected.includes(days[i].getAttribute('data-date'))) {{
                    days[i].classList.add('selected');
                }}
            }}
        }}
        saveToLocalStorage(initialSelected);
        calculateAndDisplayResult(initialSelected);
        document.getElementById('selectedDatesText').innerText = "선택한 날짜: " + initialSelected.join(', ') + " (" + initialSelected.length + "일)";
    }};
    </script>
    """

    st.components.v1.html(calendar_html, height=1000, scrolling=False)
