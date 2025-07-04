import streamlit as st
from datetime import datetime, timedelta
import json

from app.eligibility_logic import check_conditions

def daily_worker_eligibility_app():
    st.markdown("<h2>🏗️ 일용직 신청 가능 시점 판단</h2>", unsafe_allow_html=True)

    # 오늘 KST 기준 날짜
    today_kst = datetime.utcnow() + timedelta(hours=9)
    input_date = st.date_input("📅 기준 날짜 선택", today_kst.date())

    # 달력 날짜 생성 (직전달 1일부터 input_date까지)
    first_day_prev_month = (input_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_day = input_date
    cal_dates = []
    current = first_day_prev_month
    while current <= last_day:
        cal_dates.append(current)
        current += timedelta(days=1)

    # 세션 상태 초기화
    if 'selected_dates_list' not in st.session_state:
        st.session_state.selected_dates_list = []

    # 달력용 날짜 문자열 리스트 (yyyy-mm-dd)
    calendar_dates_str = [d.strftime("%Y-%m-%d") for d in cal_dates]
    fourteen_days_prior_start = (input_date - timedelta(days=14)).strftime("%Y-%m-%d")
    fourteen_days_prior_end = (input_date - timedelta(days=1)).strftime("%Y-%m-%d")

    # 달력 HTML + JS 생성
    calendar_dates_mmdd = [d.strftime("%m/%d") for d in cal_dates]

    st.markdown("#### 달력에서 근무한 날짜를 클릭해 선택하세요.")

    # JS와 HTML 코드 (간단화)
    calendar_html = """
    <style>
    .calendar {display: grid; grid-template-columns: repeat(7, 40px); grid-gap: 5px; margin-bottom: 20px;}
    .day {width: 40px; height: 40px; line-height: 40px; text-align: center; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; user-select: none; font-size: 16px;}
    .day.selected {background-color: #2196F3; color: white; font-weight: bold; border: 2px solid #1976D2;}
    .day:hover {background-color: #bbdefb;}
    .day-header {font-weight: bold; text-align: center; margin-bottom: 5px;}
    </style>
    <div>
        <div class="calendar">
            <div class="day-header">일</div><div class="day-header">월</div><div class="day-header">화</div>
            <div class="day-header">수</div><div class="day-header">목</div><div class="day-header">금</div><div class="day-header">토</div>
    """

    # 달력 빈 칸 계산
    start_weekday = (cal_dates[0].weekday() + 1) % 7  # 일요일=0, 월=1 ...
    for _ in range(start_weekday):
        calendar_html += '<div></div>'

    # 날짜 div 생성
    for d in cal_dates:
        mmdd = d.strftime("%m/%d")
        selected_class = "selected" if mmdd in st.session_state.selected_dates_list else ""
        calendar_html += f'<div class="day {selected_class}" data-date="{mmdd}" onclick="toggleDate(this)">{d.day}</div>'

    calendar_html += """
        </div>
    </div>
    <script>
    const selectedDates = new Set(%s);

    function toggleDate(el) {
        const date = el.getAttribute("data-date");
        if (selectedDates.has(date)) {
            selectedDates.delete(date);
            el.classList.remove("selected");
        } else {
            selectedDates.add(date);
            el.classList.add("selected");
        }
        // 선택 날짜 갱신
        window.parent.postMessage({func: 'updateDates', dates: Array.from(selectedDates)}, "*");
    }
    </script>
    """ % json.dumps(st.session_state.selected_dates_list)

    # 달력 렌더링
    st.components.v1.html(calendar_html, height=350)

    # 선택 날짜 텍스트 출력
    st.write("선택된 날짜들 (mm/dd):", st.session_state.selected_dates_list)

    # 버튼 누르면 조건 판단 실행
    if st.button("조건 및 결과 판단하기"):
        result = check_conditions(
            st.session_state.selected_dates_list,
            calendar_dates_str,
            fourteen_days_prior_start,
            fourteen_days_prior_end
        )

        st.markdown("### 조건 결과")
        st.write(f"조건 1 (근무일 수 1/3 미만): {'✅ 충족' if result['condition1'] else '❌ 불충족'}")
        st.write(f"조건 2 (직전 14일간 무근무): {'✅ 충족' if result['condition2'] else '❌ 불충족'}")
        if result['next_possible_date']:
            st.write(f"📅 조건 2를 충족하려면 {result['next_possible_date']} 이후에 신청하세요.")

        st.markdown("### 최종 판단")
        st.write(f"✅ 일반일용근로자: {'신청 가능' if result['condition1'] else '신청 불가능'}")
        st.write(f"✅ 건설일용근로자: {'신청 가능' if result['condition1'] or result['condition2'] else '신청 불가능'}")
        st.write(f"기간: {result['calendar_start']} ~ {result['calendar_end']}")
        st.write(f"총 기간 일수: {result['total_days']}일, 1/3 기준: {result['threshold']:.1f}일, 근무일 수: {result['worked_days']}일")
        st.write(f"직전 14일 기간: {result['fourteen_days_start']} ~ {result['fourteen_days_end']}")

# 하단에 메시지 수신 및 세션 상태 업데이트 코드 필요 (Streamlit 현재 제한적)
# 별도 WebSocket 혹은 iframe postMessage 방식으로 구현 가능 (복잡도 증가)

