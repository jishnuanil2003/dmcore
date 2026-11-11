document.addEventListener('DOMContentLoaded', function () {
  // ===== DELETE main WorkAssign (all tasks) =====
  document.querySelectorAll('.delete-work-btn').forEach(button => {
    button.addEventListener('click', function () {
      const assignId = this.dataset.assignid;
      const taskId = this.dataset.taskid;
      const taskName = this.dataset.taskname;

      if (!confirm(`Delete task "${taskName}" from this assigned work?`)) return;

      fetch('/remove-task-from-assignment/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          assign_id: assignId,
          task_id: taskId,
          task_name: taskName
        })
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        if (data.success) location.reload();
      });
    });
  });

  // ===== EDIT CATEGORY modal =====
  document.querySelectorAll('.edit-category-btn').forEach(icon => {
    icon.addEventListener('click', function () {
      document.getElementById('modal_teamlead').value = this.dataset.teamlead;
      document.getElementById('modal_category').value = this.dataset.category;
      document.getElementById('modal_target').value = this.dataset.target;
      document.getElementById('modal_start').value = this.dataset.start;
      document.getElementById('modal_due').value = this.dataset.due;
      document.getElementById('modal_description').value = this.dataset.description;
      document.getElementById('edit_category_id').value = this.dataset.editid;
    
      // Get WorkAssign ID
      const assignId = this.dataset.assignid;
    
      // Fetch WorkAssign data (platforms, criteria, file)
      fetch(`/get-full-workassign/${assignId}/`)
        .then(res => res.json())
        .then(data => {
          console.log(" [DEBUG] WorkAssign Data Received:", data);  // ! DEBUG LINE =======================
          // Set criteria
          document.getElementById('modal_criteria').value = data.criteria || '';
        
          // Show/hide file download
          const fileBtn = document.getElementById('modal_existing_file');
          if (fileBtn) {
            if (data.file_url) {
              fileBtn.href = data.file_url;
              fileBtn.classList.remove('d-none');
            } else {
              fileBtn.classList.add('d-none');
            }
          }
        
          // Populate platform flags + targets
          ['instagram', 'facebook', 'x'].forEach(platform => {
            const isChecked = data[`is_${platform}`];
            const targetValue = data[`${platform}_target`] || '';
            const checkEl = document.getElementById(`modal_is_${platform}`);
            const targetEl = document.getElementById(`modal_${platform}_target`);
          
            if (checkEl && targetEl) {
              checkEl.checked = isChecked;
              targetEl.value = targetValue;
              targetEl.classList.toggle('d-none', !isChecked);
            }
          });
        
          new bootstrap.Modal(document.getElementById('editCategoryModal')).show();
        });
    });
  });


  document.getElementById('editCategoryForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/update-lead-category/', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      if (data.success) location.reload();
    });
  });

  // ===== ADD CATEGORY modal (open + populate) =====
  document.querySelectorAll('.add-category-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const assignId = this.dataset.assignid;
      const taskId = this.dataset.taskid;
      const assignType = this.dataset.assigntype;
      const teamLeadId = this.dataset.tlid;
      const tlName = this.closest('td').querySelector('a')?.textContent.trim() || 'Team Lead';

      document.getElementById('add_assign_id').value = assignId;
      document.getElementById('add_task_id').value = taskId;
      document.getElementById('add_assign_type').value = assignType;
      document.getElementById('add_teamlead_id').value = teamLeadId;
      document.getElementById('add_teamlead_display').value = tlName;

      // Hide file download (no existing file)
      const fileBtn = document.getElementById('add_existing_file');
      if (fileBtn) fileBtn.classList.add('d-none');

      const group = document.getElementById('category_checkbox_group');
      group.innerHTML = '<em class="text-muted small">Loading categories...</em>';

      fetch(`/get-lead-categories/${assignId}/`)
        .then(res => res.json())
        .then(data => {
          group.innerHTML = '';
          const categories = data.categories || [];
          if (!categories.length) {
            group.innerHTML = '<em class="text-danger">No categories available.</em>';
            return;
          }
          categories.forEach(cat => {
            const wrapper = document.createElement('div');
            wrapper.className = 'form-check form-check-inline me-3';
            wrapper.innerHTML = `
              <input class="form-check-input" type="checkbox" name="category" value="${cat.id}" id="cat-${cat.id}">
              <label class="form-check-label" for="cat-${cat.id}">${cat.name}</label>
            `;
            group.appendChild(wrapper);
          });
        })
        .catch(err => {
          group.innerHTML = '<em class="text-danger">Error loading categories.</em>';
        });

      fetch(`/get-teamlead-name/${teamLeadId}/`)
        .then(res => res.json())
        .then(data => {
          document.getElementById('add_teamlead_display').value = data.name || 'Team Lead';
        });

      new bootstrap.Modal(document.getElementById('addCategoryModal')).show();
    });
  });

  // ===== ADD CATEGORY form submit =====
  document.getElementById('addCategoryForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/add-category-to-work/', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      if (data.success) location.reload();
    });
  });

  // ===== DELETE category from TL work =====
  document.querySelectorAll('.delete-task-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const categoryId = this.dataset.categoryid;
      if (!confirm("Are you sure you want to delete this category assignment?")) return;

      fetch(`/delete-lead-category/${categoryId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
      })
      .then(res => res.json())
      .then(data => {
        alert(data.message);
        if (data.success) location.reload();
      });
    });
  });

  // ===== Reset Add Category form =====
  document.getElementById('clearAddCategoryFormBtn').addEventListener('click', () => {
    const form = document.getElementById('addCategoryForm');
    const readonlyValues = {
      teamlead: document.getElementById('add_teamlead_display').value,
      task: document.getElementById('add_task_name_display')?.value || ''
    };
    form.reset();
    document.getElementById('add_teamlead_display').value = readonlyValues.teamlead;
    if (document.getElementById('add_task_name_display')) {
      document.getElementById('add_task_name_display').value = readonlyValues.task;
    }

    ['instagram', 'facebook', 'x'].forEach(platform => {
      document.getElementById(`add_${platform}_target`).classList.add('d-none');
    });
  });

  // ===== Reset Edit Category form =====
  document.getElementById('clearEditCategoryFormBtn').addEventListener('click', () => {
    const form = document.getElementById('editCategoryForm');
    const readonlyValues = {
      teamlead: document.getElementById('modal_teamlead').value,
      category: document.getElementById('modal_category').value
    };
    form.reset();
    document.getElementById('modal_teamlead').value = readonlyValues.teamlead;
    document.getElementById('modal_category').value = readonlyValues.category;

    ['instagram', 'facebook', 'x'].forEach(platform => {
      document.getElementById(`modal_${platform}_target`).classList.add('d-none');
    });
  });



  // ===== Platform Toggles (EDIT modal) =====
['instagram', 'facebook', 'x'].forEach(platform => {
  const checkbox = document.getElementById(`modal_is_${platform}`);
  const input = document.getElementById(`modal_${platform}_target`);
  if (checkbox && input) {
    checkbox.addEventListener('change', function () {
      input.classList.toggle('d-none', !this.checked);
    });
  }
});


  // ===== Platform Toggles (ADD modal) =====
['instagram', 'facebook', 'x'].forEach(platform => {
  const checkbox = document.getElementById(`add_is_${platform}`);
  const input = document.getElementById(`add_${platform}_target`);
  if (checkbox && input) {
    checkbox.addEventListener('change', function () {
      input.classList.toggle('d-none', !this.checked);
    });
  }
});

});
