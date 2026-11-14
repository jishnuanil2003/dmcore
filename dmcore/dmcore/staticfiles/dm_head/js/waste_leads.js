let allLeads = [...window.allLeads];
let filteredLeads = [...allLeads];
let dataTable = null;

$(document).ready(function () {

  renderTable(filteredLeads);
  bindEvents();

  $('#categoryFilter').prop('disabled', true);
});

function renderTable(data) {
  const tbody = $('#wasteLeadTableBody');
  tbody.empty();

  if (!data.length) {
    tbody.append(`<tr><td colspan="7" class="text-center text-white">No leads found</td></tr>`);
    return;
  }

  data.forEach((lead, index) => {
    tbody.append(`
      <tr>
        <td><input type="checkbox" class="rowCheckbox"></td>
        <td>${lead.collected_by} <br> <small> ${lead.added_date} | ${lead.added_time}</small></td>
        <td>${lead.name}</td>
        <td>${lead.email}</td>
        <td>${lead.contact}</td>
        <td class="${lead.waste_status === 'Waste' ? 'text-danger' : 'text-success'}">${lead.waste_status}</td>
        <td>
          <button class="btn btn-outline-info btn-sm plusBtn" data-id="${lead.id}"><i class="fa-solid fa-plus"></i></button>
          <button class="btn btn-outline-light btn-sm fileBtn" data-id="${lead.id}"><i class="fa-solid fa-file"></i></button>
        </td>
      </tr>
    `);
  });

  if ($.fn.DataTable.isDataTable('#wasteLeadsTable')) {
    $('#wasteLeadsTable').DataTable().destroy();
  }

  dataTable = $('#wasteLeadsTable').DataTable({
    paging: true,
    searching: false,
    ordering: true,
    lengthChange: false,
    order: [],
    pageLength: parseInt($('#showDropdown').val()),
    columnDefs: [{ orderable: false, targets: [0, 6] }]
  });

  $('.plusBtn').click(function () {
    const id = $(this).data('id');
    
    openPlusDetails(id);
  });

  $('.fileBtn').click(function () {
    const id = $(this).data('id');
    
    openFileDetails(id);
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
    const rows = $('#showDropdown').val();
    
    dataTable.page.len(rows).draw();
  });

  $('#clientFilter').on('change', function () {
    const client = $(this).val();
    const $cat = $('#categoryFilter');
    
    $cat.prop('disabled', !client).val('');
    $cat.find('option').each(function () {
      const match = $(this).data('client') == client;
      $(this).toggle(match || !$(this).data('client'));
    });
  });

  $('#clearFilter').click(() => {
    
    location.reload();
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
    if (search && !(lead.name.toLowerCase().includes(search) || lead.email.toLowerCase().includes(search) || lead.contact.toLowerCase().includes(search))) return false;
    return true;
  });
  
  renderTable(filteredLeads);
}


function openPlusDetails(id) {
  const lead = allLeads.find(l => l.id === id);
  if (!lead) return;

  $('#ld_name').text(lead.name);
  $('#ld_contact').text(lead.contact);
  $('#ld_email').text(lead.email);
  $('#ld_status_block').html(`
    <span class="${lead.verified_class}">${lead.verified_status}</span>
    <span class="${lead.waste_class} ms-2">${lead.waste_status}</span>
    <span class="${lead.incomplete_class} ms-2">${lead.incomplete_status}</span>
  `);

  const details = lead.additional_fields || [];
  const moreHTML = details.length
    ? details.map(d => `<div class="mb-2 d-flex justify-content-between align-items-center">
        <span class="text-white">${d.field}</span>
        <span class="text-white">${d.value}</span>
      </div>`).join('')
    : `<div class="text-white">No additional fields available.</div>`;

  $('#ld_more').html(moreHTML);

  const canvas = new bootstrap.Offcanvas(document.getElementById('leadDetailCanvas'));
  canvas.show();
}


function openFileDetails(id) {
  const lead = allLeads.find(l => l.id === id);
  if (!lead) return;

  const content = `
    <div class="mb-3">
      <h6 class="text-primary">Lead Details</h6>
      <div><strong>Name:</strong> ${lead.name}</div>
      <div><strong>Email:</strong> ${lead.email}</div>
      <div><strong>Phone:</strong> ${lead.contact}</div>
      <div><strong>Added Date:</strong> ${lead.added_date}</div>
    </div>

    <div class="mb-3">
      <h6 class="text-info">Client Details</h6>
      <div><strong>Client:</strong> ${lead.client_name}</div>
      <div><strong>Business:</strong> -</div>
      <div><strong>Category:</strong> ${lead.category_name}</div>
    </div>

    <div class="mb-3">
      <h6 class="text-success">Collected Details</h6>
      <div><strong>Collected by:</strong> ${lead.collected_by}</div>
      <div><strong>Assign Date:</strong> ${lead.assign_date || '-'}</div>
      <div><strong>Telecaller:</strong> ${lead.telecaller || '-'}</div>
    </div>
  `;

  $('#fileLeadStaticDetails').html(content);

if (lead.followup_details && lead.followup_details.date) {
  $('#fileFollowupDetailsBody').html(`
    <div><strong>Date:</strong> ${lead.followup_details.date}</div>
    <div><strong>Response:</strong> ${lead.followup_details.response}</div>
    <div><strong>Next Follow Up:</strong> ${lead.followup_details.next_date}</div>
    <div><strong>Status:</strong> ${lead.followup_details.status}</div>
  `);
} else {
  $('#fileFollowupDetailsBody').html(`No follow-up details available.`);
}

if (lead.followup_history && lead.followup_history.length > 0) {
  $('#fileFollowupHistoryBody').html(
    lead.followup_history.map(h => `
      <div class="mb-3">
        <div><strong>Date:</strong> ${h.date}</div>
        <div><strong>Allocated to:</strong> ${h.telecaller}</div>
        <div><strong>Note:</strong> ${h.note}</div>
        <div><strong>Status:</strong> ${h.status}</div>
        <hr>
      </div>
    `).join('')
  );
} else {
  $('#fileFollowupHistoryBody').html(`No follow-up history available.`);
}

  const canvas = new bootstrap.Offcanvas(document.getElementById('fileDetailCanvas'));
  canvas.show();
}



//?========= excel ===========

document.getElementById("downloadExcel").addEventListener("click", () => {
  const table = document.querySelector("#wasteLeadsTable");
  if (!table) return;

  const data = [];
  const headers = [];
  const visibleRows = table.querySelectorAll("tbody tr");

  if (!visibleRows.length || visibleRows[0].innerText.includes("No leads found")) {
    alert("No data available to export.");
    return;
  }

  table.querySelectorAll("thead th").forEach((th, index) => {
    if (index !== 0 && index !== 6) headers.push(th.textContent.trim());
  });
  data.push(headers);

  visibleRows.forEach(row => {
    if (row.style.display === "none") return;

    const cells = Array.from(row.querySelectorAll("td"));
    if (cells.length < 7) return;

    data.push([
      cells[1].innerText.replace(/\n/g, ' | '),
      cells[2].innerText.trim(),
      cells[3].innerText.trim(),
      cells[4].innerText.trim(),
      cells[5].innerText.trim()
    ]);
  });

  const worksheet = XLSX.utils.aoa_to_sheet(data);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Waste Leads");

  XLSX.writeFile(workbook, "waste_leads.xlsx");
});


//?=========== pdf table ===================
document.getElementById("downloadPdf").addEventListener("click", () => {
  const dataTable = $('#wasteLeadsTable').DataTable();

  const headerTitles = dataTable.columns().header().to$().map(function () {
    return $(this).text().trim();
  }).get().slice(1, -1);

  const visibleRows = dataTable.rows({ search: 'applied', page: 'current' }).nodes();

  const table = document.createElement("table");
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";
  table.style.fontSize = "10px";

  const thead = document.createElement("thead");
  const trHead = document.createElement("tr");
  headerTitles.forEach(text => {
    const th = document.createElement("th");
    th.textContent = text;
    th.style.backgroundColor = "#000000";
    th.style.color = "#ffffff";
    th.style.padding = "6px";
    th.style.border = "1px solid #000";
    th.style.textAlign = "left";
    trHead.appendChild(th);
  });
  thead.appendChild(trHead);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  Array.from(visibleRows).forEach(row => {
    const tds = row.querySelectorAll("td");
    const tr = document.createElement("tr");

    for (let i = 1; i < tds.length - 1; i++) {
      const td = document.createElement("td");
      td.innerHTML = tds[i].innerHTML.trim();
      td.style.border = "1px solid #000";
      td.style.padding = "5px";
      td.style.color = "#000";
      td.style.backgroundColor = "#ffffff";
      td.style.textAlign = "left";
      tr.appendChild(td);
    }

    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  const now = new Date();
  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <div style="display: flex; justify-content: space-between; font-size: 10px; margin-bottom: 5px;">
      <span>${now.toLocaleDateString("en-GB")}, ${now.toLocaleTimeString("en-GB", { hour: '2-digit', minute: '2-digit' })}</span>
      <span>Waste Leads</span>
    </div>
    <h3 style="margin-bottom: 12px;">Waste Leads</h3>
  `;
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    filename: `Waste_Leads_${now.toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).save();
});


//? ================ Print offcanvas ===================== 
document.getElementById("filePrintBtn").addEventListener("click", () => {
  const canvas = document.getElementById("fileDetailCanvas");
  const followupDetails = document.getElementById("fileFollowupDetails");
  const followupHistory = document.getElementById("fileFollowupHistory");

  followupDetails.classList.add("show");
  followupHistory.classList.add("show");

  const printBtn = document.getElementById("filePrintBtn");
  const pdfBtn = document.getElementById("filePdfBtn");
  printBtn.style.display = "none";
  pdfBtn.style.display = "none";

  const originalBody = document.body.innerHTML;

  const printable = `
    <html>
    <head>
      <title>Lead Details</title>
      <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h5, h6 { margin-bottom: 10px; }
        .accordion-button { font-weight: bold; background-color: #f0f0f0; padding: 8px; }
        .accordion-body { padding: 10px 15px; border: 1px solid #ccc; margin-bottom: 10px; }
        .mb-3 { margin-bottom: 1rem; }
        .mb-2 { margin-bottom: 0.5rem; }
        strong { display: inline-block; width: 140px; }
      </style>
    </head>
    <body>
      ${canvas.querySelector(".offcanvas-body").innerHTML}
    </body>
    </html>
  `;

  const win = window.open('', '', 'width=800,height=700');
  win.document.write(printable);
  win.document.close();
  win.focus();
  win.print();
  win.close();

  printBtn.style.display = "inline-block";
  pdfBtn.style.display = "inline-block";

  followupDetails.classList.remove("show");
  followupHistory.classList.remove("show");
});


//? ================== offcanvas PDF Button ======================
document.getElementById("filePdfBtn").addEventListener("click", () => {
  console.log("offcanvas pdf export called");
  const canvas = document.getElementById("fileDetailCanvas");
  const followupDetails = document.getElementById("fileFollowupDetails");
  const followupHistory = document.getElementById("fileFollowupHistory");
  followupDetails.classList.add("show");
  followupHistory.classList.add("show");

  const contentClone = canvas.querySelector(".offcanvas-body").cloneNode(true);

  contentClone.querySelectorAll("[class]").forEach(el => {
    el.className = el.className
      .split(" ")
      .filter(c => !["bg-dark", "text-white", "text-primary", "text-success", "text-info", "accordion-item", "accordion-body"].includes(c))
      .join(" ");
  });

  const wrapper = document.createElement("div");
  wrapper.innerHTML = `
    <div style="font-family: Arial, sans-serif; color: #000 !important; background: #fff; padding: 0px 20px 20px 20px !important; font-size: 12px;">
      <h3 style="margin-bottom: 20px;">Lead Details</h3>
      <style>
        .accordion-button {
          font-size: 13px !important;
          font-weight: bold;
          background-color: #ffffff;
          border-bottom: 1px solid #ccc;
          padding: 6px 10px;
          margin-top: 12px;
        }
      </style>
      ${contentClone.innerHTML}
    </div>
  `;

  html2pdf().set({
    margin: [0.0, 0.4, 0.4, 0.4],
    filename: `Lead_Details_${new Date().toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).save().then(() => {

    followupDetails.classList.remove("show");
    followupHistory.classList.remove("show");
  });
});
