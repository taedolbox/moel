// static/sidebar_button.js
document.addEventListener('DOMContentLoaded', (event) => {
    function updateSidebarButtonText() {
        const sidebarButton = document.querySelector('button[aria-label="메뉴 열기"]');
        const sidebarButtonClosed = document.querySelector('button[aria-label="메뉴 닫기"]');

        if (sidebarButton) {
            sidebarButton.setAttribute('aria-label', '메뉴 열기');
            sidebarButton.innerHTML = '메뉴열기';
        }

        if (sidebarButtonClosed) {
            sidebarButtonClosed.setAttribute('aria-label', '메뉴 닫기');
            sidebarButtonClosed.innerHTML = '메뉴닫기';
        }
    }

    // Call the function initially
    updateSidebarButtonText();

    // Set up a MutationObserver to watch for changes in the DOM
    // This is important because Streamlit can re-render parts of the UI
    const observer = new MutationObserver(updateSidebarButtonText);
    const config = { childList: true, subtree: true };

    // Start observing the document body for changes
    observer.observe(document.body, config);
});
