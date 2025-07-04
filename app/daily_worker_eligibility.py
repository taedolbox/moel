# app/daily_worker_eligibility.py

import streamlit as st
from datetime import datetime, timedelta
import json

def daily_worker_eligibility_app():
    st.markdown(
        "<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>",
        unsafe_allow_html=True
    )

    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []
    if 'js_message' not in st.session_state:
        st.session_state.js_message = ""

    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

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

    st.markdown("""
    <style>
    input[data-testid="stTextInput"] {
        display: none !important;
    }
    label[for="js_message"] {
        display: none !important;
    }
    #selectedDatesText, #resultContainer {
        white-space: normal !important;
        word-break: break-word !important;
    }
    </style>
    """, unsafe_allow_html=True)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")
    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")

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
            <div class="day{is_selected}" data-date="{date.strftime("%Y-%m-%d")}" onclick="toggleDate(this)">{day_num}</div>
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
    </style>
    <script>
    const CALENDAR_DATES = {calendar_dates_json};
    const FOURTEEN_DAYS_START = "{fourteen_days_prior_start}";
    const FOURTEEN_DAYS_END = "{fourteen_days_prior_end}";

    function saveToLocalStorage(data) {{
        localStorage.setItem('selectedDates', JSON.stringify(data));
        window.parent.postMessage(JSON.stringify(data), '*');
    }}

    function calculateAndDisplayResult(selected) {{
        const totalDays = CALENDAR_DATES.length;
        const threshold = totalDays / 3;
        const workedDays = selected.length;

        const fourteenDays = CALENDAR_DATES.filter(date => 
            date >= FOURTEEN_DAYS_START && date <= FOURTEEN_DAYS_END
        );
        const hasWorkIn14Days = fourteenDays.some(date => selected.includes(date));

        let condition1Text = workedDays < threshold 
            ? '✅ 조건 1 충족: 근무일 수가 기준 미만입니다.'
            : '❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.';

        let condition2Text = !hasWorkIn14Days
            ? `✅ 조건 2 충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}} ~ ${{FOURTEEN_DAYS_END}}) 무근무`
            : `❌ 조건 2 불충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}} ~ ${{FOURTEEN_DAYS_END}}) 근무기록이 존재`;


        let nextPossible = "";
        if (hasWorkIn14Days) {{
            const nextAvailableDate = new Date(FOURTEEN_DAYS_END);
            nextAvailableDate.setDate(nextAvailableDate.getDate() + 15);
            const nextDateStr = nextAvailableDate.toISOString().split('T')[0];
            nextPossible = `📅 조건 2를 충족하려면 ${nextDateStr} 이후에 신청하면 조건 2를 충족할 수 있습니다.`;
        }}

        let generalResult = workedDays < threshold 
            ? '✅ 일반일용근로자: 신청 가능'
            : '❌ 일반일용근로자: 신청 불가능';

        let constructionResult = (workedDays < threshold && !hasWorkIn14Days)
            ? '✅ 건설일용근로자: 신청 가능'
            : '❌ 건설일용근로자: 신청 불가능';

        const resultHtml = [
            '<h3>조건</h3>',
            '<p>' + condition1Text + '</p>',
            '<p>' + condition2Text + '</p>',
            nextPossible ? '<p>' + nextPossible + '</p>' : '',
            '<h3>📌 최종 판단</h3>',
            '<p>' + generalResult + '</p>',
            `<p>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(${CALENDAR_DATES[0]} ~ ${CALENDAR_DATES[CALENDAR_DATES.length - 1]}) 근로일 수의 합이 같은 기간 총 일수의 3분의 1 미만</p>`,
            '<p>' + constructionResult + '</p>'
        ].join('');
        document.getElementById('resultContainer').innerHTML = resultHtml;
    }}

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

    st.components.v1.html(calendar_html, height=1500, scrolling=False)


