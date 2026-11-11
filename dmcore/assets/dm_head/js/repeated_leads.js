let allLeads = leadData;
let filteredLeads = [...allLeads];
let dataTable = null;

$(document).ready(function () {
  renderTable(filteredLeads);
  bindEvents();
  $('#categoryFilter').prop('disabled', true);
  updateLeadCount();
});

function renderTable(data) {

    if ($.fn.DataTable.isDataTable('#repeatedTable')) {
        $('#repeatedTable').DataTable().clear().destroy();
    }

    const tbody = $('#tableBody');
    tbody.empty();

    if (!data.length) {
        tbody.append(`
            <tr>
                <td colspan="7" class="text-center text-white">
                    No leads found
                </td>
            </tr>
        `);
        return;
    }

    data.forEach((lead, index) => {
        const typeText = lead.repeated_status === 2
            ? '<span class="text-danger">Retargeted</span>'
            : 'Repeated';

        tbody.append(`
            <tr>
                <td>${index + 1}</td>
                <td><input type="checkbox" class="rowCheck" data-id="${lead.id}"></td>
                <td><button class="btn btn-outline-info btn-sm historyBtn" data-id="${lead.id}">History</button></td>
                <td>${lead.added_date || '---'}</td>
                <td>${lead.name || '---'}</td>
                <td>${lead.email || ''}<br>${lead.contact || ''}</td>
                <td>${typeText}</td>
            </tr>
        `);
    });

    dataTable = $('#repeatedTable').DataTable({
        destroy: true,
        paging: true,
        searching: false,
        ordering: true,
        lengthChange: false,
        pageLength: parseInt($('#rowLimit').val()),
        columnDefs: [
            { orderable: false, targets: [1, 2] }
        ]
    });

    bindDynamicEvents();
    updateLeadCount();
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

  $('#selectAll').on('change', function () {
    $('.rowCheck').prop('checked', this.checked);
    updateCheckedCount();
  });

  $(document).on('change', '.rowCheck', updateCheckedCount);


//?==================== excel ==========================
  $('#excelBtn').click(() => {
    const headers = ['No', 'Marked Date', 'Lead Name', 'Contact Details', 'Type'];
    const rows = [];

    $('#repeatedTable tbody tr').each(function (i, row) {
      const cells = $(row).find('td');
      if (cells.length === 7) {
        rows.push([
          cells.eq(0).text().trim(),
          cells.eq(3).text().trim(),
          cells.eq(4).text().trim(),
          cells.eq(5).text(),
          cells.eq(6).text().trim()
        ]);
      }
    });

    const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Repeated Leads");
    XLSX.writeFile(workbook, "repeated_leads.xlsx");
  });

  
//?====================== print ==========================
  $('#printBtn').click(() => {
    const printWindow = window.open('', '_blank');
    const tableHtml = $('#repeatedTable').clone();

    tableHtml.find('th:eq(1), th:eq(2), td:nth-child(2), td:nth-child(3)').remove();
    tableHtml.attr('class', 'table table-bordered');
    tableHtml.css('font-size', '12px');

    const style = `
      <style>
        body { background: white; color: black; font-family: Arial, sans-serif; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #000 !important; color: #fff !important; font-weight: bold; padding: 6px; border: 1px solid #ccc;}
        td { padding: 6px; border: 1px solid #ccc; }
      </style>
    `;

    printWindow.document.write(`
      <html>
        <head>
          <title>Repeated Leads</title>
          ${style}
        </head>
        <body>
          <h4>Repeated Leads</h4>
          ${tableHtml.prop('outerHTML')}
        </body>
      </html>
    `);
    printWindow.document.close();
    printWindow.print();
  });


//?====================== PDF ==========================
  $('#pdfBtn').click(() => {
    generateRepeatedLeadsPDF(blob => {
      const fileURL = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = fileURL;
      link.download = 'repeated_leads.pdf';
      link.click();
    });
  });



//?====================== sharebtn ==========================
  $('#shareBtn').click(() => {
    const modal = new bootstrap.Modal(document.getElementById('shareModal'));
    modal.show();
  });

//   //animation
  $('#shareViaEmail').click(() => {
    $('#emailSection').slideDown();
  });
  
  $('#shareViaWhatsApp').click(() => {
    $('#emailSection').slideUp();
  });


//?====================== whatsapp ==========================
$('#shareViaWhatsApp').click(() => {
  $('#emailSection').slideUp();

  generateRepeatedLeadsPDF(blob => {
    const fileURL = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = fileURL;
    link.download = 'repeated_leads.pdf';
    link.click();

    window.open("https://wa.me/?text=Please find the repeated leads list below.", '_blank');
  });
});


//?====================== email ==========================
$('#sendEmail').click(() => {
  const emails = $('#emailInput').val().trim();
  const message = $('#emailMessage').val().trim();
  if (!emails) return alert("Please enter at least one recipient email.");

  generateRepeatedLeadsPDF(blob => {
    const formData = new FormData();
    formData.append('pdf', blob, 'repeated_leads.pdf');
    formData.append('emails', emails);
    formData.append('message', message);

    $.ajax({
      url: '/send_lead_pdf_mail/',
      method: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: { 'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val() },
      success: () => {
        resetShareModal();
        const modal = bootstrap.Modal.getInstance(document.getElementById('shareModal'));
        modal.hide();
        showToast("Email sent successfully.", "success");
      },
      error: () => {
        showToast("Failed to sent the mail.", "danger");
      }
    });
  });
});


//?====================== delete ==========================
$('#deleteBtn').off('click').on('click', () => {
  const selectedIds = $('.rowCheck:checked').map(function () {
    return $(this).data('id');
  }).get();

  if (!selectedIds.length) {
    showToast("No leads selected for deletion.", "warning");
    return;
  }

  if (!confirm("Are you sure you want to delete the selected leads?")) return;

  fetch('/delete_repeated_leads/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
    },
    body: JSON.stringify({ ids: selectedIds })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        allLeads = allLeads.filter(lead => !selectedIds.includes(lead.id));
        filteredLeads = filteredLeads.filter(lead => !selectedIds.includes(lead.id));
        renderTable(filteredLeads);
        $('#selectAll').prop('checked', false);
        updateCheckedCount();

        showToast("Selected leads deleted successfully.", "success");
        setTimeout(() => location.reload(), 1500);
      } else {
        showToast("Deletion failed: " + (data.message || "Unknown error."), "danger");
      }
    })
    .catch(err => {
      
      showToast("Server error during deletion.", "danger");
    });
});
}

function applyFilters() {
  const client = $('#clientFilter').val();
  const category = $('#categoryFilter').val();
  const executive = $('#executiveFilter').val();
  const from = $('#startDateFilter').val();
  const to = $('#endDateFilter').val();
  const telecaller = $('#telecallerFilter').val();
  const assignFrom = $('#assignFromDate').val();
  const assignTo = $('#assignToDate').val();
  const search = $('#searchInput').val().toLowerCase();

  filteredLeads = allLeads.filter(lead => {
    if (client && lead.client_name !== client) return false;
    if (category && lead.category_name !== category) return false;
    if (executive && lead.collected_by !== executive) return false;
    if (telecaller && lead.telecaller !== telecaller) return false;
    if (from && lead.added_date < from) return false;
    if (to && lead.added_date > to) return false;
    if (assignFrom && (!lead.assign_date || lead.assign_date < assignFrom)) return false;
    if (assignTo && (!lead.assign_date || lead.assign_date > assignTo)) return false;
    if (search && !(
      lead.name.toLowerCase().includes(search) ||
      lead.email.toLowerCase().includes(search) ||
      lead.contact.toLowerCase().includes(search)
    )) return false;
    return true;
  });

  renderTable(filteredLeads);
}

function updateCheckedCount() {
  const count = $('.rowCheck:checked').length;
  $('#checkedCount').text(count);
}

function updateLeadCount() {
  $('#leadCount').text(filteredLeads.length);
}

function bindDynamicEvents() {
  $('.historyBtn').click(function () {
    const id = $(this).data('id');
    fetch(`/leads-tracker/fetch/${id}/`)
      .then(res => res.json())
      .then(data => {
        if (!data.success) return;

        $('#leadName').text(data.lead.name);
        $('#leadEmail').text(data.lead.email);
        $('#leadPhone').text(data.lead.contact);
        $('#leadAddedDate').text(data.lead.added_date);
        $('#clientName').text(data.client.name);
        $('#clientBusiness').text(data.client.business);
        $('#clientCategory').text(data.client.category);
        $('#collectedByName').text(data.lead.collected_by);
        $('#collectedCategory').text(data.client.category);

        const details = Object.entries(data.details).map(([k, v]) =>
          `<p class="mb-1"><strong>${k}</strong>: ${v}</p>`).join('');
        $('#followupDetailsContent').html(details || '---');

        const history = data.history.length
          ? data.history.map(h => `
              <div class="card bg-secondary text-white mb-2">
                <div class="card-body p-2">
                  <p class="mb-1"><strong>Response:</strong> ${h.response}</p>
                  <p class="mb-1"><strong>Reason:</strong> ${h.reason}</p>
                  <p class="mb-0"><strong>Date:</strong> ${h.date}</p>
                </div>
              </div>`).join('')
          : '<p class="text-white">No History Available</p>';

        $('#followupHistoryContent').html(history);

        const canvas = new bootstrap.Offcanvas('#leadDetailsCanvas');
        canvas.show();
      })
      .catch(() => {
        $('#followupDetailsContent').html('---');
        $('#followupHistoryContent').html('---');
        
      });
  });
}

////  generate pdf for email and whatsapp

function generateRepeatedLeadsPDF(callback) {
  const table = $('#repeatedTable').clone();
  table.find('th:eq(1), th:eq(2), td:nth-child(2), td:nth-child(3)').remove();
  table.removeClass().addClass('table').css({ fontSize: '10px', borderCollapse: 'collapse' });

  table.find('th').css({ backgroundColor: '#000', color: '#fff', border: '1px solid #000', padding: '6px' });
  table.find('td').css({ border: '1px solid #000', padding: '6px' });

  const wrapper = document.createElement("div");
  const header = document.createElement("h4");
  header.innerText = "Repeated Leads";
  header.style.marginBottom = "15px";
  wrapper.appendChild(header);
  wrapper.appendChild(table[0]);

  html2pdf().from(wrapper).set({
    margin: [0.5, 0.5],
    html2canvas: { scale: 2 },
    jsPDF: { orientation: 'portrait', unit: 'in', format: 'a4' }
  }).outputPdf('blob').then(callback);
}

function resetShareModal() {
  $('#emailInput').val('');
  $('#emailMessage').val('');
  $('#emailSection').hide();
}

function showToast(message, type = 'success') {
  const toastEl = $('#repeatedToast');
  const toastBody = $('#toastMessage');

  toastEl.removeClass().addClass(`toast text-white border-0 bg-${type}`);
  toastBody.html(message);

  const toast = new bootstrap.Toast(document.getElementById('repeatedToast'));
  toast.show();
}
