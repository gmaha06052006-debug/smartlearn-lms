/**
 * SmartLearn — Interactive client-side scripts
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Sidebar Toggle
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const sidebarBackdrop = document.getElementById('sidebarBackdrop');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('show');
    if (sidebarBackdrop) sidebarBackdrop.classList.remove('d-none');
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('show');
    if (sidebarBackdrop) sidebarBackdrop.classList.add('d-none');
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      if (sidebar.classList.contains('show')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (sidebarBackdrop) {
    sidebarBackdrop.addEventListener('click', closeSidebar);
  }

  // 2. Interactive Lesson Progress Toggle (AJAX)
  const progressButtons = document.querySelectorAll('.js-toggle-lesson-btn');
  progressButtons.forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const url = this.getAttribute('data-url');
      const lessonId = this.getAttribute('data-lesson-id');

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'ok') {
          // Toggle UI state
          if (data.completed) {
            btn.classList.remove('btn-outline-pill');
            btn.classList.add('btn-accent');
            btn.innerHTML = '<i class="bi bi-check-circle-fill"></i> Completed';
          } else {
            btn.classList.add('btn-outline-pill');
            btn.classList.remove('btn-accent');
            btn.innerHTML = '<i class="bi bi-circle"></i> Mark as Complete';
          }
          // Update progress percentage if element exists
          const progressEl = document.getElementById('courseProgressBar');
          if (progressEl) {
            progressEl.style.width = data.progress_percent + '%';
            const textEl = document.getElementById('courseProgressText');
            if (textEl) textEl.innerText = data.progress_percent + '%';
          }
        }
      })
      .catch(err => console.error('Error toggling progress:', err));
    });
  });

  // Helper to read CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
