// static/sidebar_button.js
document.addEventListener('DOMContentLoaded', (event) => {
    function updateSidebarButtonText() {
        // data-testid를 사용하여 버튼을 직접 찾습니다.
        // 이 data-testid는 사용자님이 제공해주신 HTML에서 확인된 값입니다.
        const sidebarButton = document.querySelector('button[data-testid="stBaseButton-headerNoPadding"]');

        if (sidebarButton) {
            // aria-expanded 속성을 통해 사이드바가 열려있는지 닫혀있는지 확인합니다.
            // 사이드바가 열리면 'true', 닫히면 'false' 값을 가집니다.
            const isSidebarExpanded = sidebarButton.getAttribute('aria-expanded') === 'true';

            if (isSidebarExpanded) {
                sidebarButton.setAttribute('aria-label', '메뉴 닫기');
                sidebarButton.innerHTML = '메뉴닫기';
            } else {
                sidebarButton.setAttribute('aria-label', '메뉴 열기');
                sidebarButton.innerHTML = '메뉴열기';
            }
        }
    }

    // 초기 실행
    updateSidebarButtonText();

    // MutationObserver를 사용하여 DOM 변경 감지
    // 특히 aria-expanded 속성 변경을 감지해야 합니다.
    const observer = new MutationObserver(updateSidebarButtonText);
    const config = {
        childList: true,   // 자식 노드 변경 감지
        subtree: true,     // 모든 하위 노드까지 감지
        attributes: true,  // 속성 변경 감지
        attributeFilter: ['aria-expanded', 'aria-label'] // aria-expanded와 aria-label 속성만 필터링하여 효율성 높임
    };

    // document.body 전체를 관찰 시작 (Streamlit의 동적 렌더링에 대응)
    observer.observe(document.body, config);
});
