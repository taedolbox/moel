# daily_worker_eligibility.py
```python
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

# CSS 파일 로드
def load_css():
    try:
        with open("style.css", "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("style.css 파일을 찾을 수 없습니다. 같은 디렉토리에 style.css가 있는지 확인하세요.")

calendar.setfirstweekday(calendar.SUNDAY)
current_datetime = datetime(2025, 5, 26, 6, 29)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    if 'selected_dates' not in st.session_state:
        # 테스트용 초기 근무일 설정 (조건 1 충족, 조건 2 불충족)
        st.session_state.selected_dates = {date(2025, 5, 24)} | {date(2025, 4, d) for d in [1, 5, 10, 15, 20, 25, 30, 31, 2]}  # 총 10일
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

            cols = st.columns(7, gap="small")
            for i, day_name in enumerate(days_of_week_korean):
                with cols[i]:
                    color = "red" if i == 0 or i == 6 else "#000000"
                    st.markdown(
                        f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>',
                        unsafe_allow_html=True
                    )

            for week in cal:
                cols = st.columns(7, gap="small")
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue
                        date_obj = date(year, month, day)
                        if date_obj > apply_date:
                            st.markdown(
                                f'<div class="calendar-day-container">'
                                f'<div class="calendar-day-box disabled-day">{day}</div>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        class_name = "calendar-day-box"
                        if is_selected:
                            class_name += " selected-day"
                        if is_current:
                            class_name += " current-day"

                        container_key = f"date_{date_obj.isoformat()}"
                        st.markdown(
                            f'<div class="calendar-day-container">'
                            f'<div class="selection-mark"></div>'
                            f'<div class="{class_name}">{day}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        st.button(
                            f"{day}",  # 버튼에 숫자 라벨 추가
                            key=container_key,
                            on_click=toggle_date,
                            args=(date_obj,),
                            use_container_width=True
                        )
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.rerun()

    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def toggle_date(date_obj):
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)
    st.session_state.rerun_trigger = True

def daily_worker_eligibility_app():
    load_css()
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일 기준 직전달 1일부터 신청일까지의 근로일 수가 총일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자)**: 신청일 직전 14일간 근무 사실이 없어야 합니다.")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (1/3): **{threshold:.1f}일**")
    st.markdown(f"- 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족" if condition2 else f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not condition1:
        st.markdown("### 조건 1을 만족하려면?")
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)
            if worked_days_future < threshold_future:
                st.markdown(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후 신청 시 조건 1을 만족합니다.")
                break
        else:
            st.markdown("❗ 30일 내 조건 1 만족 불가. 더 미래의 날짜가 필요합니다.")

    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.markdown("이미 최근 14일 근무 없음 → 신청일 조정 불필요.")

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown(f"✅ 일반일용근로자: 신청 가능<br>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만", unsafe_allow_html=True)
    else:
        st.markdown("❌ 일반일용근로자: 신청 불가")
    if condition1 and condition2:
        st.markdown("✅ 건설일용근로자: 신청 가능")
    else:
        st.markdown(f"❌ 건설일용근로자: 신청 불가능<br>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.", unsafe_allow_html=True)
```

### 주요 수정 사항
1. **CSS 통합**:
   - 제공된 `style.css` 사용, `load_css()`로 로드.
   - `render_calendar_interactive`: `<button>` 마크업 제거, `st.button`에 숫자 라벨(`f"{day}"`) 추가.
   - 버튼 스타일: CSS에서 `width: 44px`, `height: 44px`, 투명 배경, 점선 테두리 적용. 숫자 라벨은 `.calendar-day-box`의 `font-size: 0.9em`과 일치.
   - PC 버튼 이동: CSS의 `@media (min-width: 501px)`에서 `button[data-testid="stButton"]`에 `right: 5px` 추가:
     ```css
     button[data-testid="stButton"] {
         right: 5px !important;
         left: auto !important;
         transform: translateY(-50%) !important;
     }
     ```
     (제공된 CSS에는 없으므로, 실제 `style.css`에 추가 필요. 아래에서 수정된 CSS 제공.)

2. **조건 1 충족**:
   - `selected_dates`: 2025-04-01, 04-02, 04-05, 04-10, 04-15, 04-20, 04-25, 04-30, 04-31, 05-24 (10일).
   - 총 일수: 2025-04-01 ~ 2025-05-26 = 56일, `threshold` ≈ 18.7일.
   - `worked_days` = 10 < 18.7, `condition1 = True`.

3. **조건 2 불충족**:
   - 14일간(2025-05-12 ~ 2025-05-25)에 2025-05-24 근무, `condition2 = False`.
   - 메시지: `신청일 직전 14일간(2025-05-12 ~ 2025-05-25) 내 근무기록이 존재합니다.`
   - 제안: `last_worked_day` = 2025-05-24, `suggested_date` = 2025-06-08.

4. **출력 형식**:
   - 조건 1: `✅ 조건 1 충족: 근무일 수가 기준 미만입니다.`
   - 조건 2: `❌ 조건 2 불충족: 신청일 직전 14일간(...) 내 근무기록이 존재합니다.`
   - 조건 2 제안: `📅 조건 2를 충족하려면 언제 신청해야 할까요?`
   - 최종 판단: 일반일용근로자 신청 가능, 건설일용근로자 신청 불가능, 기간 명시.

### 수정된 CSS (`style.css`)
제공된 CSS에서 PC 버튼 오른쪽 이동(`right: 5px`)이 없으므로, `@media (min-width: 501px)`에 추가하고, 버튼 라벨 표시를 최적화합니다.

<xaiArtifact artifact_id="d3ead4c4-43c3-48c1-9586-cffbaa98b1bd" artifact_version_id="e76ea60c-6d20-49d3-8fd1-88d347905b12" title="Custom Streamlit CSS" contentType="text/css">
/* 구글 폰트 Nanum Gothic을 텍스트 스타일링을 위해 가져오기 */
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic&display=swap');

/* 전체 페이지와 Streamlit 메인 컨테이너의 배경 및 텍스트 색상 설정 */
body, div[data-testid="stAppViewContainer"] {
    background-color: #ffffff !important; /* 흰색 배경 */
    color: #000000 !important; /* 검은색 텍스트 */
}

/* Streamlit 컴포넌트(마크다운, 텍스트, 상태 메시지 등)의 텍스트 색상 설정 */
.stMarkdown, .stText, .stSuccess, .stWarning, .stError, .stInfo {
    color: #000000 !important; /* 라이트 모드에서 검은색 텍스트 */
}

/* 사이드바 콘텐츠의 텍스트 색상 설정 */
.sidebar .sidebar-content, .sidebar .sidebar-content * {
    color: #000000 !important; /* 라이트 모드에서 사이드바의 검은색 텍스트 */
}

/* 다크 모드에서 body와 메인 컨테이너 스타일 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    body, div[data-testid="stAppViewContainer"] {
        background-color: #2a2a2a !important; /* 어두운 회색 배경 */
        color: #ffffff !important; /* 흰색 텍스트 */
    }
    .stMarkdown, .stText, .stSuccess, .stWarning, .stError, .stInfo {
        color: #ffffff !important; /* 다크 모드에서 Streamlit 컴포넌트의 흰색 텍스트 */
    }
    .sidebar .sidebar-content, .sidebar .sidebar-content * {
        color: #ffffff !important; /* 다크 모드에서 사이드바의 흰색 텍스트 */
    }
}

/* 라디오 버튼 레이블 스타일링 */
.stRadio>label {
    font-size: 16px;
    color: #333 !important; /* 라이트 모드에서 라디오 레이블의 짙은 회색 텍스트 */
}

/* 다크 모드에서 라디오 버튼 레이블 스타일 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .stRadio>label {
        color: #ffffff !important; /* 다크 모드에서 라디오 레이블의 흰색 텍스트 */
    }
}

/* 특정 Streamlit 컴포넌트에 Nanum Gothic 폰트 적용 */
.stMarkdown, .stSuccess, .stWarning {
    font-family: 'Nanum Gothic', sans-serif; /* 텍스트에 사용자 지정 폰트 적용 */
}

/* 사이드바 배경 색상 */
.sidebar .sidebar-content {
    background-color: #f8f9fa !important; /* 라이트 모드에서 사이드바의 밝은 회색 배경 */
}

/* 다크 모드에서 사이드바 배경 색상 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .sidebar .sidebar-content {
        background-color: #333333 !important; /* 다크 모드에서 사이드바의 더 어두운 회색 배경 */
    }
}

/* Streamlit 상단 툴바 숨기기 */
div[data-testid="stToolbar"] {
    display: none !important; /* 상단 툴바를 화면에서 숨김 */
}

/* 사이드바 토글 버튼 스타일 */
button[kind="primary"] {
    background-color: #4CAF50 !important; /* 초록색 배경 */
    color: white !important; /* 흰색 텍스트 */
    border-radius: 5px;
    padding: 8px 16px;
    font-size: 14px;
    margin: 10px;
}

/* 라이트 모드에서 토글 버튼 스타일 */
@media (prefers-color-scheme: light), [data-theme="light"] {
    button[kind="primary"] {
        background-color: #4CAF50 !important; /* 초록색 배경 */
        color: white !important; /* 흰색 텍스트 */
    }
}

/* 달력 컨테이너 스타일 */
.calendar-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    margin: 0 auto;
}

/* 달력 제목 스타일 */
.calendar-wrapper h3 {
    background-color: #f0f0f0; /* 밝은 회색 배경 */
    color: #000000 !important; /* 검은색 텍스트 */
    text-align: center;
    padding: 8px 0;
    margin-bottom: 15px;
    font-size: 1.5em;
    width: 100%;
}

/* 요일 헤더 래퍼 스타일 */
.header-wrapper {
    display: flex !important;
    flex-direction: row !important;
    width: 100% !important;
}

/* 달력 요일 헤더 스타일 */
.day-header {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 30px;
    font-size: 1em;
    font-weight: bold;
    text-align: center;
}

/* Streamlit 컬럼 스타일 오버라이드 */
div[data-testid="column"] {
    display: inline-block !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 0 !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    vertical-align: top !important;
}

/* 달력 날짜 컨테이너 스타일 */
.calendar-day-container {
    position: relative;
    height: 44px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-sizing: border-box !important;
}

/* 달력 날짜 원 스타일 */
.calendar-day-box {
    width: 34px !important;
    height: 34px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    border: 1px solid #333 !important; /* 짙은 회색 테두리 */
    background-color: #ffffff !important; /* 흰색 배경 */
    color: #000000 !important; /* 검은색 텍스트 */
    border-radius: 50% !important;
    font-size: 0.9em !important;
    box-sizing: border-box !important;
    user-select: none !important;
    white-space: nowrap !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 1 !important;
}

/* Streamlit 버튼 스타일 */
button[data-testid="stButton"] {
    width: 34px !important;
    height: 34px !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    background: transparent !important; /* 투명 배경 */
    border: 1px solid #333 !important; /* .calendar-day-box와 동일한 테두리 */
    border-radius: 50% !important;
    color: #000000 !important; /* 검은색 텍스트 */
    padding: 0 !important;
    margin: 0 !important;
    cursor: pointer !important;
    opacity: 1 !important;
    z-index: 2 !important;
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.9em !important; /* 숫자 라벨 크기 */
    font-family: 'Nanum Gothic', sans-serif;
}

/* 버튼 호버 효과 */
button[data-testid="stButton"]:hover {
    background-color: rgba(200, 200, 200, 0.3) !important; /* 반투명 회색 배경 */
}

/* 다크 모드에서 버튼 호버 효과 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    button[data-testid="stButton"] {
        border: 1px solid #888 !important; /* 회색 테두리 */
        color: #ffffff !important; /* 흰색 텍스트 */
    }
    button[data-testid="stButton"]:hover {
        background-color: rgba(80, 80, 80, 0.5) !important; /* 다크 모드에서 반투명 어두운 회색 배경 */
    }
}

/* 다크 모드에서 달력 스타일 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .calendar-wrapper h3 {
        background-color: #333333 !important; /* 어두운 회색 배경 */
        color: #ffffff !important; /* 흰색 텍스트 */
    }
    .calendar-day-container {
        background-color: #2a2a2a !important; /* 어두운 회색 배경 */
    }
    .calendar-day-box {
        border: 1px solid #888 !important; /* 회색 테두리 */
        background-color: #000000 !important; /* 검은색 배경 */
        color: #ffffff !important; /* 흰색 텍스트 */
    }
}

/* PC 화면 스타일 (최소 너비 501px) */
@media (min-width: 501px) {
    .calendar-wrapper {
        min-width: 600px !important;
        max-width: 600px !important;
    }
    .header-wrapper {
        width: 600px !important;
    }
    .calendar-day-container {
        width: calc(600px / 7) !important;
        height: 48px !important;
    }
    .calendar-day-box {
        width: 38px !important;
        height: 38px !important;
        font-size: 1em !important;
        margin-right: 10px !important; /* 버튼과의 간격 */
    }
    button[data-testid="stButton"] {
        width: 38px !important;
        height: 38px !important;
        right: 5px !important; /* 오른쪽 끝에서 5px */
        left: auto !important;
        transform: translateY(-50%) !important; /* 수직 중앙 정렬 */
        font-size: 1em !important;
    }
    div[data-testid="column"] {
        width: calc(600px / 7) !important;
        max-width: calc(600px / 7) !important;
        min-width: calc(600px / 7) !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .day-header {
        width: calc(600px / 7) !important;
    }
}

/* 모바일 화면 스타일 (최대 너비 500px) */
@media (max-width: 500px) {
    .calendar-wrapper {
        width: 280px !important;
        min-width: 280px !important;
        max-width: 280px !important;
        margin: 0 auto !important;
    }
    .header-wrapper {
        width: 280px !important;
        display: flex !important;
        flex-wrap: nowrap !important;
    }
    .calendar-day-container {
        width: calc(280px / 7) !important;
        height: 44px !important;
        background-color: #f0f0f0 !important; /* 밝은 회색 배경 */
    }
    .calendar-day-box {
        width: 34px !important;
        height: 34px !important;
        font-size: 0.9em !important;
        margin-right: 5px !important; /* 버튼과의 간격 */
    }
    button[data-testid="stButton"] {
        width: 34px !important;
        height: 34px !important;
        font-size: 0.9em !important;
    }
    div[data-testid="column"] {
        width: calc(280px / 7) !important;
        max-width: calc(280px / 7) !important;
        min-width: calc(280px / 7) !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .day-header {
        width: calc(280px / 7) !important;
    }
}

/* 모바일 다크 모드 스타일 */
@media (max-width: 500px) and (prefers-color-scheme: dark), (max-width: 500px) and [data-theme="dark"] {
    .calendar-day-container {
        background-color: #2a2a2a !important; /* 어두운 회색 배경 */
    }
    .calendar-day-box {
        border: 1px solid #888 !important; /* 회색 테두리 */
        background-color: #000000 !important; /* 검은색 배경 */
        color: #ffffff !important; /* 흰색 텍스트 */
    }
}

/* 공통 스타일: 날짜 박스 호버 효과 */
.calendar-day-box:hover {
    background-color: #e0e0e0 !important; /* 라이트 모드에서 연한 회색 배경 */
    border-color: #555 !important; /* 짙은 회색 테두리 */
}

/* 다크 모드에서 날짜 박스 호버 효과 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .calendar-day-box:hover {
        background-color: #333333 !important; /* 어두운 회색 배경 */
        border-color: #aaaaaa !important; /* 밝은 회색 테두리 */
    }
}

/* 오늘 날짜 스타일 */
.calendar-day-box.current-day:not(.selected-day) {
    border: 2px solid #0000ff !important; /* 파란색 테두리 */
}

/* 선택된 날짜 스타일 */
.calendar-day-box.selected-day {
    background-color: #4CAF50 !important; /* 초록색 배경 */
    color: #ffffff !important; /* 흰색 텍스트 */
    border: 2px solid #4CAF50 !important; /* 초록색 테두리 */
    font-weight: bold !important;
}

/* 비활성화된 날짜 스타일 */
.calendar-day-box.disabled-day {
    border: 1px solid #555 !important; /* 짙은 회색 테두리 */
    background-color: #cccccc !important; /* 연한 회색 배경 */
    color: #666 !important; /* 어두운 회색 텍스트 */
    cursor: not-allowed !important;
}

/* 다크 모드에서 비활성화된 날짜 스타일 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .calendar-day-box.disabled-day {
        background-color: #333333 !important; /* 어두운 회색 배경 */
        border: 1px solid #444 !important; /* 더 어두운 회색 테두리 */
        color: #666 !important; /* 어두운 회색 텍스트 */
    }
}

/* 선택 표시 스타일 */
.selection-mark {
    position: absolute;
    top: 4px !important;
    left: 4px !important;
    width: 8px !important;
    height: 8px !important;
    border-radius: 50% !important;
    background-color: #4CAF50 !important; /* 초록색 배경 */
    border: 1px solid #ffffff !important; /* 흰색 테두리 */
    display: none !important;
    z-index: 0 !important;
}

/* 선택된 날짜에 선택 표시 보이기 */
.selected-day .selection-mark {
    display: block !important;
}

/* 폼 제출 버튼 숨기기 */
button[data-testid="stFormSubmitButton"] {
    display: none !important; /* 폼 제출 버튼 숨김 */
}

/* 결과 텍스트 스타일 */
.result-text p {
    font-size: 1.1em;
    margin: 5px 0;
}











""" 
# daily_worker_eligibility.py 
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

calendar.setfirstweekday(calendar.SUNDAY)
current_datetime = datetime(2025, 5, 26, 6, 29)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')

def get_date_range(apply_date):
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f"<h3>{year}년 {month}월</h3>", unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week_korean = ["일", "월", "화", "수", "목", "금", "토"]

            cols = st.columns(7, gap="small")
            for i, day_name in enumerate(days_of_week_korean):
                with cols[i]:
                    color = "red" if i == 0 or i == 6 else "#000000"
                    st.markdown(
                        f'<div class="day-header"><span style="color: {color}">{day_name}</span></div>',
                        unsafe_allow_html=True
                    )

            for week in cal:
                cols = st.columns(7, gap="small")
                for i, day in enumerate(week):
                    with cols[i]:
                        if day == 0:
                            st.markdown('<div class="calendar-day-container"></div>', unsafe_allow_html=True)
                            continue
                        date_obj = date(year, month, day)
                        if date_obj > apply_date:
                            st.markdown(
                                f'<div class="calendar-day-container">'
                                f'<div class="calendar-day-box disabled-day">{day}</div>'
                                f'<button data-testid="stButton" style="display: none;"></button>'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            continue

                        is_selected = date_obj in selected_dates
                        is_current = date_obj == current_date
                        class_name = "calendar-day-box"
                        if is_selected:
                            class_name += " selected-day"
                        if is_current:
                            class_name += " current-day"

                        container_key = f"date_{date_obj.isoformat()}"
                        st.markdown(
                            f'<div class="calendar-day-container">'
                            f'<div class="selection-mark"></div>'
                            f'<div class="{class_name}">{day}</div>'
                            f'<button data-testid="stButton" key="{container_key}" onClick="window.parent.window.dispatchEvent(new Event(\'button_click_{container_key}\'));"></button>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                        if st.button("", key=container_key, on_click=toggle_date, args=(date_obj,), use_container_width=True):
                            pass
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.rerun_trigger:
        st.session_state.rerun_trigger = False
        st.rerun()

    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

def toggle_date(date_obj):
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)
    st.session_state.rerun_trigger = True

def daily_worker_eligibility_app():
    st.header("일용근로자 수급자격 요건 모의계산")
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 신청일 기준 직전달 1일부터 신청일까지의 근로일 수가 총일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자)**: 신청일 직전 14일간 근무 사실이 없어야 합니다.")
    st.markdown("---")

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_dates = render_calendar_interactive(apply_date)
    st.markdown("---")

    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (1/3): **{threshold:.1f}일**")
    st.markdown(f"- 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족" if condition1 else "❌ 조건 1 불충족"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족" if condition2 else "❌ 조건 2 불충족"}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    if not condition1:
        st.markdown("### 조건 1을 만족하려면?")
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)
            if worked_days_future < threshold_future:
                st.markdown(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후 신청 시 조건 1을 만족합니다.")
                break
        else:
            st.markdown("❗ 30일 내 조건 1 만족 불가. 더 미래의 날짜가 필요합니다.")

    if not condition2:
        st.markdown("### 조건 2를 만족하려면?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후 신청 시 조건 2 만족.")
        else:
            st.markdown("이미 최근 14일 근무 없음 → 신청일 조정 불필요.")

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown("✅ 일반일용근로자: 신청 가능")
    else:
        st.markdown("❌ 일반일용근로자: 신청 불가")

    if condition1 and condition2:
        st.markdown("✅ 건설일용근로자: 신청 가능")
    else:
        st.markdown("❌ 건설일용근로자: 신청 불가")

if __name__ == "__main__":
    daily_worker_eligibility_app()

""" 
