document.addEventListener('DOMContentLoaded', function() {
    // Animate progress bars
    document.querySelectorAll('.progress-bar').forEach(bar => {
        const value = parseInt(bar.dataset.progress) || 0;
        bar.style.width = value + '%';

        // if (value < 40) {
        //     bar.classList.add('bg-danger');
        // } else if (value < 70) {
        //     bar.classList.add('bg-warning');
        // } else {
            bar.classList.add('bg-success');
        // }
    });

    // Handle main work edit buttons
    document.querySelectorAll('.edit-work-icon').forEach(icon => {
    icon.addEventListener('click', function () {
        const workId = this.dataset.id;

        fetch(`/get-work/${workId}/`)
            .then(res => res.json())
            .then(data => {
                // Populate form
                document.getElementById('edit_work_id').value = workId;
                document.getElementById('edit_start_date').value = data.start_date || '';
                document.getElementById('edit_end_date').value = data.end_date || '';
                document.getElementById('edit_work_description').value = data.description || '';

                const downloadLink = document.getElementById('edit_work_file_download');
                if (data.work_file_url) {
                    downloadLink.href = data.work_file_url;
                    downloadLink.classList.remove('d-none');
                } else {
                    downloadLink.classList.add('d-none');
                }

                const modal = new bootstrap.Modal(document.getElementById('editWorkModal'));
                modal.show();
            });
        });
    });
    const editWorkForm = document.getElementById('editWorkForm');
    if (editWorkForm) editWorkForm.addEventListener('submit', function (e) {
        e.preventDefault();const form = e.target;
        const formData = new FormData(form);
        fetch('/edit-work/', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            if (data.success) location.reload();
        });
    });

    // Handle main work delete buttons
    document.querySelectorAll('.delete-work-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const workId = this.dataset.id;
            if (confirm('Are you sure you want to delete this work?')) {
                fetch(`/delete-work/${workId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) location.reload();
                });
            }
        });
    });


    // Handle edit icons for tasks
    document.querySelectorAll('.edit-task-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const taskId = this.dataset.id;

            fetch(`/get-task/${taskId}/`)
                .then(res => res.json())
                .then(data => {
                    document.getElementById('edit_task_id').value = taskId;
                    document.getElementById('edit_task_client').value = data.client_name;
                    document.getElementById('edit_task_name').value = data.task_name;
                    document.getElementById('edit_task_description').value = data.task_description || '';
                    document.getElementById('edit_task_is_common').value = data.is_common ? '1' : '0';

                    // Disable task name if it's a company task
                    const taskInput = document.getElementById('edit_task_name');
                    taskInput.readOnly = data.is_common;

                    const downloadBtn = document.getElementById('edit_task_file_download');
                    if (data.task_file_url) {
                        downloadBtn.href = data.task_file_url;
                        downloadBtn.classList.remove('d-none');
                    } else {
                        downloadBtn.classList.add('d-none');
                    }

                    const modal = new bootstrap.Modal(document.getElementById('editTaskModal'));
                    modal.show();
                });
        });
    });

    const editTaskForm = document.getElementById('editTaskForm');
    if (editTaskForm) editTaskForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/edit-task/', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if (data.success) location.reload();
            });
    });

    // Handle Task delete buttons
    document.querySelectorAll('.delete-task-icon').forEach(icon => {
        icon.addEventListener('click', function () {
            const taskId = this.dataset.id;
            if (confirm('Are you sure you want to delete this task?')) {
                fetch(`/delete-task/${taskId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    if (data.success) location.reload();
                });
            }
        });
    });



    // Handle add-task button
    document.querySelectorAll('#addTaskBtn').forEach(btn => {
        btn.addEventListener('click', function () {
            const workId = this.dataset.workid;
            document.getElementById('add_task_work_id').value = workId;
        
            // Reset form
            document.getElementById('addMoreTaskForm').reset();
            document.getElementById('clientTaskInput').classList.remove('d-none');
            document.getElementById('companyTaskDropdown').classList.add('d-none');
            document.getElementById('taskTypeClient').checked = true;
        
            // Fetch available tasks
            fetch(`/get-tasks/?work_id=${workId}`)
                .then(res => res.json())
                .then(data => {
                    const dropdown = document.getElementById('taskDropdown');
                    dropdown.innerHTML = '<option selected disabled>---- Select Task ----</option>';
                    data.tasks.forEach(task => {
                        dropdown.innerHTML += `<option value="${task.id}">${task.name}</option>`;
                    });
                });
            
            const modal = new bootstrap.Modal(document.getElementById('addMoreTaskModal'));
            modal.show();
        });
    });
    
    // Toggle between input and dropdown
    document.querySelectorAll('input[name="task_type"]').forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'client') {
                document.getElementById('clientTaskInput').classList.remove('d-none');
                document.getElementById('companyTaskDropdown').classList.add('d-none');
            } else {
                document.getElementById('clientTaskInput').classList.add('d-none');
                document.getElementById('companyTaskDropdown').classList.remove('d-none');
            }
        });
    });
    
    // Submit form
    const addMoreTaskForm = document.getElementById('addMoreTaskForm');
    if (addMoreTaskForm) addMoreTaskForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);
    
        fetch('/add-more-task/', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if (data.success) location.reload();
            });
    });


    // Handle add-lead-category button
    document.querySelectorAll('.add-category-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const taskId = this.dataset.taskid;
            document.getElementById('category_task_id').value = taskId;
            document.getElementById('addCategoryForm').reset();
            const modal = new bootstrap.Modal(document.getElementById('addCategoryModal'));
            modal.show();
        });
    });

    const addCategoryForm = document.getElementById('addCategoryForm');
    if (addCategoryForm) addCategoryForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const formData = new FormData(this);

        fetch('/add-lead-category/', {
            method: 'POST',
            body: formData
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if (data.success) location.reload();
            });
    });

    // edit lead category
    document.querySelectorAll('.edit-category-icon').forEach(icon => {
      icon.addEventListener('click', function () {
        const categoryId = this.dataset.id;

        fetch(`/get-category/${categoryId}/`)
          .then(res => res.json())
          .then(data => {
            document.getElementById('edit_category_id').value = categoryId;
            document.getElementById('edit_category_head').value = data.collection_for;
            document.getElementById('edit_category_description').value = data.description || '';
            document.getElementById('edit_category_target').value = data.target || '';

            const downloadBtn = document.getElementById('edit_category_file_download');
            if (data.file_url) {
              downloadBtn.href = data.file_url;
              downloadBtn.classList.remove('d-none');
            } else {
              downloadBtn.classList.add('d-none');
            }

            new bootstrap.Modal(document.getElementById('editCategoryModal')).show();
          });
      });
    });
    
    const editCategoryForm = document.getElementById('editCategoryForm');
    if (editCategoryForm) editCategoryForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(this);

      fetch('/edit-category/', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          alert(data.message);
          if (data.success) location.reload();
        });
    });



    // delete Lead category
    document.querySelectorAll('.delete-category-icon').forEach(icon => {
      icon.addEventListener('click', function () {
        const categoryId = this.dataset.id;
        if (confirm('Are you sure you want to delete this category?')) {
          fetch(`/delete-category/${categoryId}/`, {
            method: 'POST',
            headers: {
              'X-Requested-With': 'XMLHttpRequest'
            }
          })
            .then(res => res.json())
            .then(data => {
              alert(data.message);
              if (data.success) location.reload();
            });
        }
      });
    });



    // Handle add-fields button
    document.querySelectorAll('.edit-field-icon').forEach(icon => {
      icon.addEventListener('click', function () {
        const fieldId = this.dataset.id;
    
        fetch(`/get-field/${fieldId}/`)
          .then(res => res.json())
          .then(data => {
            document.getElementById('edit_field_id').value = fieldId;
            document.getElementById('edit_field_name').value = data.name;
            document.getElementById('edit_field_description').value = data.description || '';
        
            // Prevent editing name if it's a default field
            const fieldInput = document.getElementById('edit_field_name');
            const isDefault = ["full name", "email", "contact number"].includes(data.name.trim().toLowerCase());
            fieldInput.readOnly = isDefault;
        
            new bootstrap.Modal(document.getElementById('editFieldModal')).show();
          });
      });
    });
    
    const editFieldForm = document.getElementById('editFieldForm');
    if (editFieldForm) editFieldForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(this);
    
      fetch('/edit-field/', {
        method: 'POST',
        body: formData
      })
        .then(res => res.json())
        .then(data => {
          alert(data.message);
          if (data.success) location.reload();
        });
    });

});
