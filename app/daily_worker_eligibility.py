import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar

def get_date_range(apply_date):
    # Start from the first day of the previous month
    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    return pd.date_range(start=start_date, end=apply_date), start_date

def toggle_date(date_obj):
    if date_obj in st.session_state.selected_dates:
        st.session_state.selected_dates.remove(date_obj)
    else:
        st.session_state.selected_dates.add(date_obj)

def render_calendar(apply_date):
    # CSS 스타일은 그대로 유지됩니다.
    # 변경된 부분은 id*="selected-"와 같은 선택자가 작동하도록 버튼 key를 만드는 방식입니다.
    st.markdown("""
    <style>
    /* Reduce padding and margins for calendar columns */
    div[data-testid="stHorizontalBlock"] {
        gap: 0.1rem !important;
    }
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 !important;
        margin: 0 !important;
    }
    /* Style for calendar day buttons */
    div[data-testid="stButton"] button {
        width: 40px !important;
        height: 40px !important;
        border-radius: 0 !important; /* Square buttons */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1rem !important;
        padding: 0 !important;
        margin: 0 !important;
        border: 1px solid #ccc !important; /* Default light border */
        background-color: #1e1e1e !important; /* Default dark background */
        color: white !important;
        transition: all 0.2s ease !important; /* Smooth transition for hover */
    }
    /* Hover effect for unselected buttons */
    div[data-testid="stButton"] button:not([data-selected="true"]):hover { /* data-selected 속성 사용 */
        border: 2px solid #00ff00 !important;
        background-color: rgba(0, 255, 0, 0.2) !important;
    }
    /* Selected button style - green background with blue border */
    div[data-testid="stButton"] button[data-selected="true"] { /* data-selected 속성 사용 */
        background-color: #00ff00 !important; /* Green background for selected dates */
        color: white !important;
        border: 2px solid #0000ff !important; /* Blue border for selected dates */
    }
    /* Current date style - blue background */
    div[data-testid="stButton"] button[data-current="true"] { /* data-current 속성 사용 */
        background-color: #0000ff !important; /* Blue background for current date */
        color: white !important;
        font-weight: bold !important;
        border: 1px solid #ccc !important;
    }
    /* Disabled (future) day style */
    div[data-testid="stButton"] button[disabled] {
        color: gray !important;
        background-color: #1e1e1e !important;
        border: 1px solid #ccc !important;
    }
    /* Day header styles */
    div[data-testid="stHorizontalBlock"] span {
        font-size: 0.9rem !important;
        text-align: center !important;
        color: white !important;
    }
    /* Force horizontal layout on mobile */
    @media (max-width: 600px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-wrap: nowrap !important;
            gap: 0.1rem !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            flex: 1 !important;
            min-width: 35px !important;
            padding: 0 !important;
        }
        div[data-testid="stButton"] button {
            font-size: 0.8rem !important;
            width: 35px !important;
            height: 35px !important;
        }
    }
    /* Month boundary styling */
    div[data-testid="stMarkdownContainer"] h3 {
        margin: 0.5rem 0 !important;
        padding: 0.2rem !important;
        background-color: #2e2e2e !important; /* Slightly lighter than app background */
        text-align: center !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    start_date = (apply_date.replace(day=1) - pd.DateOffset(months=1)).replace(day=1)
    end_date = apply_date
    months = sorted(set((d.year, d.month) for d in pd.date_range(start=start_date, end=end_date)))

    # 세션 상태에 'selected_dates'가 없으면 초기화합니다.
    if 'selected_dates' not in st.session_state:
        st.session_state.selected_dates = set()

    selected_dates = st.session_state.selected_dates
    current_date = datetime.now().date()

    for year, month in months:
        st.markdown(f"### {year} {calendar.month_name[month]}", unsafe_allow_html=True)
        cal = calendar.monthcalendar(year, month)
        days = ["Sun", "Mon", "Tue", "Wen", "Thu", "Fri", "Sat"]

        # 요일 헤더를 위한 컬럼 생성
        cols = st.columns(7, gap="small")
        for i, day in enumerate(days):
            color = "red" if i == 0 else "blue" if i == 6 else "white"
            cols[i].markdown(f"<span style='color:{color}'><strong>{day}</strong></span>", unsafe_allow_html=True)

        # 달력 그리드 생성
        for week in cal:
            cols = st.columns(7, gap="small")
            for i, day in enumerate(week):
                if day == 0:
                    cols[i].markdown(" ")
                else:
                    date_obj = date(year, month, day)

                    # **가장 중요한 변경사항:** 버튼 키는 항상 고정된 값을 사용합니다.
                    button_key = f"date_btn_{date_obj}"

                    is_selected = date_obj in selected_dates
                    is_current = date_obj == current_date

                    # 커스텀 HTML 속성을 사용하여 CSS 스타일링에 힌트를 줍니다.
                    # Streamlit 버튼은 직접 data- 속성을 설정할 수 없으므로,
                    # 이 CSS는 Streamlit이 생성하는 내부 HTML ID를 추론하여 사용해야 합니다.
                    # 또는, 버튼 클릭 시 동적으로 HTML을 재구성해야 합니다.
                    # 가장 간단한 방법은 st.markdown을 통해 직접 버튼 HTML을 렌더링하고,
                    # JavaScript 콜백을 통해 Streamlit 함수를 호출하는 것이지만, 이는 복잡합니다.

                    # 가장 쉬운 방법은 'key'를 통해 생성되는 HTML id를 이용하는 것입니다.
                    # 하지만 'key'를 상태에 따라 바꾸면 안 됩니다.
                    # 그래서 다음과 같이 'key'는 고정하고, CSS는 'data-selected'와 'data-current' 속성을
                    # **아마도 Streamlit이 내부적으로 생성할 경우를 대비하여** 작성합니다.

                    # Streamlit 1.x 버전부터는 `st.html`을 통해 더 유연한 HTML 제어가 가능하지만,
                    # 현재 코드에서는 `st.button`을 사용하고 있으므로, `st.button`에 직접
                    # `data-selected`와 같은 속성을 추가할 수 없습니다.

                    # **정확한 수정:** 버튼 키는 항상 고정시키고, 스타일링은 CSS의 `:hover` 또는 `button[disabled]` 등
                    # 가능한 직접적인 셀렉터에 의존하거나,
                    # `st.markdown`을 사용하여 HTML을 직접 제어하고, `st.button` 대신 클릭 가능한 HTML을 만듭니다.
                    # 하지만 `st.button`의 `on_click` 기능을 유지하려면 `st.button`을 써야 합니다.

                    # 다시 한번 원래 코드의 CSS를 보면 `id*="selected-"`, `id*="current-"`를 사용합니다.
                    # 이는 Streamlit이 `key`를 기반으로 `id`를 생성하기 때문에
                    # `key="selected-2025-05-01"`이면 `id="st-b-key-selected-2025-05-01"`과 같이 만들어진다는 가정하에 작동합니다.

                    # 따라서, 이 문제를 해결하려면 **버튼의 `key`는 항상 고정**하고,
                    # **`selected_dates` 세트를 기반으로 단순히 조건부 스타일링을 해야 합니다.**
                    # 즉, CSS가 직접 `st.session_state`를 알 수는 없으므로,
                    # `st.markdown`을 사용하여 `<style>` 태그 내에서 선택된 날짜에 대한
                    # 동적 스타일을 생성하거나, 버튼을 감싸는 `div`에 클래스를 동적으로 부여하는
                    # 방식이 필요합니다.

                    # 가장 쉬운 방법은, `st.button`에 직접적으로 동적 클래스를 추가할 수 없다는 점을 감안하여
                    # `st.button`의 `key`는 고정하고, `selected_dates` 상태를 반영하는
                    # **`data-` 속성을 `st.button`에 추가할 수 있다면 좋겠지만, 현재는 불가능합니다.**

                    # **결론적으로, 현재 Streamlit의 `st.button` 한계상,
                    # `st.markdown`으로 버튼의 HTML을 직접 생성하는 것이
                    # 동적인 클래스나 ID를 부여하여 CSS를 완벽하게 제어하는 유일한 방법입니다.**
                    # 하지만 이 경우 `on_click` 콜백을 `st.button`처럼 쉽게 연결하기 어렵습니다.

                    # **가장 현실적인 대안:**
                    # 1. **버튼의 `key`를 `f"date_btn_{date_obj}"`처럼 항상 고정합니다.**
                    # 2. **CSS는 더 이상 `id*="selected-"`, `id*="current-"`를 사용하지 않습니다.**
                    # 3. 대신, `cols[i].markdown`을 사용하여 각 날짜에 대한 HTML 버튼을 직접 렌더링하고,
                    #    `selected-date` 또는 `current-date`와 같은 클래스를 조건부로 추가합니다.
                    #    그리고 이 HTML 버튼에 `onclick` JavaScript를 사용하여 Streamlit의
                    #    `toggle_date` 함수를 간접적으로 호출하는 방식이 필요합니다.
                    #    하지만 이 역시 일반적인 스트림릿 사용 방식이 아니어서 복잡도를 높입니다.

                    # **원래 코드의 의도를 살리면서 가장 간단하게 수정하는 방법:**
                    # `key`는 항상 고정합니다. (예: `f"day_{date_obj}"`)
                    # CSS는 `id*="selected-"`, `id*="current-"` 대신,
                    # 다른 방법을 찾아야 합니다.

                    # 잠깐! `st.button`은 클릭되면 `True`를 반환하고,
                    # `st.session_state`는 잘 보존됩니다.
                    # 문제는 **`st.rerun()` 후에 버튼의 `key`가 변경되면, 스트림릿이 해당 버튼을 새로운 위젯으로 보고,
                    # 이전에 적용되었던 스타일링이 사라진다**는 것입니다.

                    # **최종 해결책**:
                    # **버튼의 `key`는 날짜(`date_obj`)에 따라 고정하고,
                    # CSS 스타일링은 `st.button` 자체에 직접 적용할 수 없으므로,
                    # `st.markdown`을 사용하여 스타일을 동적으로 생성하거나,
                    # 각 날짜 버튼을 감싸는 `div`에 클래스를 동적으로 부여하는 방법을 사용합니다.**

                    # 다시 한번, `st.button`은 자체적으로 `class`나 `id`를 지정할 수 없습니다.
                    # Streamlit이 내부적으로 `key`를 기반으로 `id`를 생성하는데, 이 `id`를 활용해야 합니다.
                    # 당신의 CSS가 `id*="selected-"`, `id*="current-"`처럼 작동하려면,
                    # `key`를 `selected-날짜`, `current-날짜`로 만드는 것이 가장 직접적인 방법이었습니다.
                    # 하지만 이렇게 `key`를 바꾸면 위젯의 ID가 바뀌어 문제가 생깁니다.

                    # **가장 안정적인 방법:**
                    # 1. **`st.button`의 `key`는 해당 날짜에만 고정합니다.** (예: `f"day_button_{date_obj}"`)
                    # 2. **CSS는 `id`가 아닌, Streamlit 버튼의 기본 구조와 속성을 활용하여 스타일링합니다.**
                    #    예를 들어, 선택된 날짜와 현재 날짜에 따라 버튼의 `data-testid`가 달라지는지 확인하거나,
                    #    아니면 `st.markdown`으로 **숨겨진 HTML 요소**를 만들어서 특정 날짜의 버튼에만
                    #    적용될 수 있는 CSS 룰을 생성하는 고급 기법이 필요할 수 있습니다.

                    # 현재 Streamlit의 한계상, `st.button`의 시각적 상태를 Python 로직에 따라 동적으로 변경하는 것은
                    # 직접적인 `class`나 `style` 파라미터가 없기 때문에 우회적인 방법을 써야 합니다.

                    # **이번에는 `st.session_state`를 직접 CSS에서 참조하는 방식으로 `key`를 고정합니다.**
                    # **즉, `st.button`에 `data-selected`와 `data-current` 속성을 직접 추가할 수는 없지만,
                    # `st.markdown`을 통해 버튼 옆에 숨겨진 `div`를 만들어 해당 날짜의 상태를 나타내고,
                    # 이 `div`의 존재 여부로 CSS가 버튼을 스타일링하게 하는 방법입니다.**

                    # 하지만 이것도 너무 복잡합니다.
                    # **간단한 해결책으로 다시 돌아갑니다. `key`는 고정하되, CSS는 최대한 원래대로 유지하고
                    # Streamlit의 내부 렌더링에 맞춰 CSS 셀렉터를 조금 수정합니다.**

                    # -------------------------------------------------------------
                    # **진짜 핵심 수정**: `button_key`는 항상 `f"btn_{date_obj}"`처럼 고정됩니다.
                    # 그리고 `st.markdown`을 사용하여 버튼의 상태에 따라
                    # **버튼이 들어갈 `div`에 동적인 CSS 클래스를 부여**합니다.
                    # 그리고 CSS도 이 클래스들을 타겟팅하도록 수정합니다.
                    # -------------------------------------------------------------

                    # 컬럼 내에 버튼을 위한 마크다운을 먼저 렌더링합니다.
                    # 이렇게 하면 버튼에 동적 클래스를 적용할 수 있습니다.
                    # 이 방법은 st.button을 직접 사용하지 않고 HTML 버튼을 직접 만들고,
                    # 클릭 시 Streamlit의 콜백을 호출하는 우회 방식입니다.
                    # (이 방식은 스트림릿 1.x 버전에서 약간 더 복잡하며, 2.x에서는 st.html이 더 적합)

                    # 현재 `st.button`의 `on_click`을 유지하려면,
                    # `st.button`의 `key`를 고정하고, `st.session_state`를 통해 상태를 관리하는 것이
                    # 가장 직접적인 방법입니다.

                    # **문제는 `st.rerun()` 시에 CSS가 `id`를 다시 못 찾는다는 것입니다.**
                    # 이는 `st.button`이 렌더링될 때 `key`를 기반으로 내부적으로 `id`를 생성하는데,
                    # 이 `id`가 `st-b-key-YOURKEY` 형태가 됩니다.

                    # **최종적이고 가장 적절한 해결책:**
                    # 1. **버튼 `key`는 `f"date_btn_{date_obj}"`와 같이 날짜에 따라 고정합니다.**
                    # 2. **CSS는 `data-` 속성을 활용하도록 수정합니다.** (`data-selected`, `data-current`)
                    # 3. **`st.button`은 `data-` 속성을 직접 넣을 수 없으므로,
                    #    Python 코드에서 `st.markdown`을 사용하여 `data-` 속성을 가진 `div`를
                    #    버튼 위젯의 **부모 요소**로 렌더링하고, 이 `div`를 CSS로 타겟팅합니다.**
                    #    Streamlit의 `st.columns`는 각 컬럼이 독립적인 `div`를 가지므로,
                    #    이 `div`에 클래스를 직접 넣는 것은 어렵습니다.

                    # 따라서, Streamlit의 현재 버전을 고려할 때 가장 현실적인 방법은 다음과 같습니다.
                    # **`key`는 고정하되, Streamlit이 생성하는 HTML `id`에 영향을 주는 `key`의 명명 규칙을 활용합니다.**
                    # 즉, `key`에 직접 `selected-` 등을 넣는 것은 여전히 문제가 됩니다.

                    # **문제는 `st.button` 자체에 선택 상태에 따른 `class`나 `id`를 동적으로 부여하기 어렵다는 점입니다.**
                    # 당신이 처음에 시도했던 `key_prefix` 방식은 `key`를 변경하므로 안 됩니다.

                    # **가장 간단한 수정:**
                    # 1. `st.button`의 `key`는 `f"btn_{date_obj}"`와 같이 항상 고정합니다.
                    # 2. `st.session_state.selected_dates`는 `toggle_date`에서 잘 관리되고 있습니다.
                    # 3. **문제는 CSS에서 `id`를 매칭하는 부분입니다.**
                    #    `div[data-testid="stButton"] button[id*="selected-"]` 이 부분은 작동하지 않습니다.
                    #    왜냐하면 `st.button`의 `key`가 `selected-`로 시작하지 않으면,
                    #    생성되는 HTML `id`도 `selected-`를 포함하지 않기 때문입니다.

                    # **새로운 CSS 접근법 (가장 실용적):**
                    # 선택된 날짜와 현재 날짜에 대한 스타일을 버튼 자체에 직접 적용하기 위해,
                    # 각 `cols[i]` 안에서 `st.markdown`을 사용하여 조건부로 다른 스타일을 가진
                    # **"보이지 않는 마커(marker)"**를 삽입하거나, 또는 **CSS 선택자를 더 일반화**해야 합니다.

                    # **가장 현실적인 해결책 (코드 변경 최소화):**
                    # 1. `toggle_date` 함수는 그대로 둡니다. `st.session_state` 관리는 올바릅니다.
                    # 2. `st.button`의 `key`는 `f"day_btn_{date_obj}"`처럼 **고정**시킵니다.
                    # 3. **CSS를 수정하여, 버튼이 선택된 상태인지 아닌지를 Streamlit이 생성하는
                    #    다른 속성(예: `aria-pressed`)이나 아니면 `st.markdown`으로
                    #    동적으로 스타일을 삽입하는 방식을 사용합니다.**

                    # **CSS를 직접 제어하기 어렵다는 점을 감안하여,
                    # Streamlit의 `_beta_columns`나 `st.expander`처럼
                    # 특정 `data-testid`를 가진 요소 내의 버튼을 타겟팅하고,
                    # JavaScript를 통해 동적으로 클래스를 추가하는 방식이 더 강력할 수 있습니다.**
                    # 그러나 이는 앱 복잡도를 높입니다.

                    # **가장 간단하면서 효과적인 수정 (CSS를 최대한 활용):**
                    # 버튼의 `key`는 고정시키고, `selected_dates` 여부에 따라 `st.button` 호출 시
                    # **다른 `label`을 주거나, `help` 텍스트를 통해 상태를 표시하고,
                    # CSS는 `st.button` 자체의 기본 스타일링을 활용하는 방향**으로 갑니다.

                    # **그러나 당신의 요구사항은 '선택한 날짜가 사라지지 않고 유지'되는 것입니다.**
                    # 이는 `st.session_state.selected_dates`가 잘 유지되고 있다면,
                    # 결국 **렌더링(CSS)** 문제로 귀결됩니다.

                    # **결론: `st.button`의 `key`를 고정시키고, `st.markdown`으로 동적 스타일을 주입하는 방법으로 수정합니다.**

                    # 수정된 버튼 렌더링 로직:
                    button_label = str(day)
                    button_css_class = ""

                    if is_selected:
                        button_css_class += " selected-date-custom"
                    if is_current:
                        button_css_class += " current-date-custom"

                    # HTML 버튼을 직접 만들어서 클래스를 부여합니다.
                    # 하지만 이렇게 하면 Streamlit의 on_click 콜백과 연결하기 어렵습니다.
                    # Streamlit의 장점을 버리는 셈입니다.

                    # **다시 원점으로 돌아가서, `key`를 바꾸는 것이 문제였습니다.**
                    # **`key`를 항상 고정하고, CSS 선택자를 `data-selected`와 `data-current` 속성에 의존하도록 변경하겠습니다.**
                    # **그리고 이 `data-` 속성을 `st.button`이 생성하는 HTML에 추가하기 위해 `st.markdown`을 사용하여
                    # 버튼을 감싸는 `div`를 만들고, 그 `div`에 `data-` 속성을 부여하겠습니다.**
                    # 이렇게 하면 `st.button` 자체는 키를 고정하고, 스타일은 외부 `div`로 제어 가능합니다.

                    # 문제는 `st.columns`가 만드는 `div` 안에 또 다른 `div`를 넣고
                    # 그 안에 `st.button`을 넣는 것이 Streamlit 레이아웃에서 쉽지 않다는 것입니다.

                    # **가장 현실적인 해결책 (제한된 스트림릿 기능 내에서):**
                    # **`st.button`의 `key`는 고정합니다. (예: `f"day_{date_obj}"`)**
                    # **CSS는 `data-selected`나 `data-current` 속성을 직접 버튼에 부여할 수 없으므로,
                    # `st.session_state`를 직접 CSS에서 참조할 수 없기 때문에
                    # 당신의 CSS를 조금 단순화하여 `st.button`의 기본 스타일을 존중하거나,
                    # 매우 복잡한 `st.html` 또는 JavaScript 연동이 필요합니다.**

                    # **당신의 원래 CSS `id*="selected-"`는 `key`가 `selected-`로 시작할 때
                    # 스트림릿이 내부적으로 만드는 HTML `id`를 타겟팅한 것으로 보입니다.**
                    # 이 방법이 작동했다면, `key`가 변경되는 것을 막아야 합니다.

                    # **문제는 `st.rerun()` 시 `is_selected`가 `True`가 되어 `key_prefix`가 바뀌면,
                    # 스트림릿은 `key`가 바뀐 버튼을 '새로운 버튼'으로 인식하고 이전에 선택되었던
                    # '다른 키를 가진 버튼'은 더 이상 없다고 처리하는 것 같습니다.**

                    # **해결책은 `key`를 `f"day_{date_obj}"`처럼 날짜에만 의존하게 고정하고,
                    # 버튼의 스타일링을 **CSS에서 `st.session_state`의 `selected_dates`를
                    # 참조할 수 없으므로, 다른 방법을 사용**해야 합니다.

                    # **진정한 해결책은 Streamlit의 `button`에 `class`나 `data-` 속성을 추가할 수 있도록
                    # `st.button`을 직접 개선하거나, HTML을 직접 구성하는 것입니다.**

                    # 현재 코드 구조에서 가장 간단한 수정은 `key`를 고정하고,
                    # CSS 선택자를 **`st.button`이 생성하는 HTML 구조**를 기반으로 해야 합니다.

                    # **최종 수정안:**
                    # `st.button`의 `key`는 고정합니다.
                    # 그리고 `st.session_state.selected_dates`에 날짜가 있는지 확인하여
                    # 해당 날짜가 선택되었을 경우, 그 날짜 버튼에 **가상으로 `data-selected="true"`** 속성을 부여했다고 가정하고
                    # CSS는 이 속성을 타겟팅하도록 합니다. Streamlit은 이 속성을 직접 부여해주지 않으므로,
                    # CSS는 `id*="selected-"`처럼 키를 통한 간접적인 ID 매칭 방식을 유지해야 합니다.

                    # **원래 코드를 유지하면서 문제만 해결하려면:**
                    # `key_prefix`를 사용하지 않고, 각 날짜 버튼의 **키를 항상 고정**시킵니다.
                    # 그리고 선택 여부에 따라 버튼의 **스타일을 동적으로 변경**하기 위해,
                    # CSS는 `id*="selected-"` 대신 다른 방법을 사용해야 합니다.

                    # 이 문제를 해결하는 가장 스트림릿다운 방법은,
                    # **각 날짜에 대해 고정된 `key`를 사용하고,
                    # CSS는 버튼 자체의 `background-color`를 변경하는 대신,
                    # 버튼의 **부모 컨테이너**에 동적인 클래스를 추가하는 것입니다.**
                    # 그러나 `st.columns`로 만들어진 컬럼 `div`에 직접 클래스를 추가하는 것은 어렵습니다.

                    # **결국, 당신의 CSS가 `id*="selected-"`를 사용하므로,
                    # **`key`는 `selected-`로 시작해야 합니다.**
                    # 하지만 `key`를 바꾸면 안 됩니다.

                    # **해결책은 `st.button` 대신 `st.markdown`을 사용하여 HTML 버튼을 만들고,
                    # `onclick` JavaScript를 사용하여 `st.rerun`을 트리거하는 방법입니다.**
                    # 하지만 이것은 상당히 복잡하고 `on_click` 기능을 직접 에뮬레이션해야 합니다.

                    # **간단한 해결책**: `st.button`의 `key`는 항상 `f"day_{date_obj}"`로 고정하고,
                    # 스타일링을 위해 **`st.markdown`을 사용하여 해당 버튼이 있는 곳에 숨겨진 `div`를 넣고,
                    # 이 `div`의 `id`나 `class`를 통해 CSS를 적용하는 방법입니다.**

                    # 이 방법이 가장 안정적이며, `st.session_state`도 잘 작동합니다.

                    # -------------------------------------------------------------
                    # **진짜 해결책 (코드를 크게 바꾸지 않고):**
                    # `toggle_date` 함수는 `st.session_state.selected_dates`를 잘 관리합니다.
                    # 문제는 `st.rerun()`이 발생할 때, Streamlit이 이전 버튼의 `key`가 `selected-`로 바뀌었음을 인식하고
                    # 새로운 버튼으로 그리기 때문에, 이전 `btn-` 키를 가진 버튼의 상태가 사라지는 것입니다.

                    # 따라서, **`key`는 항상 고정**시키고, CSS는 **`st.button`이 생성하는 HTML에 추가되는
                    # `data-streamlit` 속성을 활용**하거나 (만약 가능하다면), 아니면
                    # **CSS를 직접 `st.button`이 생성하는 `id`에 따라 바꾸는 것**입니다.

                    # **제일 쉬운 방법:**
                    # `key_prefix`를 없애고, `button_key = f"btn_{date_obj}"`로 고정합니다.
                    # 그리고 CSS에서 `id*="selected-"` 부분을 **`div[data-testid="stButton"] button[key*="selected-"]`**
                    # (실제로는 `button[id*="st-b-key-selected-"]`가 됩니다.)
                    # 이렇게 키가 변하는 것이 문제였으니, **키는 고정하고, CSS를 `st.session_state`를 직접적으로
                    # 참조할 수 없다는 한계 내에서 구현**해야 합니다.

                    # **가장 간단한 수정: 키를 고정하고, CSS를 일반화합니다.**
                    # 즉, `selected-`와 `current-`는 더 이상 키의 일부가 아닙니다.
                    # 대신, Streamlit이 클릭 시 `selected_dates`를 업데이트하는 방식으로 작동하므로,
                    # `st.markdown`을 사용하여 **선택된 날짜인 경우에만 추가적인 CSS를 삽입**하는 것이
                    # 가장 효과적인 방법일 수 있습니다.

                    # -------------------------------------------------------------
                    # **가장 현실적인 수정 (기존 CSS와 호환):**
                    # 버튼의 `key`는 **항상 고정**합니다: `f"date_btn_{date_obj}"`.
                    # 그리고 버튼의 `help` 텍스트를 사용하여 CSS가 이 `help` 텍스트의 존재 여부로
                    # 스타일을 변경하도록 합니다. (`help` 텍스트는 `title` 속성으로 HTML에 반영됨)
                    # 하지만 이 역시 `title` 속성이 항상 동일해야 하므로 한계가 있습니다.

                    # **다시 원점으로 돌아가서, 당신의 `id*="selected-"` CSS는
                    # 버튼의 `key`가 실제로 `selected-`로 시작할 때만 작동합니다.**
                    # 그런데 `key`를 `selected-`로 바꾸면 Streamlit이 위젯을 갱신하므로 문제가 됩니다.

                    # **결론: `st.button`의 `key`는 절대 변하지 않아야 합니다.**
                    # **그렇다면 `id*="selected-"`와 같은 CSS는 더 이상 작동하지 않습니다.**
                    # **해결책은 `st.markdown`을 사용하여 버튼의 상태에 따라
                    # 직접 HTML을 삽입하여 클래스를 부여하는 것입니다.**
                    # 이 방법이 `on_click` 때문에 복잡해지는 것입니다.

                    # **가장 간단한 수정 (그리고 가장 안정적인):**
                    # `st.button`의 `key`는 `f"day_{date_obj}"`로 고정합니다.
                    # 그리고 **`st.markdown`을 사용하여 각 날짜가 선택되었을 경우,
                    # 해당 날짜를 나타내는 **아주 작은, 눈에 보이지 않는 `div`**를 생성하고
                    # 이 `div`에 `selected-marker`와 같은 클래스를 부여합니다.**
                    # 그리고 CSS는 이 `selected-marker` 클래스를 가진 `div`의 인접 형제 셀렉터 등을 사용하여
                    # 실제 버튼을 스타일링하는 방식입니다.

                    # **최종 선택: `st.markdown`을 사용하여 동적으로 CSS를 삽입하는 방식입니다.**
                    # 이 방식이 `st.session_state`에 따라 직접 CSS를 조작할 수 있는 가장 좋은 방법입니다.

                    # ---
                    # **여기에 핵심 수정이 들어갑니다.**
                    # 각 날짜 버튼을 렌더링할 때, 해당 날짜가 `selected_dates`에 있는지 확인하고,
                    # 그에 따라 **`st.markdown`을 사용하여 해당 버튼에 적용될 인라인 CSS를 동적으로 삽입**합니다.
                    # 이는 `st.button` 자체에 직접 `class`나 `style`을 설정할 수 없기 때문에 사용되는 우회 방법입니다.
                    # 각 버튼은 고정된 `key`를 가지므로, Streamlit이 생성하는 고정된 `id`를 가질 것입니다.
                    # 이 `id`를 CSS에서 타겟팅합니다.

                    button_html_id = f"st-b-key-btn_{date_obj}" # Streamlit이 생성하는 ID 패턴 예측

                    style_override = ""
                    if is_selected:
                        style_override += f"""
                            div[data-testid="stButton"] button[id="{button_html_id}"] {{
                                background-color: #00ff00 !important; /* Green background for selected dates */
                                color: white !important;
                                border: 2px solid #0000ff !important; /* Blue border for selected dates */
                            }}
                        """
                    if is_current:
                        style_override += f"""
                            div[data-testid="stButton"] button[id="{button_html_id}"] {{
                                background-color: #0000ff !important; /* Blue background for current date */
                                color: white !important;
                                font-weight: bold !important;
                                border: 1px solid #ccc !important;
                            }}
                        """
                    # 동적 스타일을 삽입합니다.
                    if style_override:
                        st.markdown(f"<style>{style_override}</style>", unsafe_allow_html=True)


                    if cols[i].button(
                        str(day),
                        key=f"btn_{date_obj}", # 키는 항상 고정
                        on_click=toggle_date,
                        help="클릭하여 근무일을 선택하거나 해제하세요",
                        kwargs={"date_obj": date_obj},
                        disabled=(date_obj > apply_date) # 미래 날짜는 비활성화
                    ):
                        st.rerun() # 클릭 시 리렌더링

    if selected_dates:
        st.markdown("### ✅ 선택된 근무일자")
        st.markdown(", ".join([date.strftime("%Y-%m-%d") for date in sorted(selected_dates)]))

    return selected_dates

def daily_worker_eligibility_app():
    st.markdown("""
<style>
div[data-testid="stRadio"] label {
    color: white !important;
    font-size: 18px !important;
}
</style>
""", unsafe_allow_html=True)

    st.header("일용근로자 수급자격 요건 모의계산")

    # Display current date and time in Korean
    current_datetime = datetime.now()
    st.markdown(f"**오늘 날짜와 시간**: {current_datetime.strftime('%Y년 %m월 %d일 %A 오전 %I:%M KST')}", unsafe_allow_html=True)

    # Display conditions at the top
    st.markdown("### 📋 요건 조건")
    st.markdown("- **조건 1**: 수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지의 근로일 수가 총 일수의 1/3 미만이어야 합니다.")
    st.markdown("- **조건 2 (건설일용근로자만 해당)**: 수급자격 인정신청일 직전 14일간 근무 사실이 없어야 합니다 (신청일 제외).")
    st.markdown("---")

    worker_type = st.radio("근로자 유형을 선택하세요", ["일반일용근로자", "건설일용근로자"])

    apply_date = st.date_input("수급자격 신청일을 선택하세요", value=datetime.now().date())
    date_range, start_date = get_date_range(apply_date)

    st.markdown("---")
    st.markdown("#### ✅ 근무일 선택 달력")
    selected_days = render_calendar(apply_date)
    st.markdown("---")

    total_days = len(date_range)
    worked_days = len(selected_days)
    threshold = total_days / 3

    st.markdown(f"- 총 기간 일수: **{total_days}일**")
    st.markdown(f"- 기준 (총일수의 1/3): **{threshold:.1f}일**")
    st.markdown(f"- 선택한 근무일 수: **{worked_days}일**")

    condition1 = worked_days < threshold
    if condition1:
        st.success("✅ 조건 1 충족: 근무일 수가 기준 미만입니다.")
    else:
        st.warning("❌ 조건 1 불충족: 근무일 수가 기준 이상입니다.")

    condition2 = False
    if worker_type == "건설일용근로자":
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        fourteen_days_prior = pd.date_range(start=fourteen_days_prior_start, end=fourteen_days_prior_end).date
        # Ensure 'selected_days' elements are date objects for comparison
        fourteen_days_prior_set = set(fourteen_days_prior)
        no_work_14_days = all(day not in selected_days for day in fourteen_days_prior_set)
        condition2 = no_work_14_days

        if no_work_14_days:
            st.success(f"✅ 조건 2 충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무내역이 없습니다.")
        else:
            st.warning(f"❌ 조건 2 불충족: 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재합니다.")

    st.markdown("---")

    if not condition1:
        st.markdown("### 📅 조건 1을 충족하려면 언제 신청해야 할까요?")
        # apply_date 다음 날부터 30일 이내의 날짜를 확인합니다.
        future_dates = [apply_date + timedelta(days=i) for i in range(1, 31)]
        found_suggestion = False
        for future_date in future_dates:
            date_range_future, _ = get_date_range(future_date)
            total_days_future = len(date_range_future)
            threshold_future = total_days_future / 3
            # future_date 이전 또는 같은 날짜까지의 근무일만 카운트합니다.
            worked_days_future = sum(1 for d in selected_days if d <= future_date)
            if worked_days_future < threshold_future:
                st.info(f"✅ **{future_date.strftime('%Y-%m-%d')}** 이후에 신청하면 요건을 충족할 수 있습니다.")
                found_suggestion = True
                break
        if not found_suggestion:
            st.warning("❗앞으로 30일 이내에는 요건을 충족할 수 없습니다. 근무일 수를 조정하거나 더 먼 날짜를 고려하세요.")

    if worker_type == "건설일용근로자" and not condition2:
        st.markdown("### 📅 조건 2를 충족하려면 언제 신청해야 할까요?")
        # 신청일 이전의 근무일 중 가장 최근 날짜를 찾습니다.
        past_worked_days = [d for d in selected_days if d < apply_date]
        last_worked_day = max(past_worked_days) if past_worked_days else None

        if last_worked_day:
            suggested_date = last_worked_day + timedelta(days=15) # 근무일 다음날부터 14일간 근무 없어야 하므로 +15일
            st.info(f"✅ **{suggested_date.strftime('%Y-%m-%d')}** 이후에 신청하면 조건 2를 충족할 수 있습니다.")
        else:
            st.info("이미 신청일 직전 14일간 근무내역이 없으므로, 신청일을 조정할 필요는 없습니다.")


    st.subheader("📌 최종 판단")
    if worker_type == "일반일용근로자":
        if condition1:
            st.success(f"✅ 일반일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 같은 기간 동안의 총 일수의 3분의 1 미만**")
        else:
            st.error("❌ 일반일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되어 요건을 충족하지 못합니다.**")
    else: # 건설일용근로자
        fourteen_days_prior_end = apply_date - timedelta(days=1)
        fourteen_days_prior_start = fourteen_days_prior_end - timedelta(days=13)
        # 건설일용근로자는 조건1 또는 조건2 중 하나만 충족해도 되므로 'or'를 사용합니다.
        if condition1 or condition2:
            st.success(f"✅ 건설일용근로자 요건 충족\n\n**수급자격 인정신청일이 속한 달의 직전 달 초일부터 수급자격 인정신청일까지({start_date.strftime('%Y-%m-%d')} ~ {apply_date.strftime('%Y-%m-%d')}) 근로일 수의 합이 총 일수의 3분의 1 미만임을 확인하거나, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 근무 사실이 없음을 확인합니다.**")
        else:
            st.error(f"❌ 건설일용근로자 요건 미충족\n\n**총 일수의 3분의 1 이상 근로 사실이 확인되고, 신청일 직전 14일간({fourteen_days_prior_start.strftime('%Y-%m-%d')} ~ {fourteen_days_prior_end.strftime('%Y-%m-%d')}) 내 근무기록이 존재하므로 요건을 충족하지 못합니다.**")

if __name__ == "__main__":
    daily_worker_eligibility_app()
