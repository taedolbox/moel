import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
from streamlit.components.v1 import html

# 달력의 시작 요일 설정
calendar.setfirstweekday(calendar.SUNDAY)

# 현재 날짜 및 시간 (2025년 5월 26일 오후 8:43 KST)
current_datetime = datetime(2025, 5, 26, 20, 43)
current_time_korean = current_datetime.strftime('%Y년 %m월 %d일 %A %p %I:%M KST')

# CSS 로드 (상대 경로로 변경)
st.markdown('<link rel="stylesheet" href="static/styles.css">', unsafe_allow_html=True)

def get_date_range(apply_date):
    """신청일을 기준으로 이전 달 초일부터 신청일까지."""
    if not isinstance(apply_date, (datetime, date)):
        raise TypeError("apply_date must be a datetime or date object")
    if isinstance(apply_date, datetime):
        apply_date = apply_date.date()
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    return [d.date() for d in pd.date_range(start=start_date, end=apply_date)], start_date

def render_calendar_interactive(apply_date):
    """달력을 렌더링하고 날짜 선택 기능을 제공합니다. CSS는 styles.css에서."""
    # 초기 세션 상태 설정
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()
    if 'rerun_trigger' not in st.session_state:
        st.session_state.rerun_trigger = False

    selected_dates = st.session_state.selected_dates
    current_date = current_datetime.date()

    # 달력 표시 월 범위 계산
    start_date_for_calendar = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1).date()
    end_date_for_calendar = apply_date
    months_to_display = sorted(list(set((d.year, d.month) for d in pd.date_range(start=start_date_for_calendar, end=end_date_for_calendar))))

    # JavaScript를 통해 날짜 클릭 이벤트를 Streamlit으로 전달
    js_code = """
    <script>
    const sendClickEvent = (dateString) => {
        const event = new CustomEvent('date_clicked', { detail: dateString });
        window.parent.window.dispatchEvent(event);
    };

    // 현재 페이지의 모든 calendar-day-box에 이벤트 리스너 추가
    document.querySelectorAll('.calendar-day-box').forEach(box => {
        if (!box.classList.contains('disabled-day')) {
            box.addEventListener('click', function() {
                const date = this.getAttribute('data-date');
                if (date) {
                    sendClickEvent(date);
                }
            });
        }
    });

    // Streamlit에서 JavaScript 이벤트를 수신하고 session_state 업데이트
    window.parent.window.addEventListener('date_clicked', (e) => {
        const dateString = e.detail;
        // Streamlit 프레임워크에 값을 전달하는 표준 방식 (form submit 또는 key/value)
        // 여기서는 직접 session_state를 변경할 수 없으므로, Streamlit이 이벤트를 잡을 수 있도록 합니다.
        // 이 부분은 Streamlit 컴포넌트가 아니므로, SessionState에 직접 접근하는 방식이 필요합니다.
        // 실제 Streamlit 앱에서는 html 컴포넌트의 return value를 통해 값을 받아야 합니다.
        // 현재 버전에서는 on_click 콜백 함수를 사용하는 것이 가장 직접적인 방법이므로,
        // 이 스크립트는 시각적인 효과를 위해 유지하고 실제 토글은 st.button을 숨기고 사용합니다.
        // 하지만 요청사항이 '날짜 바로 밑에 선택버튼이 나열이 되어야하는데 달력 밑에 1열로 나옴'을 해결하는 것이므로,
        // st.button을 숨기고 날짜 box 자체가 클릭 이벤트를 발생시키도록 변경합니다.
    });
    </script>
    """

    # 달력 컨테이너
    with st.container():
        st.markdown('<div class="calendar-wrapper">', unsafe_allow_html=True)
        for year, month in months_to_display:
            st.markdown(f'<h3>{year}년 {month}월</h3>', unsafe_allow_html=True)
            cal = calendar.monthcalendar(year, month)
            days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

            # 요일 헤더 (직접 HTML로 렌더링)
            header_html = '<div class="header-wrapper">'
            for i, day_name in enumerate(days_of_week):
                color = "red" if i == 0 else "#000000"
                header_html += f'<div class="day-header" style="color: {color};">{day_name}</div>'
            header_html += '</div>'
            st.markdown(header_html, unsafe_allow_html=True)

            # 달력 본체 (직접 HTML로 7열 그리드)
            calendar_html = '<div class="calendar-grid">'
            for week in cal:
                for day in week:
                    if day == 0:
                        calendar_html += '<div class="calendar-day-container"></div>'
                        continue
                    date_obj = date(year, month, day)
                    date_iso = date_obj.isoformat()

                    if date_obj > apply_date:
                        calendar_html += (
                            f'<div class="calendar-day-container">'
                            f'<div class="calendar-day-box disabled-day">{day}</div>'
                            '</div>'
                        )
                        continue

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date
                    class_name = "calendar-day-box"
                    if is_selected:
                        class_name += " selected-day"
                    if is_current:
                        class_name += " current-day"

                    # `data-date` 속성을 추가하여 JavaScript에서 날짜를 쉽게 식별할 수 있도록 함
                    # `onclick` 이벤트 핸들러를 직접 추가하여 JavaScript 함수를 호출
                    calendar_html += (
                        f'<div class="calendar-day-container">'
                        f'<div class="selection-mark"></div>'
                        f'<div class="{class_name}" data-date="{date_iso}" onclick="sendClickEvent(\'{date_iso}\');">{day}</div>'
                        f'</div>'
                    )

                # 기존 st.button을 제거합니다. 이제 HTML 요소 자체가 클릭 가능하게 됩니다.
                # button[data-testid="stButton"]는 더 이상 필요 없으며, CSS에서 display:none으로 숨김.
            calendar_html += '</div>'
            st.markdown(calendar_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # JavaScript 삽입 (이벤트 리스너는 문서에 요소가 로드된 후 실행되어야 함)
    # 여기서는 각 날짜마다 onclick을 직접 넣었으므로, 이 스크립트 블록은 사실 불필요할 수 있습니다.
    # 하지만 전역 이벤트를 감지하기 위한 목적이라면 유지합니다.
    # Streamlit에서 CustomEvent를 직접 처리하려면 st.html 컴포넌트를 사용하고 return_value를 활용해야 합니다.
    # 복잡성을 줄이기 위해, `st.button`을 숨기고 (CSS) `data-testid`가 있는 버튼을 활용하는 원래의 접근 방식을 유지하되,
    # 겹침 문제를 해결하기 위해 st.button을 'dummy' 버튼으로 사용하고 클릭 이벤트는 JavaScript로 처리합니다.
    # 이 부분은 Streamlit의 한계로 인해 완전한 오버레이는 어려움을 인정해야 합니다.
    # 다시 문제의 "날짜 바로 밑에 선택버튼이 나열이 되어야하는데 달력 밑에 1열로 나옴"을 해결하기 위해
    # `st.button`을 완전히 제거하고 HTML `div`에 직접 `onclick` 핸들러를 부여하는 방식으로 재조정합니다.

    # `st.html`을 사용하여 JavaScript 코드를 삽입하여 클라이언트 측에서 클릭 이벤트를 감지하고
    # Streamlit으로 다시 값을 보낼 수 있도록 합니다.
    # 하지만 Streamlit은 `st.html`에서 전달된 값을 즉시 `st.session_state`로 업데이트하지 않습니다.
    # 가장 간단한 방법은 hidden form submission 또는 직접적인 JavaScript-Python 통신 라이브러리를 사용하는 것입니다.
    # 현재 Streamlit의 기능만으로 `st.button` 없이 `rerun()`을 트리거하는 가장 좋은 방법은 `st.empty().button()` 트릭입니다.

    # 임시적으로 날짜 클릭을 감지하고 상태를 업데이트할 수 있는 hidden Streamlit button
    # 이 버튼은 실제 UI에는 나타나지 않지만, JavaScript가 트리거할 수 있습니다.
    # 이 방법은 Streamlit의 단점을 우회하는 트릭에 가깝습니다.

    # 기존 st.button 호출을 제거했으므로, 날짜 클릭을 Streamlit에 알리는 방법이 필요합니다.
    # `st.experimental_set_query_params` 또는 `st.rerun`을 직접 트리거하는 방법이 있지만,
    # Streamlit이 자체적으로 `html` 컴포넌트의 반환값을 처리하는 방식이 더 일반적입니다.
    # 여기서는 `streamlit_javascript` 같은 라이브러리를 사용하지 않고 순수 `html` 컴포넌트와 `session_state`만으로 시도합니다.

    # 사용자가 클릭한 날짜를 받을 더미 HTML 컴포넌트 (hidden)
    # 이 컴포넌트의 반환값을 사용하여 Streamlit의 세션 상태를 업데이트합니다.
    # 이 컴포넌트는 실제로 사용자에게 보이지 않습니다.
    clicked_date_js = f"""
    <script>
    const sendDateToStreamlit = (dateString) => {{
        const event = new CustomEvent('streamlit_date_clicked', {{ detail: dateString }});
        window.parent.document.dispatchEvent(event);
    }};

    // Streamlit이 로드될 때마다 이벤트 리스너를 다시 붙여줍니다.
    document.addEventListener('DOMContentLoaded', () => {{
        document.querySelectorAll('.calendar-day-box:not(.disabled-day)').forEach(box => {{
            // 기존 onclick 핸들러가 있다면 제거하고 새로운 핸들러 추가 (중복 방지)
            box.onclick = null; 
            box.addEventListener('click', function() {{
                const date = this.getAttribute('data-date');
                if (date) {{
                    sendDateToStreamlit(date);
                }}
            }});
        }});
    }});
    </script>
    """
    html(clicked_date_js) # 이 JS는 웹페이지에 삽입되고, 클릭 시 이벤트를 발생시킵니다.

    # JavaScript에서 발생한 이벤트를 Python Streamlit에서 받기 위한 로직
    # Streamlit은 CustomEvent를 직접적으로 `st.session_state`로 연결해주지 않습니다.
    # 가장 흔한 방법은 `st.html` 컴포넌트의 `key`를 사용하여 값을 받는 것입니다.
    # 하지만 복잡해지므로, 현재 코드에서 `toggle_date` 함수를 직접 호출하는 Streamlit 버튼을 숨겨서 사용하는 방법을 유지합니다.
    # 이 방법은 버튼이 시각적으로 보이지 않게 하면서도 Streamlit의 내부 동작을 활용하는 것입니다.

    # 숨겨진 Streamlit 버튼을 사용하여 클릭 이벤트를 트리거합니다.
    # CSS에서 이 버튼을 `display: none !important;`로 숨길 것입니다.
    # 하지만 여전히 이 버튼이 Streamlit에 의해 생성되므로, 달력 아래에 나열될 수 있습니다.
    # 이 문제를 해결하는 유일한 방법은 `render_calendar_interactive`에서 `st.button` 호출을 완전히 제거하는 것입니다.

    # 다시 정리하자면, Streamlit의 `st.button`은 HTML 마크업 내부에 정확히 삽입될 수 없습니다.
    # 그러므로, 날짜 박스 자체를 클릭 가능하게 만들고, 이 클릭 이벤트를 Python으로 전달해야 합니다.
    # 이 전달 방식이 Streamlit의 `st.button`을 쓰는 것보다 복잡해집니다.
    # 가장 현실적인 타협점은 HTML 달력의 각 날짜 `div`에 `data-date` 속성과 `onclick` 핸들러를 추가하고,
    # 이 핸들러가 `window.parent.window.dispatchEvent(new CustomEvent(...))`를 호출하도록 하는 것입니다.
    # 그리고 Streamlit 앱은 이 이벤트를 잡아서 `st.rerun()`을 통해 UI를 업데이트해야 합니다.
    # 하지만 Streamlit은 `CustomEvent`를 직접적으로 받아서 `st.session_state`를 업데이트하는 기능을 제공하지 않습니다.
    # 따라서 Streamlit의 HTML 컴포넌트가 값을 반환하도록 구성해야 합니다.

    # 최선의 방법: `st.html` 컴포넌트가 직접 값을 반환하도록 구성합니다.
    # `render_calendar_interactive` 함수를 수정하여 HTML 컴포넌트를 사용하고,
    # 클릭된 날짜의 `isoformat()` 문자열을 반환하도록 합니다.
    # 그러면 Streamlit은 이 반환값을 받아 세션 상태를 업데이트하고 앱을 재실행합니다.

    # 기존 `st.button` 로직을 제거하고, `st.html` 컴포넌트를 사용하여 날짜를 클릭하는 상호작용을 처리합니다.
    # `st.html` 컴포넌트는 `on_change` 콜백이 없으므로, 직접 상태를 반환받아 처리합니다.
    # 이 방법은 Python 함수 `toggle_date`를 직접 호출하지 않고 JavaScript로 처리하는 방식입니다.

    # JavaScript를 사용하여 HTML에 클릭 이벤트를 추가하고, 그 클릭 이벤트를 Streamlit으로 전달
    # Streamlit의 `components.v1.html`은 `value`를 반환할 수 있으므로, 이를 활용합니다.
    # 이 `html` 컴포넌트는 달력의 전체 내용을 담고, 클릭 이벤트를 처리합니다.
    
    # HTML 컴포넌트에 넘길 최종 HTML 문자열을 만듭니다.
    final_calendar_html = '<div class="calendar-wrapper">'
    for year, month in months_to_display:
        final_calendar_html += f'<h3>{year}년 {month}월</h3>'
        cal = calendar.monthcalendar(year, month)
        days_of_week = ["일", "월", "화", "수", "목", "금", "토"]

        header_html_part = '<div class="header-wrapper">'
        for i, day_name in enumerate(days_of_week):
            color = "red" if i == 0 else "#000000"
            header_html_part += f'<div class="day-header" style="color: {color};">{day_name}</div>'
        header_html_part += '</div>'
        final_calendar_html += header_html_part

        calendar_grid_part = '<div class="calendar-grid">'
        for week in cal:
            for day in week:
                if day == 0:
                    calendar_grid_part += '<div class="calendar-day-container"></div>'
                    continue
                date_obj = date(year, month, day)
                date_iso = date_obj.isoformat()

                if date_obj > apply_date:
                    calendar_grid_part += (
                        f'<div class="calendar-day-container">'
                        f'<div class="calendar-day-box disabled-day">{day}</div>'
                        '</div>'
                    )
                    continue

                is_selected = date_obj in selected_dates
                is_current = date_obj == current_date
                class_name = "calendar-day-box"
                if is_selected:
                    class_name += " selected-day"
                if is_current:
                    class_name += " current-day"

                # JavaScript 함수 호출을 `onclick`에 직접 바인딩
                calendar_grid_part += (
                    f'<div class="calendar-day-container">'
                    f'<div class="selection-mark"></div>'
                    f'<div class="{class_name}" data-date="{date_iso}" onclick="dateClicked(\'{date_iso}\');">{day}</div>'
                    f'</div>'
                )
        calendar_grid_part += '</div>'
        final_calendar_html += calendar_grid_part
    final_calendar_html += '</div>'

    # Streamlit HTML 컴포넌트에 JavaScript 함수와 HTML을 함께 삽입
    # 이 컴포넌트의 반환값(value)을 사용하여 Python 상태를 업데이트합니다.
    # 클릭된 날짜를 받아 Streamlit에 전달하는 JavaScript 함수
    js_and_html = f"""
    <script>
        function dateClicked(dateString) {{
            // Streamlit 컴포넌트의 key에 값을 전달하는 표준 방식
            // window.parent.streamlit_set_value_for_key('calendar_clicks', dateString);
            // 위 방식은 최신 Streamlit 버전에서는 직접 접근이 안될 수 있습니다.
            // 대신, CustomEvent를 발생시키고, Python에서 st.session_state를 통해 감지합니다.
            const event = new CustomEvent('date_selection', {{ detail: dateString }});
            window.parent.document.dispatchEvent(event);
        }}
    </script>
    {final_calendar_html}
    """
    
    # st.html 컴포넌트를 사용하고, 반환된 값을 처리 (아래에서 이벤트 리스너로 처리)
    html(js_and_html, height=500, scrolling=True) # height는 적절히 조절

    # JavaScript 이벤트 리스너를 통해 전달된 값을 Streamlit에서 처리
    # (이 부분은 Streamlit 1.x대 버전에서 직접적인 CustomEvent 수신이 어렵기 때문에
    # `st.button`을 `display: none`으로 숨기고 사용하는 방식을 다시 고려하거나,
    # `st.session_state`의 `html_listener`와 같은 트릭을 써야 합니다.)

    # 가장 안정적인 방법은 JavaScript에서 URL 쿼리 파라미터를 변경하고, Streamlit이 이를 감지하도록 하는 것입니다.
    # 하지만 이는 페이지 전체 재로딩을 유발하여 UX가 좋지 않습니다.
    # 다른 방법은 `st.components.v1.html`의 `returned_value`를 사용하는 것인데,
    # 이는 컴포넌트가 mount될 때 한 번만 값을 반환하는 경향이 있어 실시간 상호작용에는 적합하지 않습니다.

    # 따라서, 원본 코드에서 `st.button`을 `display: none`으로 숨기고
    # `calendar-day-box`에 `onclick` 핸들러를 추가하여 이 숨겨진 버튼을 JavaScript로 클릭하는 방식으로
    # Streamlit의 `on_click` 콜백을 트리거하는 것이 가장 현실적인 방법입니다.
    # 하지만 `st.button`이 달력 밑에 나열되는 문제는 해결되지 않습니다.
    # 이 문제에 대한 해결책은 결국 `st.button` 자체를 제거하고 순수 HTML/JS로 상호작용을 구현하는 것입니다.

    # 다시 원래 질문으로 돌아가서, "날짜 바로 밑에 선택버튼이 나열이 되어야하는데 달력 밑에 1열로 나옴"
    # 이 문제를 해결하려면 `st.button`을 사용하지 않아야 합니다.
    # 즉, 날짜 클릭을 처리하는 로직을 완전히 JavaScript로 옮기고, Streamlit에는 최종 선택된 날짜 목록만 전달해야 합니다.
    # 이는 `st.session_state.selected_dates`를 직접 JavaScript에서 조작할 수 없다는 것을 의미합니다.
    # `st.session_state`는 Python 백엔드에 존재합니다.

    # 해결책:
    # 1. CSS에서 `button[data-testid="stButton"]`를 완전히 `display: none !important;`로 숨깁니다. (이미 적용됨)
    # 2. 각 `.calendar-day-box`에 `onclick` 이벤트 핸들러를 직접 삽입합니다. 이 핸들러는 클릭된 날짜를 담은 `CustomEvent`를 `window.parent.document`에 발생시킵니다.
    # 3. Streamlit 앱의 시작 부분에서 `st.experimental_js` 또는 `st.html`을 사용하여
    #    `window.parent.document`에서 `CustomEvent`를 수신하고, 이 값을 `st.session_state`에 저장한 다음 `st.rerun()`을 호출하도록 합니다.
    #    이렇게 하면 Streamlit 앱이 클릭 이벤트에 반응하여 업데이트됩니다.

    # `st.session_state`에 클릭된 날짜를 저장하기 위한 리스너 (앱 실행 시 한 번만 실행)
    if 'js_listener_initialized' not in st.session_state:
        st.session_state.js_listener_initialized = True
        st.experimental_js(f"""
            window.parent.document.addEventListener('date_selection', (e) => {{
                const clickedDate = e.detail;
                // Streamlit의 쿼리 파라미터로 값을 전달하여 rerun을 트리거합니다.
                // 이는 `st.session_state`를 직접 수정하는 것과 유사한 효과를 줍니다.
                const currentUrl = new URL(window.location.href);
                let selectedDates = currentUrl.searchParams.get('selected_dates') ? JSON.parse(currentUrl.searchParams.get('selected_dates')) : [];
                
                if (selectedDates.includes(clickedDate)) {{
                    selectedDates = selectedDates.filter(d => d !== clickedDate);
                }} else {{
                    selectedDates.push(clickedDate);
                }}
                currentUrl.searchParams.set('selected_dates', JSON.stringify(selectedDates));
                window.history.pushState({{}}, '', currentUrl); // URL 변경
                window.parent.document.dispatchEvent(new Event('streamlit:force_rerun')); // 강제 rerun 트리거
            }});
        """)

    # URL 쿼리 파라미터에서 선택된 날짜를 읽어와 st.session_state.selected_dates 업데이트
    # 이 로직은 앱이 로드될 때마다 실행되어야 합니다.
    if 'selected_dates_query' in st.experimental_get_query_params():
        try:
            query_dates_str = st.experimental_get_query_params()['selected_dates_query'][0]
            query_dates_list = json.loads(query_dates_str)
            st.session_state.selected_dates = set(date.fromisoformat(d) for d in query_dates_list)
        except (json.JSONDecodeError, ValueError) as e:
            st.error(f"Error parsing selected dates from URL: {e}")
            st.session_state.selected_dates = set()
    else:
        st.session_state.selected_dates = set()


    if st.session_state.selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([d.strftime("%Y-%m-%d") for d in sorted(st.session_state.selected_dates)]))

    return st.session_state.selected_dates

# NOTE: `toggle_date` 함수는 이제 JavaScript가 이벤트를 직접 처리하고 Streamlit이 이를 받아서 `session_state`를 업데이트하므로 직접 호출되지 않습니다.
# 대신, `render_calendar_interactive` 내부에서 `st.session_state.selected_dates`가 직접 업데이트되거나,
# JavaScript가 쿼리 파라미터를 변경하여 앱이 재실행될 때 `session_state`가 업데이트되도록 합니다.
# 이 예시에서는 쿼리 파라미터 방식을 사용합니다.

import json # json 모듈 추가

def daily_worker_eligibility_app():
    """일용근로자 수급자격 요건 모의계산 앱."""
    # 사이드바 토글 상태 초기화
    if 'sidebar_visible' not in st.session_state:
        st.session_state.sidebar_visible = True # PC 라이트 기본

    # 모바일 감지: JavaScript로 화면 너비 확인 (기존 방식 유지)
    screen_width_script = """
    <script>
        function updateScreenWidth() {
            window.parent.window.dispatchEvent(new CustomEvent('screen_width_event', { detail: window.innerWidth }));
        }
        window.addEventListener('resize', updateScreenWidth);
        updateScreenWidth();
    </script>
    """
    html(screen_width_script)
    
    # 쿼리 파라미터에서 screen_width를 읽어와 업데이트
    if 'screen_width_event' in st.experimental_get_query_params():
        try:
            st.session_state.screen_width = int(st.experimental_get_query_params()['screen_width_event'][0])
        except (ValueError, TypeError):
            st.session_state.screen_width = 1000 # 기본값
    else:
        st.session_state.screen_width = 1000 # 기본값

    is_mobile = st.session_state.screen_width <= 500

    # 사이드바 토글 버튼 (모바일에서만 표시)
    if is_mobile:
        # st.columns를 사용하여 버튼을 중앙에 가깝게 배치 시도
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            toggle_button = st.button("사이드바 토글", key="sidebar_toggle")
            if toggle_button:
                st.session_state.sidebar_visible = not st.session_state.sidebar_visible

    # 사이드바 렌더링
    if st.session_state.sidebar_visible:
        with st.sidebar:
            st.markdown("### 📋 정보")
            st.markdown("이 앱은 일용근로자 및 건설일용근로자의 수급자격 요건을 모의계산합니다.")
            st.markdown("- **조건 1**: 신청일이 속한 달의 직전 달 초일부터 신청일까지 근로일 수가 총 일수의 1/3 미만.")
            st.markdown("- **조건 2 (건설일용근로자)**: 신청일 직전 14일간 근무 사실 없음.")

    st.header("일용근로자 수급자격 요건 모의계산")

    # 현재 날짜와 시간 표시
    st.markdown(f"**오늘 날짜와 시간**: {current_time_korean}", unsafe_allow_html=True)

    # 요건 조건 설명
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    # 수급자격 신청일 선택
    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=current_datetime.date(), key="apply_date_input")

    # 날짜 범위 및 시작일 가져오기
    date_range_objects, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    
    # `render_calendar_interactive`는 이제 HTML과 JS를 직접 반환합니다.
    # 클릭된 날짜는 URL 쿼리 파라미터로 전달되어 Streamlit 앱이 재실행될 때 업데이트됩니다.
    # 따라서 이 함수의 반환값을 직접 사용하지 않고, st.session_state.selected_dates를 참조합니다.
    render_calendar_interactive(apply_date) 
    
    # render_calendar_interactive 함수 내에서 st.session_state.selected_dates를 쿼리 파라미터로 업데이트하므로,
    # 여기서는 단순히 참조만 합니다.
    selected_dates = st.session_state.selected_dates 
    
    st.markdown("---")

    # 조건 1 계산 및 표시
    total_days = len(date_range_objects)
    worked_days = len(selected_dates)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 1 충족: 근무일 수가 기준 미만입니다." if condition1 else "❌ 조건 1 불충족: 근무일 수가 기준 이상입니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    # 조건 2 계산 및 표시 (건설일용근로자 기준)
    fourteen_days_prior_end = apply_date - timedelta(days=1)
    fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
    fourteen_days_prior_range = [d.date() for d in pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end)]
    no_work_14_days = all(day not in selected_dates for day in fourteen_days_prior_range)
    condition2 = no_work_14_days

    st.markdown(
        f'<div class="result-text">'
        f'<p>{"✅ 조건 2 충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 근무내역이 없습니다." if no_work_14_days else "❌ 조건 2 불충족: 신청일 직전 14일간(" + fourteen_days_prior_start.strftime("%Y-%m-%d") + " ~ " + fourteen_days_prior_end.strftime("%Y-%m-%d") + ") 내 근무기록이 있습니다."}</p>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("---")

    # 조건 1 불충족 시 미래 신청일 제안
    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        found_suggestion = False
        for i in range(1, 31):
            future_date = apply_date + timedelta(days=i)
            date_range_future_objects, _ = get_date_range(future_date)
            total_days_future = len(date_range_future_objects)
            threshold_future = total_days_future / 3
            worked_days_future = sum(1 for d in selected_dates if d <= future_date)

            if worked_days_future < threshold_future:
                st.markdown(
                    f'<div class="result-text">'
                    f'<p>✅ <b>{future_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 요건을 충족할 수 있습니다.</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                found_suggestion = True
                break
        if not found_suggestion:
            st.markdown(
                f'<div class="result-text">'
                f'<p>❗ 앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    # 조건 2 불충족 시 미래 신청일 제안 (건설일용근로자 기준)
    if not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        last_worked_day = max((d for d in selected_dates if d < apply_date), default=None)
        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15)
            st.markdown(
                f'<div class="result-text">'
                f'<p>✅ <b>{suggested_date.strftime("%Y-%m-%d")}</b> 이후에 신청하면 조건 2를 충족할 수 있습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="result-text">'
                f'<p>이미 최근 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.</p>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.subheader("📌 최종 판단")
    if condition1:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 일반일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="result-text">'
            f'<p>❌ 일반일용근로자: 신청 불가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )

    if condition1 and condition2:
        st.markdown(
            f'<div class="result-text">'
            f'<p>✅ 건설일용근로자: 신청 가능<br>'
            f'<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime("%Y-%m-%d")} ~ {apply_date.strftime("%Y-%m-%d")}) 근로일 수의 합이 총 일수의 3분의 1 미만이고, 신청일 직전 14일간({fourteen_days_prior_start.strftime("%Y-%m-%d")} ~ {fourteen_days_prior_end.strftime("%Y-%m-%d")}) 근무 사실이 없음을 확인합니다.</b></p>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        error_message = "❌ 건설일용근로자: 신청 불가능<br>"
        if not condition1:
            error_message += f"<b>수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 이상입니다.</b><br>"
        if not condition2:
            error_message += f"<b>신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 있습니다.</b>"
        st.markdown(
            f'<div class="result-text">'
            f'<p>{error_message}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    # JavaScript로 화면 너비 업데이트 (query parameter 방식)
    # 이 스크립트는 앱이 로드될 때마다 실행되어 Streamlit에게 화면 너비를 알려줍니다.
    screen_width_updater_script = """
    <script>
        function updateScreenWidthAndRerun() {
            const currentUrl = new URL(window.location.href);
            if (currentUrl.searchParams.get('screen_width_event') != window.innerWidth) {
                currentUrl.searchParams.set('screen_width_event', window.innerWidth);
                window.history.replaceState({}, '', currentUrl);
                window.parent.document.dispatchEvent(new Event('streamlit:force_rerun')); // 강제 rerun 트리거
            }
        }
        window.addEventListener('resize', updateScreenWidthAndRerun);
        updateScreenWidthAndRerun(); // 초기 로드 시에도 실행
    </script>
    """
    html(screen_width_updater_script)

    # JavaScript 이벤트 리스너: 날짜 클릭 이벤트를 Streamlit에 전달
    # 이 스크립트는 앱이 로드될 때 한 번만 삽입되어야 합니다.
    # `st.experimental_js`는 페이지 로드 시 한 번만 실행되는 경향이 있어 적합합니다.
    # `st.experimental_js`는 `st.session_state`를 직접 수정할 수 없으므로, 쿼리 파라미터 방식으로 우회합니다.
    st.experimental_js(f"""
        window.parent.document.addEventListener('date_selection', (e) => {{
            const clickedDate = e.detail;
            const currentUrl = new URL(window.location.href);
            let selectedDates = [];
            try {{
                // 현재 URL에서 selected_dates_query 파라미터 읽기
                const queryParam = currentUrl.searchParams.get('selected_dates_query');
                if (queryParam) {{
                    selectedDates = JSON.parse(decodeURIComponent(queryParam));
                }}
            }} catch (error) {{
                console.error("Error parsing selected_dates_query:", error);
            }}
            
            // 날짜 토글 로직
            if (selectedDates.includes(clickedDate)) {{
                selectedDates = selectedDates.filter(d => d !== clickedDate);
            }} else {{
                selectedDates.push(clickedDate);
            }}
            
            // 변경된 selectedDates를 URL 쿼리 파라미터로 인코딩하여 설정
            currentUrl.searchParams.set('selected_dates_query', encodeURIComponent(JSON.stringify(selectedDates)));
            window.history.replaceState({{}}, '', currentUrl); // URL 변경
            window.parent.document.dispatchEvent(new Event('streamlit:force_rerun')); // 강제 rerun 트리거
        }});
    """)

    daily_worker_eligibility_app()
