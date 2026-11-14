const toggleBtn = document.getElementById('toggleSidebar');
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('main-content');

toggleBtn.addEventListener('click', () => {
  if (window.innerWidth < 768) {
    sidebar.classList.toggle('show');
    sidebar.classList.toggle('d-none');
    sidebar.classList.toggle('d-block');
  } else {
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('full');
  }
});

window.addEventListener('resize', () => {
  if (window.innerWidth >= 768) {
    sidebar.classList.remove('d-none', 'd-block', 'show', 'collapsed');
    mainContent.classList.remove('full');
  } else {
    sidebar.classList.add('d-none');
  }
});
