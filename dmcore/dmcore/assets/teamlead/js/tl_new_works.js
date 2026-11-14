document.addEventListener('DOMContentLoaded', () => {
  const modal = new bootstrap.Modal(document.getElementById('taskDetailModal'));

  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('modalClientName').value = btn.dataset.client || '';
      document.getElementById('modalAssignDate').value = btn.dataset.assign || '';
      const rawTaskName = btn.dataset.name || '';
      const taskType = btn.dataset.type || '';
      const formattedName = taskType === 'lead_collection' ? `Lead Collection : ${rawTaskName}` : rawTaskName;
      document.getElementById('modalTaskName').value = formattedName;

      document.getElementById('modalTarget').value = btn.dataset.target || '';
      document.getElementById('modalStartDate').value = btn.dataset.start || '';
      document.getElementById('modalEndDate').value = btn.dataset.end || '';
      document.getElementById('modalDescription').value = btn.dataset.description || '';
      document.getElementById('v_instagram').parentElement.style.display =
        btn.dataset.instagramShow === '1' ? 'block' : 'none';
      document.getElementById('v_facebook').parentElement.style.display =
        btn.dataset.facebookShow === '1' ? 'block' : 'none';
      document.getElementById('v_twitter').parentElement.style.display =
        btn.dataset.twitterShow === '1' ? 'block' : 'none';
          
      document.getElementById('v_instagram').value = btn.dataset.instagram || '';
      document.getElementById('v_facebook').value = btn.dataset.facebook || '';
      document.getElementById('v_twitter').value = btn.dataset.twitter || '';

      const fileLink = btn.dataset.file;
      const linkEl = document.getElementById('modalDownloadLink');
      if (fileLink) {
        linkEl.href = fileLink;
        linkEl.parentElement.style.display = 'block';
      } else {
        linkEl.parentElement.style.display = 'none';
      }

      modal.show();
    });
  });
});
