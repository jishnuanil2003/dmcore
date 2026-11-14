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
