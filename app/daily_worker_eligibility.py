# app/daily_worker_eligibility.py

import streamlit as st
from datetime import datetime, timedelta
import json

from .eligibility_logic import check_conditions  # 핵심: 상대경로로 불러오기

def daily_worker_eligibility_app():
    st.markdown("<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>", unsafe_allow_html=True)

    # 세션 상태
    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []

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
        ym = date.strftime("%Y-%m")
        calendar_groups.setdefault(ym, []).append(date)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])
    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # 숨김 CSS
    st.markdown("""
    <style>
    input[data-testid="stTextInput"] { display: none !important; }
    label[for="js_message"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    calendar_html = '<div id="calendar-container">'
    for ym, dates in calendar_groups.items():
        year, month = ym.split("-")
        calendar_html += f"<h4>{year}년 {month}월</h4><div class='calendar'>"
        calendar_html += "".join('<div class="day-header">{}</div>'.format(d) for d in "일월화수목금토")
        offset = (dates[0].weekday() + 1) % 7
        calendar_html += '<div class="empty-day"></div>' * offset

        for date in dates:
            day_num = date.day
            date_str = date.strftime("%m/%d")
            calendar_html += f'<div class="day" data-date="{date_str}" onclick="toggleDate(this)">{day_num}</div>'
        calendar_html += "</div>"
    calendar_html += "</div><p id='selectedDatesText'></p><div id='resultContainer'></div>"

    # CSS + JS
    calendar_html += f"""
    <style>
    .calendar {{
        display: grid; grid-template-columns: repeat(7, 40px); grid-gap: 5px;
    }}
    .day-header, .empty-day {{
        width: 40px; height: 40px; line-height: 40px; text-align: center;
    }}
    .day {{ width: 40px; height: 40px; line-height: 40px; text-align: center;
        border: 1px solid #ddd; border-radius: 5px; cursor: pointer; }}
    .day.selected {{ background: #2196F3; color: white; }}
    </style>

    <script>
    const CALENDAR_DATES = {calendar_dates_json};
    const FOURTEEN_DAYS_START = "{fourteen_days_prior_start}";
    const FOURTEEN_DAYS_END = "{fourteen_days_prior_end}";

    function toggleDate(el) {{
        el.classList.toggle('selected');
        const selected = Array.from(document.getElementsByClassName('day'))
            .filter(d => d.classList.contains('selected'))
            .map(d => d.getAttribute('data-date'));
        localStorage.setItem('selectedDates', JSON.stringify(selected));
        document.getElementById('selectedDatesText').innerText = "선택한 날짜: " + selected.join(', ');

        const total = CALENDAR_DATES.length;
        const worked = selected.length;

        const fourteen = CALENDAR_DATES.filter(date => date >= FOURTEEN_DAYS_START && date <= FOURTEEN_DAYS_END);
        const fourteen_worked = fourteen.filter(date => selected.includes(date.substring(5).replace('-', '/'))).length;

        const results = {check_conditions.__name__}(
            total, worked, fourteen_worked
        );

        console.log('조건 판단 결과:', results);  // JS에선 불러올 수 없음 → JS로 다시 계산해야 함
    }}
    </script>
    """

    st.components.v1.html(calendar_html, height=1000, scrolling=False)

