import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import pytz

calendar.setfirstweekday(calendar.SUNDAY)
KST = pytz.timezone('Asia/Seoul')

# ✅ ✅ ✅ CSS 직접 내장
st.markdown("""
<style>
/* 👉 그리드 달력 컨테이너 */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 0px !important;
    box-sizing: border-box !important;
    justify-content: flex-start !important;
}

div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    text-align: left !important;
    position: relative !important;
}

div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
    justify-content: flex-start !important;
}

.day-header {
    text-align: center !important;
    font-weight: bold !important;
    width: 40px !important;
    height: 40px !important;
    line-height: 40px !important;
    border: 1px solid #ccc !important;
    border-radius: 50% !important;
    background: #f8f8f8 !important;
}

.day-header.sunday { color: red !important; }
.day-header.saturday { color: blue !important; }

.day {
    text-align: center !important;
    width: 40px !important;
    height: 40px !important;
    line-height: 40px !important;
    border: 1px solid #ccc !important;
    border-radius: 50% !important;
    margin: 0 !important;
    background: #fff !important;
    cursor: pointer !important;
    transition: transform 0.2s, background 0.2s, border 0.2s !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.day:hover { background: #eee !important; }
.day.selected { border: 2px solid #4444ff !important; background: #e6e6ff !important; }
.day.sunday { color: red !important; }
.day.saturday { color: blue !important; }

.result-text {
    margin: 10px 0 !important;
    padding: 10px !important;
    border-left: 4px solid #36A2EB !important;
    background: #f9f9f9 !important;
}

@media (prefers-color-scheme: dark) {
    .day-header { color: #ddd !important; background: #444 !important; }
    .day { background: #333 !important; color: #ddd !important; }
    .result-text { background: #2a2a2a !important; }
}
</style>
""", unsafe_allow_html=True)

# 🔽 utils
def get_date_range(apply_date):
    start_of_apply_month = apply_date.replace(day=1)
    start_date = (start_of_apply_month - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now(KST).date()
    start_of_prev_month = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_of_prev_month, end=apply_date)))

    for year, month in months:
        st.markdown(f"### {year}년 {month}월")
        cal = calendar.monthcalendar(year, month)
        day_headers = ["일", "월", "화", "수", "목", "금", "토"]
        cols = st.columns(7)
        for i, day_name in enumerate(day_headers):
            with cols[i]:
                cls = "day-header"
                if i == 0: cls += " sunday"
                elif i == 6: cls += " saturday"
                st.markdown(f'<div class="{cls}">{day_name}</div>', unsafe_allow_html=True)

        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.empty()
                        continue
                    date_obj = date(year, month, day)
                    is_selected = date_obj in selected_dates
                    is_disabled = date_obj > apply_date
                    cls = "day"
                    if is_selected: cls += " selected"
                    if i == 0: cls += " sunday"
                    elif i == 6: cls += " saturday"

                    key = f"date_{date_obj}"
                    checked = st.checkbox("", value=is_selected, key=key, label_visibility="hidden", disabled=is_disabled)
                    st.markdown(f'<div class="{cls}">{day}</div>', unsafe_allow_html=True)
                    if not is_disabled and checked != is_selected:
                        if checked: selected_dates.add(date_obj)
                        else: selected_dates.discard(date_obj)
                        st.session_state.selected_dates = selected_dates
                        st.rerun()

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%m/%d") for d in sorted(selected_dates)]))

    return selected_dates

# 🔽 main app
def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")

    now = datetime.now(KST)
    st.markdown(f"**오늘 날짜와 시간**: {now.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')}")

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1:** 신청일 직전 달 초일부터 신청일까지 근무일이 총일의 1/3 미만이어야 함")
    st.markdown("- **조건 2 (건설일용):** 신청일 직전 14일간 근무 사실 없어야 함 (신청일 제외)")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", now.date())
    days, start_date = get_date_range(apply_date)
    selected_dates = render_calendar(apply_date)

    total_days = len(days)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준(1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일: **{worked_days}일**")

    cond1 = worked_days < threshold
    st.markdown(f'<div class="result-text">{ "✅ 조건 1 충족" if cond1 else "❌ 조건 1 불충족" }</div>', unsafe_allow_html=True)

    end14 = apply_date - timedelta(days=1)
    start14 = end14 - timedelta(days=13)
    days14 = [d for d in pd.date_range(start=start14, end=end14)]
    cond2 = all(d.date() not in selected_dates for d in days14)

    st.markdown(f'<div class="result-text">{ "✅ 조건 2 충족" if cond2 else "❌ 조건 2 불충족" } ({start14} ~ {end14})</div>', unsafe_allow_html=True)

    st.subheader("📌 최종 판단")
    st.markdown(f'<div class="result-text">{ "✅ 일반일용근로자: 신청 가능" if cond1 else "❌ 일반일용근로자: 신청 불가" }</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-text">{ "✅ 건설일용근로자: 신청 가능" if cond1 and cond2 else "❌ 건설일용근로자: 신청 불가" }</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    daily_worker_eligibility_app()


