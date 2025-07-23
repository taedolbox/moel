function hideElements(selector, context) {
    context.querySelectorAll(selector).forEach(el => {
        el.style.display = "none";
        console.log(`Hid element: ${selector}`, el);
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
            "[class*='st-emotion-cache'][data-testid*='MainMenu']"
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

        // 콤보박스 스타일 확인
        const selectBox = ctx.querySelector("[data-testid='stSelectbox']");
        if (selectBox) {
            console.log("Selectbox found:", selectBox);
            console.log("Selectbox styles:", getComputedStyle(selectBox));
        } else {
            console.error("Selectbox not found in context");
        }
    });
}

// DOM 로드 후 실행
document.addEventListener("DOMContentLoaded", debugElements);
setTimeout(debugElements, 1000); // 지연 실행으로 동적 로드 대응
