document.addEventListener("DOMContentLoaded", () => {
  const table = $('#followUpTable').DataTable({
    paging: true,
    ordering: true,
    lengthChange: false,
    pageLength: 25,
    searching: false
  });

    [
    'hrFilter',
    'startDate',
    'endDate',
    'statusFilter',
    'followupStatusFilter',
    'followupStatusFilter2',
    'followupStatusFilter3'
  ].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('change', applyFilters);
  });

  function applyFilters() {

      const hr = document.getElementById('hrFilter')?.value;
      const status = document.getElementById('statusFilter')?.value?.toLowerCase();

      const start = document.getElementById('startDate')?.value;
      const end = document.getElementById('endDate')?.value;

      const follow1 = document.getElementById('followupStatusFilter')?.value?.toLowerCase();
      const follow2 = document.getElementById('followupStatusFilter2')?.value?.toLowerCase();
      const follow3 = document.getElementById('followupStatusFilter3')?.value?.toLowerCase();

      // GLOBAL FOLLOWUP GROUPING
      const groupedByStatus = {};

      $('#followUpTable tbody tr').each(function () {

          const row = $(this);

          const status =
              row.data('followup')?.toString().toLowerCase();

          if (!status)
              return;

          if (!groupedByStatus[status]) {
              groupedByStatus[status] = [];
          }

          groupedByStatus[status].push(row);

      });
      $('#followUpTable tbody tr').each(function () {

          const row = $(this);

          const rowHr = row.data('hr')?.toString();
          const rowStatus = row.data('status')?.toString();
          const rowDate = row.data('added')?.toString();

          const rowFollowup = row.data('followup')?.toString().toLowerCase();

       

          let visible = true;

          // HR Filter
          if (hr && rowHr !== hr) {
              visible = false;
          }

          // Lead Status
          if (visible && status && rowStatus !== status) {
              visible = false;
          }

          // Date Filter
          if (visible && start && (!rowDate || rowDate < start)) {
              visible = false;
          }

          if (visible && end && (!rowDate || rowDate > end)) {
              visible = false;
          }

          // COMBINED FOLLOWUP FILTER IDS
          let allowedRows = [];


          // FOLLOWUP STATUS 1
          if (follow1) {

              const rows =
                  groupedByStatus[follow1] || [];

              if (rows.length > 0) {
                  allowedRows.push(rows[0]);
              }
          }


          // FOLLOWUP STATUS 2
          if (follow2) {

              const rows =
                  groupedByStatus[follow2] || [];

              const middleRows =
                  rows.slice(1, -1);

              allowedRows.push(...middleRows);
          }


          // FOLLOWUP STATUS 3
          if (follow3) {

              const rows =
                  groupedByStatus[follow3] || [];

              if (rows.length > 0) {

                  const lastRow =
                      rows[rows.length - 1];

                  allowedRows.push(lastRow);
              }
          }


          // REMOVE DUPLICATES
          allowedRows = [...new Set(allowedRows)];


          // APPLY FILTER
          if (
              visible &&
              (follow1 || follow2 || follow3)
          ) {

              const exists =
                  allowedRows.some(r => r[0] === row[0]);

              if (!exists) {
                  visible = false;
              }
          }

          row.toggle(visible);
      });

      toggleNoData();
  }

  function toggleNoData() {
    const visibleRows = $('#followUpTable tbody tr:visible').length;
    const msgEl = document.getElementById('noDataMessage');

    if (visibleRows === 0) {
      if (!msgEl) {
        const msg = document.createElement('div');
        msg.className = 'text-white text-center mt-3';
        msg.id = 'noDataMessage';
        msg.innerHTML = '<h5>No data found for the selected filters.</h5>';
        document.getElementById('followUpTable').parentElement.appendChild(msg);
      } else {
        msgEl.style.display = 'block';
      }
    } else {
      if (msgEl) msgEl.style.display = 'none';
    }
  }

  document.getElementById('clearFilters')?.addEventListener('click', () => {
    [
  'hrFilter',
  'statusFilter',
  'startDate',
  'endDate',
  'followupStatusFilter',
  'followupStatusFilter2',
  'followupStatusFilter3'
].forEach(id => {
      const el = document.getElementById(id);
      if (el?.tagName === 'SELECT') el.selectedIndex = 0;
      if (el?.tagName === 'INPUT') el.value = '';
    });
    applyFilters();
  });

  document.getElementById('rowCount')?.addEventListener('change', function () {
    table.page.len(parseInt(this.value)).draw();
  });

  document.getElementById('searchInput')?.addEventListener('keyup', function () {
    const val = this.value.toLowerCase();
    $('#followUpTable tbody tr').each(function () {
      $(this).toggle($(this).text().toLowerCase().includes(val));
    });
  });

  document.getElementById('clearSearch')?.addEventListener('click', () => {
    document.getElementById('searchInput').value = '';
    document.getElementById('searchInput').dispatchEvent(new Event('keyup'));
  });

  document.getElementById('selectAll')?.addEventListener('change', function () {
    const checked = this.checked;
    document.querySelectorAll('.rowCheckbox').forEach(cb => cb.checked = checked);
  });

  document.getElementById('bulkDeleteBtn')?.addEventListener('click', () => {
    const selected = Array.from(document.querySelectorAll('.rowCheckbox:checked')).map(cb => cb.value);
    if (!selected.length) return alert("Select at least one entry.");
    if (!confirm("Are you sure to de-allocate selected leads?")) return;

    fetch('/deallocate-followups/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ lead_ids: selected })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) window.location.reload();
      else alert("Failed to deallocate");
    });
  });


  const toastEl = document.getElementById('followUpToast');
  const toastMsg = document.getElementById('followUpToastMessage');
  const toast = new bootstrap.Toast(toastEl);


  const followUpModal = new bootstrap.Modal(document.getElementById('followUpStatusModal'));


  document.getElementById('addFollowStatusBtn')?.addEventListener('click', () => {
    fetch('/get-followup-statuses/')
      .then(res => res.json())
      .then(data => {
        const list = document.getElementById('existingStatusList');
        list.innerHTML = '';
        data.forEach(item => {
          const li = document.createElement('li');
          li.className = 'list-group-item d-flex justify-content-between bg-dark text-white';
          li.innerHTML = `
            <span>${item.status_name}</span>
            <button class="btn btn-sm btn-danger" onclick="deleteFollowStatus(${item.id})">&times;</button>
          `;
          list.appendChild(li);
        });

        followUpModal.show();
      });
  });


  document.getElementById('saveNewStatus')?.addEventListener('click', () => {
    const input = document.getElementById('newStatusInput');
    const value = input.value.trim();
    if (!value) return;

    const existingStatuses = Array.from(document.querySelectorAll('#existingStatusList li span'))
      .map(span => span.textContent.toLowerCase());

    if (existingStatuses.includes(value.toLowerCase())) {
      toastMsg.textContent = 'Status already exists.';
      toastEl.classList.replace('text-bg-success', 'text-bg-danger');
      toast.show();
      return;
    }

    fetch('/add-followup-status/', {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: value })
    }).then(() => {
      input.value = '';
      followUpModal.hide();
      toastMsg.textContent = 'Status added successfully!';
      toastEl.classList.replace('text-bg-danger', 'text-bg-success');
      toast.show();
    });
  });
});

function deleteFollowStatus(id) {
  fetch(`/delete-followup-status/${id}/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': getCookie('csrftoken') }
  }).then(() => document.getElementById('addFollowStatusBtn').click());
}

function getCookie(name) {
  let cookie = document.cookie.split(';').find(c => c.trim().startsWith(name + '='));
  return cookie ? decodeURIComponent(cookie.split('=')[1]) : null;
}
