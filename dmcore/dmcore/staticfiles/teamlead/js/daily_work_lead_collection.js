document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.progress-bar').forEach(bar => {
      const value = parseInt(bar.dataset.progress || '0');
      bar.style.width = `${value}%`;
      bar.innerText = `${value}%`;
      bar.setAttribute('aria-valuenow', value);
    });

    document.querySelectorAll('.btn-outline-info.btn-sm').forEach(btn => {
      if (btn.innerText.trim().toLowerCase() === "add") {
        btn.addEventListener('click', () => {
          new bootstrap.Modal(document.getElementById('addLeadDailyModal')).show();
        });
      }
    });
  });