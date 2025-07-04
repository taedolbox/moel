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

    # 한국표준시 현재 날짜
    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    # 달력 날짜 생성
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
        if ym not in calendar_groups:
            calendar_groups[ym] = []
        calendar_groups[ym].append(date)

    calendar_dates_json = json.dumps([d.strftime("%Y-%m-%d") for d in cal_dates])
    fourteen_days_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")
    fourteen_days_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")

    calendar_html = """
    <div id="calendar-container">
    """

    for ym, dates in calendar_groups.items():
        y, m = ym.split("-")
        calendar_html += f"""
        <h4>{y}년 {m}월</h4>
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
            date_str = date.strftime("%Y-%m-%d")
            calendar_html += f'<div class="day" data-date="{date_str}" onclick="toggleDate(this)">{day_num}</div>'
        calendar_html += "</div>"

    calendar_html += """
    </div>
    <p id="selectedDatesText"></p>
    <div id="resultContainer"></div>

    <style>
    .calendar {{
        display: grid;
        grid-template-columns: repeat(7, 40px);
        grid-gap: 5px;
        margin-bottom: 20px;
    }}
    .day-header, .empty-day {{
        width: 40px; height: 40px; line-height: 40px;
        text-align: center; font-weight: bold; color: #555;
    }}
    .day-header {{ background: #e0e0e0; border-radius: 5px; }}
    .empty-day {{ background: transparent; }}
    .day {{
        width: 40px; height: 40px; line-height: 40px; text-align: center;
        border: 1px solid #ddd; border-radius: 5px; cursor: pointer;
    }}
    .day:hover {{ background: #f0f0f0; }}
    .day.selected {{ border: 2px solid #2196F3; background: #2196F3; color: #fff; }}
    #resultContainer {{ margin-top:20px; padding:15px; background:#f9f9f9; border-radius:8px; }}
    </style>

    <script>
    const CALENDAR_DATES = JSON.parse('{calendar_dates}');
    const FOURTEEN_DAYS_START = '{fds}';
    const FOURTEEN_DAYS_END = '{fde}';

    function toggleDate(el) {{
        el.classList.toggle('selected');
        updateResult();
    }}

    function updateResult() {{
        const selected = [];
        document.querySelectorAll('.day.selected').forEach(el => selected.push(el.dataset.date));

        const totalDays = CALENDAR_DATES.length;
        const threshold = totalDays / 3;
        const workedDays = selected.length;

        const fourteen = CALENDAR_DATES.filter(d => d >= FOURTEEN_DAYS_START && d <= FOURTEEN_DAYS_END);
        const noWork14 = fourteen.every(d => !selected.includes(d));

        let cond1 = workedDays < threshold;
        let cond2 = noWork14;

        let cond1Text = cond1 ? '✅ 조건 1 충족: 근무일 수 기준 미만' : '❌ 조건 1 불충족: 근무일 수 기준 이상';
        let cond2Text = cond2 ? `✅ 조건 2 충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}}~${{FOURTEEN_DAYS_END}}) 무근무`
                              : `❌ 조건 2 불충족: 신청일 직전 14일간(${{FOURTEEN_DAYS_START}}~${{FOURTEEN_DAYS_END}}) 근무 내역 있음`;

        let cond1Next = '';
        let cond2Next = '';
        if (!cond1) {{
            const nextDate = new Date(CALENDAR_DATES[0]);
            nextDate.setDate(nextDate.getDate() + Math.ceil(threshold - workedDays) + 1);
            cond1Next = `📅 조건 1을 충족하려면 오늘 이후에 근로제공이 없는 경우 ${{nextDate.toISOString().slice(0,10)}} 이후에 신청하면 조건 1을 충족할 수 있습니다.`;
        }}
        if (!cond2) {{
            const nextDate2 = new Date(FOURTEEN_DAYS_END);
            nextDate2.setDate(nextDate2.getDate() + 15);
            cond2Next = `📅 조건 2를 충족하려면 오늘 이후에 근로제공이 없는 경우 ${{nextDate2.toISOString().slice(0,10)}} 이후에 신청하면 조건 2를 충족할 수 있습니다.`;
        }}

        let resultHTML = `
            <p>총 기간 일수: ${{totalDays}}일</p>
            <p>1/3 기준: ${{threshold.toFixed(1)}}일</p>
            <p>근무일 수: ${{workedDays}}일</p>
            <p>${{cond1Text}}</p>
            ${cond1Next ? '<p>' + cond1Next + '</p>' : ''}
            <p>${{cond2Text}}</p>
            ${cond2Next ? '<p>' + cond2Next + '</p>' : ''}
            <h3>📌 최종 판단</h3>
            <p>✅ 일반일용근로자: ${{cond1 ? '신청 가능' : '신청 불가능'}}</p>
            <p>✅ 건설일용근로자: ${{(cond1 && cond2) ? '신청 가능' : '신청 불가능'}}</p>
        `;
        document.getElementById('resultContainer').innerHTML = resultHTML;
        document.getElementById('selectedDatesText').innerText = "선택한 날짜: " + selected.join(', ');
    }}

    window.onload = updateResult;
    </script>
    """.format(
        calendar_dates=calendar_dates_json,
        fds=fourteen_days_start,
        fde=fourteen_days_end
    )

    st.components.v1.html(calendar_html, height=1600, scrolling=False)
