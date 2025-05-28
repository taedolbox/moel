function toggleSidebar() {
  const sidebar = document.querySelector('.stSidebar');
  const button = document.querySelector('.toggle-btn');
  sidebar.classList.toggle('collapsed');
  button.textContent = sidebar.classList.contains('collapsed') ? '메뉴열기' : '메뉴닫기';
}
