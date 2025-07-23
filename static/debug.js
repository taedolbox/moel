console.log("Custom header element:", document.querySelector(".custom-header"));
console.log("stAppHeader element:", document.querySelector(".stAppHeader"));
console.log("stToolbar element:", document.querySelector("[data-testid='stToolbar']"));
console.log("stMainMenu element:", document.querySelector("[data-testid='stMainMenu']"));

if (!document.querySelector(".custom-header")) {
    console.error("Custom header not found in DOM");
} else {
    const header = document.querySelector(".custom-header");
    console.log("Custom header styles:", getComputedStyle(header));
    console.log("Custom header position:", header.getBoundingClientRect());
}

if (document.querySelector(".stAppHeader")) {
    console.log("stAppHeader styles:", getComputedStyle(document.querySelector(".stAppHeader")));
    document.querySelector(".stAppHeader").style.display = "none";
}
if (document.querySelector("[data-testid='stToolbar']")) {
    console.log("stToolbar styles:", getComputedStyle(document.querySelector("[data-testid='stToolbar']")));
    document.querySelector("[data-testid='stToolbar']").style.display = "none";
}
if (document.querySelector("[data-testid='stMainMenu']")) {
    console.log("stMainMenu styles:", getComputedStyle(document.querySelector("[data-testid='stMainMenu']")));
    document.querySelector("[data-testid='stMainMenu']").style.display = "none";
}

// 추가: 동적 클래스 포함 모든 헤더 요소 숨김
document.querySelectorAll("[class*='stAppHeader'], [class*='stToolbar'], [class*='stMainMenu']").forEach(el => {
    el.style.display = "none";
});
