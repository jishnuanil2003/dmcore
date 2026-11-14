let allLeads = [...window.allLeads];
let filteredLeads = [...allLeads];
let dataTable = null;

$(document).ready(() => {
  renderTable(filteredLeads);
  bindEvents();
  $('#categoryFilter').prop('disabled', true);
});

function renderTable(data) {
  const table = $('#leadReportsTable');
  const tbody = $('#tableBody');

  if ($.fn.DataTable.isDataTable(table)) {
    table.DataTable().destroy();
    table.find('tbody').off();
  }

  tbody.empty();

  if (!data.length) {
    tbody.append(`<tr><td colspan="6" class="text-center text-white">No leads found</td></tr>`);
  } else {
    data.forEach((lead, index) => {
      const statusInfo = computeStatus(lead);

      tbody.append(`
        <tr>
          <td>${index + 1}</td>
          <td>${lead.added_date || '-'}</td>
          <td>${lead.name || '-'}</td>
          <td>${lead.email || ''}</td>
          <td>${lead.contact || ''}</td>
          <td class="${statusInfo.class}">${statusInfo.label}</td>
        </tr>
      `);
    });

    dataTable = table.DataTable({
      paging: true,
      searching: false,
      ordering: true,
      lengthChange: false,
      order: [],
      pageLength: parseInt($('#rowLimit').val()),
      columnDefs: [{ orderable: false, targets: [] }]
    });
  }
}


function computeStatus(lead) {
  if (lead.waste_data === 1) return { label: "Waste", class: "text-danger" };
  if (lead.incomplete_status === 1) return { label: "Incomplete", class: "text-warning" };
  if (lead.repeated_status === 1) return { label: "Repeated", class: "text-warning" };
  if (lead.status === 1 && lead.transfer_status === 1) return { label: "Transferred", class: "text-info" };
  if (lead.status === 1) return { label: "Verified", class: "text-success" };
  return { label: "Unverified", class: "text-secondary" };
}

function bindEvents() {
  $('#searchInput').on('keyup', applyFilters);
  $('#clearSearch').click(() => { $('#searchInput').val(''); applyFilters(); });

  $('select, input[type=date]').on('change', applyFilters);

  $('#rowLimit').on('change', () => {
    dataTable.page.len($('#rowLimit').val()).draw();
  });

  $('#clientFilter').on('change', function () {
    const selectedClient = $(this).val();
    const $cat = $('#categoryFilter');

    $cat.prop('disabled', !selectedClient).val('');
    $cat.find('option').each(function () {
      const match = $(this).data('client') == selectedClient;
      $(this).toggle(match || !$(this).data('client'));
    });
  });

  $('#clearFilter').click(() => location.reload());
}

function applyFilters() {
  const client = $('#clientFilter').val();
  const category = $('#categoryFilter').val();
  const executive = $('#executiveFilter').val();
  const from = $('#startDateFilter').val();
  const to = $('#endDateFilter').val();
  const status = $('#statusFilter').val();
  const source = $('#sourceFilter').val();
  const search = $('#searchInput').val().toLowerCase();

  filteredLeads = allLeads.filter(lead => {
    const computed = computeStatus(lead);

    if (client && lead.client_name !== client) return false;
    if (category && lead.category_name !== category) return false;
    if (executive && lead.collected_by !== executive) return false;
    if (from && lead.added_date < from) return false;
    if (to && lead.added_date > to) return false;
    if (source && lead.source !== source) return false;
    if (status && computed.label.toLowerCase() !== status.toLowerCase()) return false;

    if (search && !(
      lead.name?.toLowerCase().includes(search) ||
      lead.email?.toLowerCase().includes(search) ||
      lead.contact?.toLowerCase().includes(search)
    )) return false;

    return true;
  });
  
  renderTable(filteredLeads);
}
