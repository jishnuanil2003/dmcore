let allLeads = leadData;
let filteredLeads = [...allLeads];
let dataTable = null;

$(document).ready(function () {
  renderTable(filteredLeads);
  bindEvents();
  $('#categoryFilter').prop('disabled', true);

});

function renderTable(data) {
  const table = $('#leadsTable');
  const tbody = $('#tableBody');

  if ($.fn.DataTable.isDataTable(table)) {
    table.DataTable().destroy();
    tbody.empty();
  }

  if (!data.length) {
    tbody.html(`<tr><td colspan="7" class="text-center text-white">No leads found</td></tr>`);
    $('#entryInfo').text(`Showing 0 of ${allLeads.length} entries`);
    
    return;
  }

  let rowsHTML = '';
  data.forEach((lead, index) => {
    const id = lead.id ?? '-';
    const transferDate = lead.transfer_date || '-';
    const addedDate = lead.added_date || '-';
    const name = lead.name || '-';
    const email = lead.email || '-';
    const contact = lead.contact || '-';
    const finalResponse = lead.final_response || 'Not Allocated';

    rowsHTML += `
      <tr>
        <td>${index + 1}</td>
        <td><button class="btn btn-outline-info btn-sm trackBtn" data-id="${id}">Track</button></td>
        <td>${transferDate} <br><small>Collected on: ${addedDate}</small></td>
        <td>${name}</td>
        <td>${email}</td>
        <td>${contact}</td>
        <td>${finalResponse}</td>
      </tr>
    `;
  });

  tbody.html(rowsHTML);
  $('#entryInfo').text(`Showing ${data.length} of ${allLeads.length} entries`);

  try {
    dataTable = table.DataTable({
      paging: true,
      searching: false,
      ordering: true,
      lengthChange: false,
      order: [],
      pageLength: parseInt($('#showDropdown').val()),
      columnDefs: [{ orderable: false, targets: [1] }]
    });
  } catch (e) {
    
  }

  $('.trackBtn').click(function () {
    const leadId = $(this).data('id');
    openLeadDetails(leadId);
  });
}

function bindEvents() {
  $('#searchInput').on('keyup', applyFilters);
  $('#clearSearch').click(() => {
    $('#searchInput').val('');
    applyFilters();
  });

  $('select, input[type=date]').on('change', applyFilters);

  $('#showDropdown').on('change', () => {
    dataTable.page.len($('#showDropdown').val()).draw();
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

  $('#clearFilter').click(() => {
    location.reload();
  });
}

function applyFilters() {
  const status = $('#statusFilter').val();
  const followup1 = $('#followupStatusFilter').val();
  const followup2 = $('#followupStatusFilter2').val();
  const followup3 = $('#followupStatusFilter3').val();
  const client = $('#clientFilter').val();
  const category = $('#categoryFilter').val();
  const executive = $('#executiveFilter').val();
  const from = $('#startDateFilter').val();
  const to = $('#endDateFilter').val();
  const telecaller = $('#telecallerFilter').val();
  const assignFrom = $('#assignFromDate').val();
  const assignTo = $('#assignToDate').val();
  const search = $('#searchInput').val().toLowerCase();

  // GLOBAL STATUS GROUPING
  const groupedByStatus = {};

  allLeads.forEach(lead => {

      let status = lead.final_response || 'No Updation';

   
      if (status === 'No Data Availale') {
          status = 'No Updation';
      }

      if (status === 'Waste Lead') {
          status = 'Marked as Waste';
      }

      if (!groupedByStatus[status]) {
          groupedByStatus[status] = [];
      }

      groupedByStatus[status].push(lead.id);

  });

  filteredLeads = allLeads.filter(lead => {

      if (status && lead.lead_status !== status)
          return false;




      // COMBINED FOLLOWUP FILTER IDS
      let allowedIds = [];

      // FOLLOWUP STATUS 1
      if (followup1) {

          const ids = groupedByStatus[followup1] || [];

          if (ids.length > 0) {
              allowedIds.push(ids[0]); // FIRST
          }
      }


      // FOLLOWUP STATUS 2
      if (followup2) {

          const ids = groupedByStatus[followup2] || [];

          const middleIds = ids.slice(1, -1);

          allowedIds.push(...middleIds);
      }


      // FOLLOWUP STATUS 3
      if (followup3) {

          const ids = groupedByStatus[followup3] || [];

          if (ids.length > 0) {

              const lastId = ids[ids.length - 1];

              allowedIds.push(lastId); // LAST
          }
      }


      // REMOVE DUPLICATES
      allowedIds = [...new Set(allowedIds)];


      // APPLY COMBINED FILTER
      if (
          (followup1 || followup2 || followup3) &&
          !allowedIds.includes(lead.id)
      ) {
          return false;
      }

      if (client && lead.client_name !== client)
          return false;

      if (category && lead.category_name !== category)
          return false;

      if (executive && lead.collected_by !== executive)
          return false;

      if (telecaller && lead.telecaller !== telecaller)
          return false;

      if (from && lead.added_date < from)
          return false;

      if (to && lead.added_date > to)
          return false;

      if (
          assignFrom &&
          (!lead.assign_date || lead.assign_date < assignFrom)
      ) {
          return false;
      }

      if (
          assignTo &&
          (!lead.assign_date || lead.assign_date > assignTo)
      ) {
          return false;
      }

      if (
          search &&
          !(
              lead.name.toLowerCase().includes(search) ||
              lead.email.toLowerCase().includes(search) ||
              lead.contact.toLowerCase().includes(search)
          )
      ) {
          return false;
      }

      return true;
  });

  renderTable(filteredLeads);
  
}

function openLeadDetails(leadId) {
  fetch(`/lead_data_collection_hr/${leadId}/`)
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        
        document.getElementById("leadName").textContent = data.lead.name || "-";
        document.getElementById("leadEmail").textContent = data.lead.email || "-";
        document.getElementById("leadPhone").textContent = data.lead.contact || "-";
        document.getElementById("leadAddedDate").textContent = data.lead.added_date || "-";

        document.getElementById("clientName").textContent = data.client.name || "-";
        document.getElementById("clientBusiness").textContent = data.client.business || "-";
        document.getElementById("clientCategory").textContent = data.category || "-";

        document.getElementById("collectedByName").textContent = data.collected_by.name || "-";
        document.getElementById("collectedCategory").textContent = data.category || "-";

        
        fetch(`/get-followup-data/${leadId}/`)
          .then(res => res.json())
          .then(extra => {
            if (extra.success) {
              
              document.getElementById("followupDetailsContent").innerHTML = extra.details.length
                ? extra.details.map(d => `
                    <div class="mb-2">
                      <p><strong>Date:</strong> ${d.date}</p>
                      <p><strong>Response:</strong> ${d.response}</p>
                      <p><strong>Next Follow Up:</strong> ${d.next}</p>
                      <p><strong>Status:</strong> ${d.status}</p>
                      <hr>
                    </div>`).join("")
                : "<p>No follow-up details available.</p>";

              document.getElementById("followupHistoryContent").innerHTML = extra.history.length
                ? extra.history.map(h => `
                    <div class="mb-2">
                      <p><strong>Date:</strong> ${h.date}</p>
                      <p><strong>Allocated to:</strong> ${h.telecaller}</p>
                      <p><strong>Note:</strong> ${h.note}</p>
                      <p><strong>Status:</strong> ${h.status}</p>
                      <hr>
                    </div>`).join("")
                : "<p>No follow-up history available.</p>";
              
              document.getElementById("recordingsContent").innerHTML = extra.recordings.length
                ? extra.recordings.map(r => `
                    <div class="mb-3">
                      <p><strong>Date:</strong> ${r.date}</p>
                      <audio controls src="${r.url}" class="w-100"></audio>
                    </div>`).join("")
                : "<p>No recordings found.</p>";
            }
          });
        
        const offcanvas = new bootstrap.Offcanvas(document.getElementById('leadDetailsCanvas'));
        offcanvas.show();
      }
    })
    .catch(err => {
      
      alert("Something went wrong. Please try again.");
    });
}

  $('#downloadExcelBtn').click(() => {
    const rows = $('#leadsTable tbody tr:visible');
    const data = [["#", "Transfer Date", "Lead Name", "Email", "Phone", "Final Response"]];

    rows.each(function () {
      const cells = $(this).find('td');
      if (cells.length >= 7) {
        data.push([
          cells.eq(0).text().trim(),                   
          cells.eq(2).text().trim(),                   
          cells.eq(3).text().trim(),                   
          cells.eq(4).text().trim(),                   
          cells.eq(5).text().trim(),                   
          cells.eq(6).text().trim()                    
        ]);
      }
    });

    const ws = XLSX.utils.aoa_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Leads");

    const today = new Date().toISOString().split("T")[0];
    XLSX.writeFile(wb, `Leads_${today}.xlsx`);
  });
