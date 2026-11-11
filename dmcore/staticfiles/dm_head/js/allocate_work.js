document.addEventListener('DOMContentLoaded', function () {
  const categorySection = document.getElementById('lead_category_section');
  const categoryDropdown = document.getElementById('category_select');
  const taskDropdown = document.getElementById('task_select');
  const workInput = document.getElementById('modal_work_id');
  const hiddenTaskInput = document.getElementById('hidden_task_id');
  const allocateForm = document.getElementById('allocateWorkForm');
  const searchInput = document.getElementById('searchInput');
  const table = document.getElementById('workTable');

  let allTaskData = [];

  // Trigger allocate modal
  document.querySelectorAll('.allocate-btn').forEach(button => {
    button.addEventListener('click', function () {
      const workId = this.dataset.workid;
      workInput.value = workId;
      taskDropdown.innerHTML = '<option disabled selected>Select Task</option>';
      categoryDropdown.innerHTML = '';
      categorySection.classList.add('d-none');
      hiddenTaskInput.value = '';

      fetch(`/get-tasks-for-work/${workId}/`)
        .then(res => res.json())
        .then(data => {
          allTaskData = data.tasks || [];
          allTaskData.forEach(task => {
            const opt = document.createElement('option');
            opt.value = task.id;
            opt.textContent = task.name;
            opt.dataset.isLead = task.is_lead_collection;
            opt.dataset.categories = JSON.stringify(task.categories || []);
            taskDropdown.appendChild(opt);
          });

          new bootstrap.Modal(document.getElementById('allocateWorkModal')).show();
        });
    });
  });

  // Populate categories on task change
  taskDropdown.addEventListener('change', function () {
    const selected = this.options[this.selectedIndex];
    if (!selected) return;

    const isLead = selected.dataset.isLead === 'true';
    const categories = JSON.parse(selected.dataset.categories || '[]');
    hiddenTaskInput.value = selected.value;
    categoryDropdown.innerHTML = '';

    if (isLead && categories.length > 0) {
      categorySection.classList.remove('d-none');
      categoryDropdown.removeAttribute('disabled');
      categoryDropdown.setAttribute('required', 'required');
      categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = cat.name;
        categoryDropdown.appendChild(opt);
      });
    } else {
      categorySection.classList.add('d-none');
      categoryDropdown.setAttribute('disabled', 'disabled');
      categoryDropdown.removeAttribute('required');
    }

    hiddenTaskInput.value = selected.value;
    categoryDropdown.innerHTML = '';

    if (isLead && categories.length > 0) {
      categorySection.classList.remove('d-none');
      categoryDropdown.removeAttribute('disabled');
      categoryDropdown.setAttribute('required', 'required');
      categories.forEach(cat => {
        const opt = document.createElement('option');
        opt.value = cat.id;
        opt.textContent = cat.name;
        categoryDropdown.appendChild(opt);
      });
    
      document.getElementById('criteria_section').classList.remove('d-none');
    
    } else {
      categorySection.classList.add('d-none');
      categoryDropdown.setAttribute('disabled', 'disabled');
      categoryDropdown.removeAttribute('required');
    
      document.getElementById('criteria_section').classList.add('d-none');
    }

  });
  

  // Form submission
  allocateForm.addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(allocateForm);

    fetch('/submit-work-allocation/', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        if (data.success) {
          bootstrap.Modal.getInstance(document.getElementById('allocateWorkModal')).hide();
          setTimeout(() => location.reload(), 500);
        }
      })
      .catch(() => alert('Something went wrong. Please try again.'));
  });

  // Delete TL assignment
  document.querySelectorAll('.delete-assign-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const workId = this.dataset.workid;
      const tlId = this.dataset.tlid;

      if (!confirm("Delete all assignments for this Team Lead under this work?")) return;

      fetch(`/delete-all-tasks-for-tl/${workId}/${tlId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        if (data.success) location.reload();
      });
    });
  });

  // Live table search
  if (searchInput && table) {
    searchInput.addEventListener('input', () => {
      const term = searchInput.value.toLowerCase();
      Array.from(table.tBodies[0].rows).forEach(row => {
        const match = row.innerText.toLowerCase().includes(term);
        row.style.display = match ? '' : 'none';
      });
    });
  }

  // Set progress bar widths
  document.querySelectorAll('.progress-bar').forEach(bar => {
    const value = parseInt(bar.dataset.progress) || 0;
    bar.style.width = value + '%';
    bar.textContent = value + '%';
  });
});

['instagram', 'facebook', 'x'].forEach(platform => {
  const box = document.getElementById(`is_${platform}`);
  const input = box.nextElementSibling.nextElementSibling;
  box.addEventListener('change', () => {
    if (box.checked) {
      input.classList.remove('d-none');
    } else {
      input.classList.add('d-none');
      input.value = '';
    }
  });
});
