function hideElements(selector, context) {
    context.querySelectorAll(selector).forEach(el => {
        el.style.display = "none";
        console.log(`Hid element: ${selector}`, el);
    });
}

function applySelectboxStyles(context) {
    const selectBoxes = context.querySelectorAll(
        "[data-testid='stSelectbox'], [data-testid='stSelectbox'] > div, " +
        "div[data-baseweb='select'], div[data-baseweb='select'] > div, " +
        "[data-testid='stSelectbox'] [role='combobox'], " +
        "[class*='st-emotion-cache'][data-testid='stSelectbox'], " +
        "[class*='st-emotion-cache'] [role='combobox']"
    );
    selectBoxes.forEach(el => {
        el.style.border = "2px solid #2196F3";
        el.style.color = "#2196F3";
        el.style.backgroundColor = "#E3F2FD";
        el.style.fontWeight = "600";
        el.style.borderRadius = "4px";
        el.style.zIndex = "2";
        console.log("Applied styles to selectbox:", el);
    });

    const selectSpans = context.querySelectorAll(
        "[data-testid='stSelectbox'] span, div[data-baseweb='select'] span, " +
        "[class*='st-emotion-cache'] span"
    );
    selectSpans.forEach(span => {
        span.style.color = "#2196F3";
        span.style.fontWeight = "600";
        console.log("Applied styles to selectbox span:", span);
    });
}

function debugElements() {
    // 현재 문서, 부모 문서, 최상위 문서 검사
    const contexts = [document, window.parent?.document, window.top?.document].filter(ctx => ctx);
    contexts.forEach(ctx => {
        console.log("Inspecting context:", ctx === document ? "current" : ctx === window.parent?.document ? "parent" : "top");

        // Custom header
        const customHeader = ctx.querySelector(".custom-header");
        if (customHeader) {
            console.log("Custom header found:", customHeader);
            console.log("Custom header styles:", getComputedStyle(customHeader));
            console.log("Custom header position:", customHeader.getBoundingClientRect());
        } else {
            console.error("Custom header not found in context");
        }

        // Streamlit 헤더 및 툴바
        const selectors = [
            ".stAppHeader",
            "[data-testid*='Header']",
            "[data-testid*='Toolbar']",
            "[data-testid*='MainMenu']",
            "[class*='stAppHeader']",
            "[class*='stToolbar']",
            "[class*='stMainMenu']",
            "[class*='st-emotion-cache'][data-testid*='Header']",
            "[class*='st-emotion-cache'][data-testid*='Toolbar']",
            "[class*='st-emotion-cache'][data-testid*='MainMenu']",
            "[data-testid*='st']",
            "header[data-testid]",
            "div[data-testid*='Toolbar']",
            "div[data-testid*='MainMenu']"
        ];

        selectors.forEach(selector => {
            hideElements(selector, ctx);
            const elements = ctx.querySelectorAll(selector);
            if (elements.length > 0) {
                console.log(`${selector} elements found:`, elements);
                elements.forEach(el => {
                    console.log(`${selector} styles:`, getComputedStyle(el));
                });
            }
        });

        // 콤보박스 스타일 적용 및 확인
        applySelectboxStyles(ctx);
        const selectBox = ctx.querySelector("[data-testid='stSelectbox']");
        if (selectBox) {
            console.log("Selectbox found:", selectBox);
            console.log("Selectbox styles:", getComputedStyle(selectBox));
        } else {
            console.error("Selectbox not found in context");
        }
    });

    // Streamlit 버전 및 iframe 정보
    console.log("Streamlit version:", window.Streamlit ? window.Streamlit.version : "Unknown");
    console.log("Is in iframe:", window.self !== window.top);
}

// DOM 로드 후 실행 및 주기적 실행
document.addEventListener("DOMContentLoaded", debugElements);
setInterval(debugElements, 1000); // 동적 로드 대응
