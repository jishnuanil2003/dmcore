document.addEventListener('DOMContentLoaded', function () {
  // === View Task Details Modal ===
  document.querySelectorAll('.view-task-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const clientName = this.dataset.clientname;
      const allocatedDate = this.dataset.date;
      const taskName = this.dataset.taskname;
      const assignId = this.dataset.assignid;
      const isCategory = this.dataset.isCategory === '1';

      const categoryId = this.dataset.categoryid || null;
      const taskId = this.dataset.taskid || null;
      const categoryName = this.dataset.categoryname || null;

      document.getElementById('view_client_name').value = clientName;
      document.getElementById('view_allocated_date').value = allocatedDate;
      document.getElementById('view_description').value = 'Loading...';

      const taskUl = document.getElementById('view_task_details');
      taskUl.innerHTML = '';

      if (isCategory && categoryName) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>Lead Collection</strong><ul><li>${categoryName}</li></ul>`;
        taskUl.appendChild(li);
      } else {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${taskName}</strong>`;
        taskUl.appendChild(li);
      }

      const fileSection = document.createElement('div');
      fileSection.id = 'view_file_download';
      fileSection.className = 'mt-2';
      const modalBody = document.querySelector('#viewTaskDetailsModal .modal-body');
      const existing = document.getElementById('view_file_download');
      if (existing) existing.remove();
      modalBody.appendChild(fileSection);

      let fetchUrl = '';
      if (isCategory && categoryId) {
        fetchUrl = `/get-lead-team-alloc-desc/${categoryId}/${assignId}/`;
      } else if (!isCategory && taskId) {
        fetchUrl = `/get-workassign-desc/${assignId}/`;
      }

      if (fetchUrl) {
        fetch(fetchUrl)
          .then(res => res.json())
          .then(data => {
            console.log('Fetched Data:', data);
            document.getElementById('view_description').value = data.description || 'No description available';

            if (data.file_url) {
              fileSection.innerHTML = `
                <label class="form-label">File</label><br>
                <a href="${data.file_url}" target="_blank" class="text-info">Download File</a>
              `;
            }
          })
          .catch(err => {
            console.log('Fetch Error:', err);
            document.getElementById('view_description').value = 'Error loading details.';
          });
      }

      new bootstrap.Modal(document.getElementById('viewTaskDetailsModal')).show();
    });
  });

  // === Assign Modal ===
document.querySelectorAll('.assign-btn').forEach(btn => {
  btn.addEventListener('click', function () {
    const taskId = this.dataset.taskid;
    const categoryId = this.dataset.categoryid;
    const taskName = this.dataset.taskname;
    const assignId = this.dataset.teamallocid;
    const tlId = this.dataset.teamleadid;

    console.log('[DEBUG] Assign Modal Opened');
    console.log('Task ID:', taskId);
    console.log('Category ID:', categoryId);
    console.log('Task Name:', taskName);
    console.log('Team Allocation ID:', assignId);
    console.log('Team Lead ID:', tlId);

    document.getElementById('assign_task_id').value = taskId || '';
    document.getElementById('team_allocation_id').value = assignId;
    document.getElementById('assign_task_name_display').value = taskName;

    const dropdown = document.getElementById('lead_category_dropdown');
    const dropdownContainer = document.getElementById('lead_category_dropdown_container');
    dropdown.innerHTML = '<option selected disabled>Select Category</option>';
    dropdownContainer.classList.add('d-none');

    if (taskName.toLowerCase() === 'lead collection') {
      dropdownContainer.classList.remove('d-none');
      fetch(`/get-lead-categories-for-tl-task/${assignId}/`)
        .then(res => res.json())
        .then(data => {
          console.log('[DEBUG] Lead Categories Fetched:', data);
          data.categories.forEach(cat => {
            const opt = document.createElement('option');
            opt.value = cat.id;
            opt.textContent = cat.name;
            dropdown.appendChild(opt);
          });
        });
    }

const execDropdown = document.getElementById('exec_dropdown');
execDropdown.innerHTML = '<option selected disabled>Select Employee</option>';

fetch(`/get-employees-for-tl/${tlId}/`)
  .then(res => res.json())
  .then(data => {
    console.log('[DEBUG] Executives Fetched:', data);
    if (!data.length) {
      const opt = document.createElement('option');
      opt.disabled = true;
      opt.textContent = 'No employees linked.';
      execDropdown.appendChild(opt);
      return;
    }
    data.forEach(emp => {
      const opt = document.createElement('option');
      opt.value = emp.id;
      opt.textContent = emp.name;
      execDropdown.appendChild(opt);
    });
  });

// fetch description and file
fetch(`/get-full-workassign/${assignId}/`)
  .then(res => res.json())
  .then(data => {
    console.log('[DEBUG] WorkAssign Details:', data);
    document.querySelector('textarea[name="description"]').value = data.description || '';
    const fileBtn = document.getElementById('download_file_btn');
    const fileWrapper = document.getElementById('work_file_download_link');
    if (data.file_url) {
      fileBtn.href = data.file_url;
      fileWrapper.style.display = 'block';
    } else {
      fileWrapper.style.display = 'none';
    }
  });


    new bootstrap.Modal(document.getElementById('assignExecModal')).show();
  });
});

// === Clear assign form ===
document.getElementById('clearAssignExecBtn').addEventListener('click', () => {
  const form = document.getElementById('assignExecForm');
  const taskName = document.getElementById('assign_task_name_display').value;
  form.reset();
  document.getElementById('assign_task_name_display').value = taskName;
  document.getElementById('lead_category_dropdown_container').classList.add('d-none');
  console.log('[DEBUG] Form cleared');
});

// === Submit assign form ===
document.getElementById('assignExecForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);

  // For debugging: log all form values
  console.log('[DEBUG] Form Submission');
  for (let [key, value] of formData.entries()) {
    console.log(`${key}:`, value);
  }

  fetch('/assign-to-executives/', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      console.log('[DEBUG] Server Response:', data);
      if (data.success) {
        window.location.reload();
      } else {
        alert(data.message);
      }
    })
    .catch(err => {
      console.error('[ERROR] Submission Failed:', err);
      alert('An error occurred. Please try again.');
    });
});


  // === Search Filter ===
  const searchInput = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearch");
  const rows = document.querySelectorAll("#targetTable tbody tr");

  function filterRows() {
    const searchTerm = searchInput.value.toLowerCase();
    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(searchTerm) ? "" : "none";
    });
  }

  searchInput.addEventListener("keyup", filterRows);
  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    filterRows();
  });
});
