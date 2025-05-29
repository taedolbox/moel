/* 컨테이너 스타일 */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 0px !important; /* 데스크톱 간격 최소화 */
    width: 100% !important;
    box-sizing: border-box !important;
    justify-content: flex-start !important; /* 왼쪽 정렬 */
}

/* stMarkdownContainer 스타일 */
div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    justify-content: center !important; /* 요일과 날짜는 중앙 정렬 */
    align-items: center !important; /* 수직 중앙 정렬 */
    width: 100% !important;
    height: 100% !important;
    text-align: left !important; /* 본문 텍스트는 왼쪽 정렬 */
}

/* 요일과 날짜를 포함하지 않은 stMarkdownContainer (본문 텍스트) */
div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
    justify-content: flex-start !important; /* 본문 텍스트는 왼쪽 정렬 */
}

/* 요일 헤더 스타일 */
.day-header {
    text-align: center; /* 텍스트 중앙 정렬 */
    font-weight: bold;
    margin: 0 auto;
    padding: 0;
    color: #333;
    width: 40px !important; /* 원형 크기 고정 */
    height: 40px !important; /* 원형 크기 고정 */
    min-width: 40px !important; /* 최소 크기 고정 */
    min-height: 40px !important; /* 최소 크기 고정 */
    aspect-ratio: 1/1 !important; /* 원형 유지 */
    line-height: 40px; /* 텍스트 세로 중앙 정렬 */
    border: 1px solid #ccc; /* 원형 테두리 */
    border-radius: 50%; /* 원형 스타일 */
    background-color: #f8f8f8; /* 배경색 약간 다르게 */
    display: flex;
    justify-content: center; /* 요일 중앙 정렬 */
    align-items: center; /* 수직 중앙 정렬 */
}

/* 날짜 스타일 */
.day {
    text-align: center; /* 텍스트 중앙 정렬 */
    width: 40px !important; /* 원형 크기 고정 */
    height: 40px !important; /* 원형 크기 고정 */
    min-width: 40px !important; /* 최소 크기 고정 */
    min-height: 40px !important; /* 최소 크기 고정 */
    aspect-ratio: 1/1 !important; /* 원형 유지 */
    line-height: 40px; /* 텍스트 세로 중앙 정렬 */
    border: 1px solid #ccc;
    border-radius: 50%;
    margin: 0 auto;
    background-color: #fff;
    color: #333;
    cursor: pointer;
    transition: background-color 0.2s;
    position: relative;
    display: flex;
    justify-content: center; /* 숫자 중앙 정렬 */
    align-items: center; /* 수직 중앙 정렬 */
}

/* 체크박스 스타일 */
.stCheckbox {
    position: absolute !important;
    top: 0 !important;
    left: -20px !important; /* 좌측으로 5cm(50px) 이동 */
    width: 40px !important; /* .day와 동일한 크기 */
    height: 40px !important; /* .day와 동일한 크기 */
    min-width: 40px !important;
    min-height: 40px !important;
    aspect-ratio: 1/1 !important; /* 원형 유지 */
    margin: 0 !important; /* 원 숫자와 위치 조정 */
    padding: 0 !important;
    background-color: rgba(0, 128, 255, 0.3); /* 터치 영역 확인 */
    cursor: pointer !important;
    z-index: 5000 !important;
    pointer-events: auto !important;
    box-sizing: border-box !important;
    display: flex;
    justify-content: center; /* 체크박스 중앙 정렬 */
    align-items: center; /* 수직 중앙 정렬 */
}

/* 체크박스 내부 요소 스타일 */
.stCheckbox > div > div {
    width: 40px !important; /* .stCheckbox와 동일한 크기 */
    height: 40px !important; /* .stCheckbox와 동일한 크기 */
    min-width: 40px !important;
    min-height: 100% !important;
    aspect-ratio: 1/1 !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    background-color: rgba(255, 165, 0, 0.3); /* 내부 요소 확인 */
}

/* 모바일에서도 7열 유지, 크기 증가 및 정렬 조정 */
@media (max-width: 767px) {
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 2px !important; /* 모바일 간격 유지 */
        justify-content: flex-start !important; /* 왼쪽 이동 */
        margin-left: 0; /* 왼쪽 이동 제거, 중앙 정렬 보완 */
    }
    div[data-testid="stMarkdownContainer"] {
        display: flex !important;
        justify-content: center !important; /* 요일과 날짜 중앙 정렬 */
        align-items: center !important; /* 수직 중앙 정렬 */
    }
    div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
        justify-content: flex-start !important; /* 본문 텍스트 왼쪽 정렬 */
    }
    .day, .stCheckbox {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        aspect-ratio: 1/1 !important;
        line-height: 40px !important;
        font-size: 1em;
        margin: 2px auto !important; /* 모바일 여백 유지 */
    }
    .stCheckbox {
        left: 0 !important; /* 모바일에서는 이동 없음 */
    }
    .stCheckbox > div > div {
        width: 100% !important;
        height: 100% !important;
        min-width: 100% !important;
        min-height: 100% !important;
        aspect-ratio: 1/1 !important;
    }
    .day-header {
        padding: 5px 2px; /* 모바일 간격 조정 */
        width: auto; /* 모바일에서는 원형 제거 */
        height: auto; /* 모바일에서는 원형 제거 */
        min-width: auto !important;
        min-height: auto !important;
        aspect-ratio: unset !important;
        line-height: normal; /* 기본 라인 높이 */
        border: none; /* 모바일에서는 테두리 제거 */
        border-radius: 0; /* 모바일에서는 원형 제거 */
        background-color: transparent; /* 배경 제거 */
        justify-content: center; /* 요일 중앙 정렬 */
    }
}

/* 데스크탑에서 달력 왼쪽 정렬 */
@media (min-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        max-width: 600px !important; /* 달력 전체 너비 600px로 설정 */
        margin: 0 0 0 0 !important; /* 왼쪽 정렬 */
        justify-content: flex-start !important; /* 왼쪽 정렬 */
    }
}

/* 모든 텍스트 왼쪽 정렬 */
.stMarkdown, .stText, .stHeader {
    text-align: left !important;
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .day-header {
        color: #ddd;
        background-color: #444; /* 다크 모드에서 요일 배경 */
    }
    .day-header.weekend {
        color: #ff6666;
    }
    .day {
        background-color: #333;
        color: #ddd;
        border-color: #888;
    }
    .day:hover:not(.disabled) {
        background-color: #444;
    }
    .day.disabled {
        background-color: #555;
        color: #888;
    }
    .day.selected {
        border-color: #ff6666;
    }
    .day.current {
        border-color: #6666ff;
    }
}

.day:hover:not(.disabled) {
    background-color: #f0f0f0;
}

.day.selected {
    border: 2px solid #ff4444;
    font-weight: bold;
}

.day.current {
    border: 2px solid #4444ff;
}

.day.disabled {
    background-color: #e0e0e0;
    color: #888;
    cursor: not-allowed;
}




/* ─────────────────────────────
   달력 컨테이너 7열 그리드 구성
───────────────────────────── */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 0px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    justify-content: flex-start !important;
}

/* ─────────────────────────────
   Markdown 정렬 (요일/숫자)
───────────────────────────── */
div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    height: 100% !important;
    text-align: left !important;
}

div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
    justify-content: flex-start !important;
}

/* ─────────────────────────────
   요일 헤더 스타일
───────────────────────────── */
.day-header {
    text-align: center;
    font-weight: bold;
    margin: 0 auto;
    padding: 0;
    color: #333;
    width: 40px !important;
    height: 40px !important;
    aspect-ratio: 1/1 !important;
    line-height: 40px;
    border: 1px solid #ccc;
    border-radius: 50%;
    background-color: #f8f8f8;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ─────────────────────────────
   날짜(숫자) 원 스타일
───────────────────────────── */
.day {
    text-align: center;
    width: 40px !important;
    height: 40px !important;
    aspect-ratio: 1/1 !important;
    line-height: 40px;
    border: 1px solid #ccc;
    border-radius: 50%;
    margin: 0 auto;
    background-color: #fff;
    color: #333;
    cursor: pointer;
    transition: background-color 0.2s;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ─────────────────────────────
   숨겨진 체크박스 영역
───────────────────────────── */
.stCheckbox {
    opacity: 0 !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    pointer-events: auto !important;
    z-index: 1 !important;
}

/* 내부 구조 완전 숨김 */
.stCheckbox > div > div {
    display: none !important;
}

/* ─────────────────────────────
   날짜 상태별 스타일
───────────────────────────── */
.day:hover:not(.disabled) {
    background-color: #f0f0f0;
}

.day.selected {
    border: 2px solid #ff4444;
    font-weight: bold;
}

.day.current {
    border: 2px solid #4444ff;
}

.day.disabled {
    background-color: #e0e0e0;
    color: #888;
    cursor: not-allowed;
}

/* ─────────────────────────────
   모바일 최적화 (7열 유지 + 크기 조정)
───────────────────────────── */
@media (max-width: 767px) {
    div[data-testid="stHorizontalBlock"] {
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 2px !important;
        justify-content: flex-start !important;
        margin-left: 0;
    }

    .day, .stCheckbox {
        width: 40px !important;
        height: 40px !important;
        aspect-ratio: 1/1 !important;
        line-height: 40px !important;
        font-size: 1em;
        margin: 2px auto !important;
    }

    .stCheckbox {
        left: 0 !important;
    }

    .day-header {
        padding: 5px 2px;
        width: auto;
        height: auto;
        aspect-ratio: unset !important;
        line-height: normal;
        border: none;
        border-radius: 0;
        background-color: transparent;
        justify-content: center;
    }
}

/* ─────────────────────────────
   데스크탑 레이아웃 왼쪽 정렬
───────────────────────────── */
@media (min-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        max-width: 600px !important;
        margin: 0 !important;
        justify-content: flex-start !important;
    }
}

/* ─────────────────────────────
   텍스트 전체 왼쪽 정렬
───────────────────────────── */
.stMarkdown, .stText, .stHeader {
    text-align: left !important;
}

/* ─────────────────────────────
   다크 모드 대응
───────────────────────────── */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .day-header {
        color: #ddd;
        background-color: #444;
    }
    .day-header.weekend {
        color: #ff6666;
    }
    .day {
        background-color: #333;
        color: #ddd;
        border-color: #888;
    }
    .day:hover:not(.disabled) {
        background-color: #444;
    }
    .day.disabled {
        background-color: #555;
        color: #888;
    }
    .day.selected {
        border-color: #ff6666;
    }
    .day.current {
        border-color: #6666ff;
    }
}




/* 컨테이너 스타일 */
div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(7, 1fr) !important;
    gap: 0px !important;
    width: 100% !important;
    box-sizing: border-box !important;
    justify-content: flex-start !important;
}

/* stMarkdownContainer 스타일 */
div[data-testid="stMarkdownContainer"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    width: 100% !important;
    height: 100% !important;
    text-align: left !important;
}

/* 요일과 날짜를 포함하지 않은 stMarkdownContainer */
div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
    justify-content: flex-start !important;
}

/* 요일 헤더 스타일 */
.day-header {
    text-align: center;
    font-weight: bold;
    margin: 0 auto;
    padding: 0;
    color: #333;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    min-height: 40px !important;
    aspect-ratio: 1/1 !important;
    line-height: 40px;
    border: 1px solid #ccc;
    border-radius: 50%;
    background-color: #f8f8f8;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* 날짜 스타일 */
.day {
    text-align: center;
    width: 40px !important;
    height: 40px !important;
    min-width: 40px !important;
    min-height: 40px !important;
    aspect-ratio: 1/1 !important;
    line-height: 40px;
    border: 1px solid #ccc;
    border-radius: 50%;
    margin: 0 auto;
    background-color: #fff;
    color: #333;
    cursor: pointer;
    transition: background-color 0.2s, border 0.2s;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 6000 !important;
    pointer-events: auto !important;
    touch-action: manipulation !important;
    padding: 10px !important;
}

/* 호버 시 툴팁 표시 */
.day:not(.disabled):hover::before {
    content: '숫자 오른쪽을 클릭해주세요';
    position: absolute;
    right: 50px; /* 툴팁 오른쪽 끝을 원 왼쪽에 맞춤 */
    top: 0;
    background-color: #333;
    color: #fff;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
    z-index: 7000;
    opacity: 0.9;
    pointer-events: none; /* 툴팁이 클릭 방해 안 하도록 */
}

/* 호버 및 터치 시 녹색 점 표시 */
.day:not(.disabled):hover::after,
.day:not(.disabled):active::after {
    content: '';
    position: absolute;
    width: 8px;
    height: 8px;
    background-color: #00ff00;
    border-radius: 50%;
    left: -10px;
    top: 20px;
    z-index: 7000;
    opacity: 1;
    animation: fadeOut 1s forwards;
}

/* 페이드아웃 애니메이션 */
@keyframes fadeOut {
    0% { opacity: 1; }
    100% { opacity: 0; }
}

/* 선택된 날짜 (빨간 테두리 및 배경색) */
.day.selected {
    border: 2px solid #ff4444 !important;
    font-weight: bold !important;
    background-color: #ffe6e6 !important;
}

/* 체크박스 스타일 */
.stCheckbox {
    position: absolute;
    width: 40px !important;
    height: 40px !important;
    left: 0 !important;
    top: 0 !important;
    z-index: 6500 !important;
    opacity: 0 !important;
    pointer-events: auto !important;
    cursor: pointer;
}

.stCheckbox > div > div {
    display: block !important;
    width: 40px !important;
    height: 40px !important;
    border: none !important;
    background-color: transparent !important;
}

/* 결과 텍스트 스타일 */
.result-text {
    margin: 10px 0;
    padding: 10px;
    border-left: 4px solid #36A2EB;
    background-color: #f9f9f9;
}

/* 모바일 스타일 */
@media (max-width: 767px) {
    div[data-testid="stHorizontalBlock"] {
        display: grid !important;
        grid-template-columns: repeat(7, 1fr) !important;
        gap: 2px !important;
        justify-content: flex-start !important;
        margin-left: 0;
    }
    div[data-testid="stMarkdownContainer"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    div[data-testid="stMarkdownContainer"]:not(:has(.day-header)):not(:has(.day)) {
        justify-content: flex-start !important;
    }
    .day {
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        aspect-ratio: 1/1 !important;
        line-height: 40px !important;
        font-size: 1em;
        margin: 2px auto !important;
        padding: 15px !important;
        touch-action: manipulation !important;
    }
    .day:not(.disabled):hover::after,
    .day:not(.disabled):active::after {
        left: -10px;
        top: 20px;
    }
    .day.selected {
        border: 2px solid #ff4444 !important;
        font-weight: bold !important;
        background-color: #ffe6e6 !important;
    }
    .stCheckbox {
        width: 40px !important;
        height: 40px !important;
        left: 0 !important;
        top: 0 !important;
    }
    .stCheckbox > div > div {
        width: 40px !important;
        height: 40px !important;
    }
    .result-text {
        padding: 8px;
    }
}

/* 데스크탑 스타일 */
@media (min-width: 768px) {
    div[data-testid="stHorizontalBlock"] {
        max-width: 600px !important;
        margin: 0 !important;
        justify-content: flex-start !important;
    }
    .day.selected {
        border: 2px solid #ff4444 !important;
        font-weight: bold !important;
        background-color: #ffe6e6 !important;
    }
}

/* 모든 텍스트 왼쪽 정렬 */
.stMarkdown, .stText, .stHeader {
    text-align: left !important;
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark), [data-theme="dark"] {
    .day-header {
        color: #ddd;
        background-color: #444;
    }
    .day-header.weekend {
        color: #ff6666;
    }
    .day {
        background-color: #333;
        color: #ddd;
        border-color: #888;
    }
    .day:hover:not(.disabled) {
        background-color: #444;
    }
    .day:not(.disabled):hover::before {
        background-color: #555;
        color: #fff;
    }
    .day.disabled {
        background-color: #555;
        color: #888;
    }
    .day.selected {
        border: 2px solid #ff6666 !important;
        font-weight: bold !important;
        background-color: #4a2a2a !important;
    }
    .day.current {
        border-color: #6666ff;
    }
    .result-text {
        background-color: #2a2a2a;
        border-left-color: #4CAF50;
    }
    .stCheckbox > div > div {
        background-color: transparent !important;
    }
}

.day:hover:not(.disabled) {
    background-color: #f0f0f0;
}

.day.current {
    border: 2px solid #4444ff;
}

.day.disabled {
    background-color: #e0e0e0;
    color: #888;
    cursor: not-allowed;
}

