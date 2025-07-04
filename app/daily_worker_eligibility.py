# app/daily_worker_eligibility.py

import streamlit as st
from datetime import datetime, timedelta
import json

def daily_worker_eligibility_app():
    st.markdown(
        "<span style='font-size:22px; font-weight:600;'>🏗️ 일용직 신청 가능 시점 판단</span>",
        unsafe_allow_html=True
    )

    # 세션 상태
    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []

    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    # 캘린더 날짜 계산
    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date
    cal_dates = []
    current_date = first_day_prev_month
    while current_date <= last_day:
        cal_dates.append(current_date)
        current_date += timedelta(days=1)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])

    fourteen_days_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")
    fourteen_days_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    next_possible_date = (input_date + timedelta(days=14)).strftime("%Y-%m-%d")

    # 캘린더 그룹핑
    calendar_groups = {}
    for date in cal_dates:
        ym = date.strftime("%Y-%m")
        if ym not in calendar_groups:
            calendar_groups[ym] = []
        calendar_groups[ym].append(date)

    # CSS 숨김
    st.markdown("""
    <style>
    input[data-testid="stTextInput"] { display: none !important; }
    label[for="js_message"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # HTML + JS
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
        first_day = dates[0]
        start_offset = (first_day.weekday() + 1) % 7
        for _ in range(start_offset):
            calendar_html += '<div class="empty-day"></div>'
        for d in dates:
            day_num = d.day
            date_str = d.strftime("%m/%d")
            calendar_html += f'<div class="day" data-date="{date_str}" onclick="toggleDate(this)">{day_num}</div>'
        calendar_html += "</div>"

    calendar_html += """
    </div>
    <p id="selectedDatesText"></p>
    <div id="resultContainer"></div>

    <style>
    .calendar { display: grid; grid-template-columns: repeat(7, 40px); grid-gap: 5px; margin-bottom: 20px; }
    .day-header, .empty-day { width: 40px; height: 40px; line-height: 40px; text-align: center; font-weight: bold; }
    .day { width: 40px; height: 40px; line-height: 40px; text-align: center; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; user-select: none; }
    .day:hover { background: #f0f0f0; }
    .day.selected { background: #2196F3; color: white; font-weight: bold; border: 2px solid #2196F3; }
    #resultContainer { margin-top: 20px; padding: 15px; background: #f9f9f9; border-radius: 8px; font-size: 1em; overflow: visible; }
    </style>

    <script>
    const CALENDAR_DATES = {calendar_dates};
    const FOURTEEN_DAYS_START = '{fds}';
    const FOURTEEN_DAYS_END = '{fde}';
    const NEXT_POSSIBLE = '{npd}';

    function saveSelected(selected) {
        window.parent.postMessage(JSON.stringify(selected), '*');
    }

    function calculateAndDisplayResult(selected) {
        const totalDays = CALENDAR_DATES.length;
        const threshold = totalDays / 3;
        const workedDays = selected.length;

        const fourteenDays = CALENDAR_DATES.filter(d => d >= FOURTEEN_DAYS_START && d <= FOURTEEN_DAYS_END);
        const noWork14Days = fourteenDays.every(fd => !selected.includes(fd.substring(5).replace("-", "/")));

        const cond1 = workedDays < threshold;
        const cond2 = noWork14Days;

        const cond1Txt = cond1
            ? `✅ 조건 1 충족: 근무일 수가 기준 미만입니다.`
            : `❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.`;

        const cond2Txt = cond2
            ? `✅ 조건 2 충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}} ~ ${{FOURTEEN_DAYS_END}}) 무근무`
            : `❌ 조건 2 불충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}} ~ ${{FOURTEEN_DAYS_END}}) 내 근무기록이 존재합니다.`;

        const cond2Next = !cond2
            ? `📅 조건 2를 충족하려면 오늘 이후에 근로제공이 없는 경우 ${NEXT_POSSIBLE} 이후에 신청하면 조건 2를 충족할 수 있습니다.`
            : '';

        const cond1Next = !cond1
            ? `📅 조건 1을 충족하려면 근무일 수가 1/3 기준 이하로 줄어드는 시점에 신청해야 합니다.`
            : '';

        const resultGeneral = cond1 ? '✅ 일반일용근로자: 신청 가능' : '❌ 일반일용근로자: 신청 불가능';
        const resultConstruction = (cond1 || cond2) ? '✅ 건설일용근로자: 신청 가능' : '❌ 건설일용근로자: 신청 불가능';

        const html = [
            `<p>총 기간 일수: ${totalDays}일</p>`,
            `<p>1/3 기준: ${threshold.toFixed(1)}일</p>`,
            `<p>근무일 수: ${workedDays}일</p>`,
            `<p>${cond1Txt}</p>`,
            `<p>${cond2Txt}</p>`,
            cond1Next ? `<p>${cond1Next}</p>` : '',
            cond2Next ? `<p>${cond2Next}</p>` : '',
            `<h3>📌 최종 판단</h3>`,
            `<p>${resultGeneral}</p>`,
            `<p>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지(${CALENDAR_DATES[0]} ~ ${CALENDAR_DATES[CALENDAR_DATES.length - 1]}) 근로일 수의 합이 같은 기간 총 일수의 3분의 1 미만</p>`,
            `<p>${resultConstruction}</p>`,
            cond2Txt.includes('무근무') ? '' : `<p>신청일 직전 14일간 근무내역이 있습니다.</p>`
        ].join('');

        document.getElementById('resultContainer').innerHTML = html;
    }

    function toggleDate(el) {
        el.classList.toggle('selected');
        const selected = [];
        document.querySelectorAll('.day.selected').forEach(e => selected.push(e.getAttribute('data-date')));
        saveSelected(selected);
        calculateAndDisplayResult(selected);
        document.getElementById('selectedDatesText').innerText = `선택한 날짜: ${selected.join(', ')} (${selected.length}일)`;
    }

    window.onload = function() {
        calculateAndDisplayResult([]);
    }
    </script>
    """.format(
        calendar_dates=calendar_dates_json,
        fds=fourteen_days_start,
        fde=fourteen_days_end,
        npd=next_possible_date
    )

    st.components.v1.html(calendar_html, height=1500, scrolling=True)
