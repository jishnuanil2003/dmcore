document.addEventListener('DOMContentLoaded', () => {

  document.querySelectorAll('.progress-bar').forEach(bar => {
    const value = parseInt(bar.dataset.progress || '0');
    bar.style.width = `${value}%`;
    bar.innerText = `${value}%`;
    bar.setAttribute('aria-valuenow', value);
  });

  document.querySelectorAll('.view-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.getElementById('v_client').value = btn.dataset.client || '';
      document.getElementById('v_allocated').value = btn.dataset.assign || '';
      document.getElementById('v_accepted').value = btn.dataset.accept || '';
      const rawTaskName = btn.dataset.name || '';
      const taskType = btn.dataset.type || '';
      document.getElementById('v_taskname').value = taskType === 'lead_collection' ? `Lead Collection : ${rawTaskName}` : rawTaskName;
      document.getElementById('v_target').value = btn.dataset.target || '';
      document.getElementById('v_achieved').value = btn.dataset.achieved || '';
      document.getElementById('v_start').value = btn.dataset.start || '';
      document.getElementById('v_end').value = btn.dataset.end || '';
      document.getElementById('v_description').value = btn.dataset.description || '';
      document.getElementById('v_instagram').parentElement.style.display =
        btn.dataset.instagramShow === '1' ? 'block' : 'none';
      document.getElementById('v_facebook').parentElement.style.display =
        btn.dataset.facebookShow === '1' ? 'block' : 'none';
      document.getElementById('v_twitter').parentElement.style.display =
        btn.dataset.twitterShow === '1' ? 'block' : 'none';
          
      document.getElementById('v_instagram').value = btn.dataset.instagram || '';
      document.getElementById('v_facebook').value = btn.dataset.facebook || '';
      document.getElementById('v_twitter').value = btn.dataset.twitter || '';

      const file = btn.dataset.file;
      const box = document.getElementById('v_file_box');
      const link = document.getElementById('v_file_link');
      if (file) {
        link.href = file;
        box.style.display = 'block';
      } else {
        box.style.display = 'none';
      }

      new bootstrap.Modal(document.getElementById('viewTaskModal')).show();
    });
  });

  // Add Daily Work Modal
  document.querySelectorAll('.add-daily-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const taskName = btn.dataset.name || '';
      const assignId = btn.dataset.assignid || '';

      document.getElementById('d_taskname').value = taskName;
      const hidden = document.getElementById('task_assign_id');
      if (hidden) hidden.value = assignId;

      new bootstrap.Modal(document.getElementById('addDailyModal')).show();
    });
  });
});
