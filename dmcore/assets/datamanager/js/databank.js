document.addEventListener('DOMContentLoaded', function () {
  const body = document.getElementById('leadsTableBody');
  const loading = document.getElementById('leadsLoading');
  const empty = document.getElementById('noDataMessage');
  const message = document.getElementById('leadMessage');
  const pageSize = document.getElementById('rowCount');
  const searchInput = document.getElementById('searchInput');
  let currentPage = 1;
  let pageCount = 1;
  let searchTimer;

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, function (character) {
      return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[character];
    });
  }

  function showMessage(text, type) {
    message.className = 'alert alert-' + type;
    message.textContent = text;
  }

  function paramsForRequest() {
    const params = new URLSearchParams({ page: currentPage, page_size: pageSize.value || '25' });
    const filters = {
      client: document.getElementById('clientSelect').value,
      category: document.getElementById('categorySelect').value,
      hr: document.getElementById('hrFilter').value,
      date_from: document.getElementById('startDate').value,
      date_to: document.getElementById('endDate').value,
      status: document.getElementById('statusSelect').value,
      search: searchInput.value.trim()
    };
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    return params;
  }

  function renderLeads(leads) {
    body.innerHTML = leads.map(function (lead) {
      const details = (lead.details || []).map(function (detail) {
        return '<div><strong>' + escapeHtml(detail.field_name) + ':</strong> ' + escapeHtml(detail.field_data) + '</div>';
      }).join('') || '<span class="text-white-50">-</span>';
      const channel = lead.send_channel === 'sms' ? 'SMS' : 'Email';
      const sendLabel = 'Send by ' + channel;
      const action = lead.is_confused
        ? (lead.interview_email_sent
          ? '<button class="btn btn-success btn-sm" type="button" disabled>Sent</button>'
          : '<button class="btn btn-outline-info btn-sm send-interview" type="button" data-channel="' + escapeHtml(channel) + '" data-lead-id="' + escapeHtml(lead.id) + '">' + sendLabel + '</button>')
        : '';
      const displayStatus = lead.is_confused ? 'Confused' : lead.status;
      return '<tr>' +
        '<td>' + escapeHtml(lead.name) + '</td>' +
        '<td>' + escapeHtml(lead.email) + '</td>' +
        '<td>' + escapeHtml(lead.contact) + '</td>' +
        '<td>' + escapeHtml(lead.source) + '</td>' +
        '<td>' + escapeHtml(lead.category_name) + '</td>' +
        '<td>' + escapeHtml(lead.executive_name) + '</td>' +
        '<td>' + escapeHtml(lead.added_date) + '</td>' +
        '<td>' + escapeHtml(displayStatus) + '</td>' +
        '<td>' + details + '</td>' +
        '<td>' + action + '</td>' +
      '</tr>';
    }).join('');
  }

  async function loadLeads() {
    loading.classList.remove('d-none');
    empty.classList.add('d-none');
    message.classList.add('d-none');
    try {
      const response = await fetch('/api/leads/?' + paramsForRequest().toString(), {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Unable to load leads.');
      renderLeads(data.results || []);
      document.getElementById('leadCount').textContent = data.count;
      currentPage = data.page;
      pageCount = data.num_pages;
      document.getElementById('pageSummary').textContent = pageCount ? 'Page ' + currentPage + ' of ' + pageCount : '';
      const first = data.count ? ((currentPage - 1) * data.page_size) + 1 : 0;
      const last = Math.min(currentPage * data.page_size, data.count);
      document.getElementById('paginationSummary').textContent = data.count ? 'Showing ' + first + '–' + last + ' of ' + data.count : '';
      document.getElementById('previousPage').disabled = currentPage <= 1;
      document.getElementById('nextPage').disabled = currentPage >= pageCount;
      empty.classList.toggle('d-none', (data.results || []).length !== 0);
    } catch (error) {
      body.innerHTML = '';
      document.getElementById('leadCount').textContent = '0';
      showMessage(error.message || 'Unable to load leads.', 'danger');
    } finally {
      loading.classList.add('d-none');
    }
  }

  ['clientSelect', 'categorySelect', 'hrFilter', 'startDate', 'endDate', 'statusSelect'].forEach(function (id) {
    document.getElementById(id).addEventListener('change', function () {
      currentPage = 1;
      loadLeads();
    });
  });
  pageSize.addEventListener('change', function () { currentPage = 1; loadLeads(); });
  searchInput.addEventListener('input', function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () { currentPage = 1; loadLeads(); }, 250);
  });
  document.getElementById('clearSearch').addEventListener('click', function () {
    searchInput.value = '';
    currentPage = 1;
    loadLeads();
  });
  document.getElementById('clearFilters').addEventListener('click', function () {
    ['clientSelect', 'categorySelect', 'hrFilter', 'statusSelect', 'startDate', 'endDate'].forEach(function (id) {
      document.getElementById(id).value = '';
    });
    currentPage = 1;
    loadLeads();
  });
  document.getElementById('previousPage').addEventListener('click', function () {
    if (currentPage > 1) { currentPage -= 1; loadLeads(); }
  });
  document.getElementById('nextPage').addEventListener('click', function () {
    if (currentPage < pageCount) { currentPage += 1; loadLeads(); }
  });

  body.addEventListener('click', async function (event) {
    const button = event.target.closest('.send-interview');
    if (!button) return;
    const leadId = button.dataset.leadId;
    const defaultLabel = button.textContent;
    button.disabled = true;
    button.textContent = 'Sending...';
    try {
      const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const response = await fetch('/api/leads/' + encodeURIComponent(leadId) + '/send-interview/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest' }
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || 'Unable to send interview invitation.');
      button.textContent = 'Sent';
      button.classList.remove('btn-outline-info');
      button.classList.add('btn-success');
      showMessage(data.message, 'success');
    } catch (error) {
      showMessage(error.message || 'Unable to send interview invitation.', 'danger');
      button.disabled = false;
      button.textContent = defaultLabel;
    }
  });

  loadLeads();
});
