// static/sidebar_button.js
document.addEventListener('DOMContentLoaded', (event) => {
    function updateSidebarButtonText() {
        // 사이드바 열기 버튼 찾기 (초기 상태 또는 닫힌 상태)
        let sidebarButtonOpen = document.querySelector('button[aria-label="메뉴 열기"]');
        // 사이드바 닫기 버튼 찾기 (열린 상태)
        let sidebarButtonClose = document.querySelector('button[aria-label="메뉴 닫기"]');

        // Streamlit 1.x 버전에서는 data-testid를 사용할 수도 있습니다.
        // aria-label을 찾지 못했을 경우 data-testid로 시도
        if (!sidebarButtonOpen && !sidebarButtonClose) {
            const genericButton = document.querySelector('button[data-testid="stSidebarCollapseButton"]');
            if (genericButton) {
                if (genericButton.getAttribute('aria-expanded') === 'false') {
                    sidebarButtonOpen = genericButton;
                } else if (genericButton.getAttribute('aria-expanded') === 'true') {
                    sidebarButtonClose = genericButton;
                }
            }
        }

        // 버튼 텍스트와 aria-label 업데이트
        if (sidebarButtonOpen) {
            sidebarButtonOpen.setAttribute('aria-label', '메뉴 열기');
            sidebarButtonOpen.innerHTML = '메뉴열기';
        }

        if (sidebarButtonClose) {
            sidebarButtonClose.setAttribute('aria-label', '메뉴 닫기');
            sidebarButtonClose.innerHTML = '메뉴닫기';
        }
    }

    // 초기 실행
    updateSidebarButtonText();

    // MutationObserver를 사용하여 DOM 변경 감지
    // Streamlit이 UI를 다시 렌더링할 때 버튼 텍스트가 유지되도록 합니다.
    const observer = new MutationObserver(updateSidebarButtonText);
    // childList: 자식 노드 추가/제거 감지
    // subtree: 모든 후손 노드 감지
    // attributes: 속성 변경 감지 (aria-expanded 등)
    // attributeFilter: 특정 속성만 감지하여 성능 최적화
    const config = { childList: true, subtree: true, attributes: true, attributeFilter: ['aria-expanded', 'aria-label'] };

    // document.body를 관찰 시작 (전체 문서의 변경을 감시)
    observer.observe(document.body, config);
});
