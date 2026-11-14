let dataTable;

document.addEventListener("DOMContentLoaded", function () {
  const rowLimitElement = document.getElementById("rowLimit");
  const rowLimitValue = rowLimitElement ? parseInt(rowLimitElement.value) || 10 : 10;

  dataTable = $('#leadTable').DataTable({
    paging: true,
    searching: false,
    ordering: true,
    order: [],
    lengthChange: false,
    pageLength: rowLimitValue,
    columnDefs: [{ orderable: false, targets: "nosort" }]
  });

  rowLimitElement?.addEventListener("change", function () {
    const val = parseInt(this.value) || 10;
    dataTable.page.len(val).draw();
  });

  setupEventListeners();
  applyFilters();
  filterCategoryByClient();
});


function setupEventListeners() {
  const filterFields = ["clientFilter", "categoryFilter", "employeeFilter", "fromDate", "toDate", "searchInput"];

  // Filters
  filterFields.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", applyFilters);
      el.addEventListener("change", applyFilters);
    }
  });

  // Clear filters
  document.getElementById("clearFilters")?.addEventListener("click", () => {
    filterFields.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.value = "";
    });
    applyFilters();
  });

  // Clear search
  document.getElementById("clearSearch")?.addEventListener("click", () => {
    document.getElementById("searchInput").value = "";
    applyFilters();
  });

  // Select all visible rows
  document.getElementById("checkAll")?.addEventListener("change", function () {
    const checked = this.checked;
    document.querySelectorAll("#leadTable tbody tr").forEach(row => {
      if ($(row).is(":visible")) {
        const cb = row.querySelector("input[type='checkbox']");
        if (cb) cb.checked = checked;
      }
    });
  });

  // Transfer leads
 document.getElementById("transferBtn")?.addEventListener("click", function () {
  console.log("🔁 Transfer button clicked");

  // Check for checkbox selection
  const selectedCheckboxes = document.querySelectorAll("input[name='selected_leads']:checked");
  const selected = Array.from(selectedCheckboxes).map(cb => cb.value);

  if (selected.length === 0) {
    alert("Select at least one lead.");
    return;
  }

  const csrfEl = document.querySelector("[name=csrfmiddlewaretoken]");
  if (!csrfEl) {
    return;
  }

  const csrfToken = csrfEl.value;
  fetch("/transfer-selected-leads/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify({ leads: selected })
  })
    .then(res => {
      return res.json();
    })
    .then(data => {
      if (data.success) {
        window.location.reload();
      } else {
        alert("Transfer failed: " + (data.message || "Unknown error"));
      }
    })
    .catch(err => {
      alert("Something went wrong during transfer.");
    });
});


  // PDF export
  document.getElementById("pdfBtn")?.addEventListener("click", exportPDF);

  // EXCEL export
document.getElementById("excelBtn").addEventListener("click", function () {
  const clientDropdown = document.getElementById("clientFilter");
  const selectedClient = clientDropdown?.options[clientDropdown.selectedIndex]?.text;
  const clientName = clientDropdown?.value ? selectedClient.trim().replace(/\s+/g, "_") : null;
  const filename = clientName ? `${clientName}_leads.xlsx` : `leads.xlsx`;

  const table = document.getElementById("leadTable");
  const visibleRows = Array.from(table.querySelectorAll("tbody tr")).filter(row => row.style.display !== "none");

  // Build new array with clean headers and split values
  const data = [
    ["Collected By", "Date", "Name", "Source", "Email", "Phone", "Status"]
  ];

  visibleRows.forEach(row => {
    const cells = row.querySelectorAll("td");

    // Extract and split values
    const collectedByText = cells[1]?.innerText.split("\n");
    const nameSourceText = cells[2]?.innerText.split("\n");
    const contactText = cells[3]?.innerText.split("\n");
    const statusText = cells[4]?.innerText;

    data.push([
      collectedByText?.[0] || "",
      collectedByText?.[1] || "",
      nameSourceText?.[0] || "",
      nameSourceText?.[1] || "",
      contactText?.[0] || "",
      contactText?.[1] || "",
      statusText || ""
    ]);
  });

  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(data);
  XLSX.utils.book_append_sheet(wb, ws, "Leads");

  XLSX.writeFile(wb, filename);
})

  document.getElementById("clientFilter")?.addEventListener("change", filterCategoryByClient);
}

document.getElementById("clientFilter")?.addEventListener("change", () => {
  document.getElementById("categoryFilter").value = "";
  filterCategoryByClient();
  applyFilters();
});


// ? =========== Print ==========
document.getElementById("printBtn")?.addEventListener("click", () => {
  const table = document.getElementById("leadTable");
  const clonedTable = table.cloneNode(true);
  clonedTable.querySelectorAll("thead th:first-child, tbody td:first-child").forEach(el => el.remove());

  Array.from(clonedTable.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  Array.from(clonedTable.querySelectorAll("tbody tr")).forEach(row => {
    const tds = row.querySelectorAll("td");
    const badge = tds[3]?.querySelector(".badge");
    if (badge) tds[3].textContent = badge.innerText.trim();
  });

  clonedTable.className = "table table-bordered table-sm";
  clonedTable.style.fontSize = "10px";
  clonedTable.style.width = "100%";
  clonedTable.style.borderCollapse = "collapse";
  clonedTable.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.border = "1px solid #ccc";
    th.style.padding = "6px";
    th.style.textAlign = "center";
  });

  clonedTable.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  const wrapper = document.createElement("div");
  wrapper.style.padding = "20px";
  wrapper.style.fontFamily = "sans-serif";
  wrapper.style.backgroundColor = "#ffffff";
  wrapper.innerHTML = `<h3 style="text-align: center; margin-bottom: 15px;">Verified Leads for Transfer</h3>`;
  wrapper.appendChild(clonedTable);
  const originalContent = document.body.innerHTML;
  document.body.innerHTML = "";
  document.body.style.backgroundColor = "#ffffff";
  document.body.appendChild(wrapper);

  window.print();
  setTimeout(() => {
    console.log("🔄 Restoring original page...");
    document.body.innerHTML = originalContent;
    location.reload();
  }, 0);
});

// ? ========== share ==========
document.getElementById("shareBtn")?.addEventListener("click", () => {
  const table = document.getElementById("leadTable").cloneNode(true);

  // Remove checkboxes
  table.querySelectorAll("thead th:first-child, tbody td:first-child").forEach(el => el.remove());
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  // Strip badge
Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
  const tds = row.querySelectorAll("td");
  const badge = tds[3]?.querySelector(".badge");
  if (badge) tds[3].textContent = badge.innerText.trim();
});


  // Format
  table.className = "table table-bordered table-sm";
  table.style.fontSize = "10px";
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";
  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.border = "1px solid #ccc";
    th.style.padding = "6px";
    th.style.textAlign = "center";
  });
  table.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  const wrapper = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = "Verified Leads for Transfer";
  title.style.textAlign = "center";
  title.style.marginBottom = "15px";
  wrapper.appendChild(title);
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    filename: `Leads_${new Date().toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).outputPdf("blob").then(blob => {
    const url = URL.createObjectURL(blob);
    const modal = new bootstrap.Modal(document.getElementById("shareModal"));
    modal.show();

    // WhatsApp
    document.getElementById("shareViaWhatsApp")?.addEventListener("click", () => {
      console.log("📲 WhatsApp share clicked");
        
      generateShareablePDF(blob => {
        console.log("📄 PDF blob ready");
      
        // Download locally (optional)
        const file = new File([blob], "Lead_Report.pdf", { type: "application/pdf" });
        const fileURL = URL.createObjectURL(file);
        const a = document.createElement("a");
        a.href = fileURL;
        a.download = "Lead_Report.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(fileURL);
      
        // Open WhatsApp
        const message = encodeURIComponent("Please find the lead report attached.");
        window.open(`https://wa.me/?text=${message}`, "_blank");
      });
    });


    // Email toggle
    document.getElementById("shareViaEmail").onclick = () => {
      document.getElementById("emailSection").style.display = "block";
    };

    // Email send
    document.getElementById("sendEmail")?.addEventListener("click", () => {
      console.log("📨 Send Email clicked");
    
      const emails = document.getElementById("emailInput").value.trim();
      const message = document.getElementById("emailMessage").value.trim();
    
      if (!emails) {
        alert("Please enter at least one email address.");
        return;
      }
    
      generateShareablePDF(blob => {
        const formData = new FormData();
        formData.append("pdf", blob, "Lead_Report.pdf");
        formData.append("emails", emails);
        formData.append("message", message);
      
        fetch("/send_lead_pdf_mail/", {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
          },
          body: formData
        })
        .then(res => res.json())
        .then(data => {
          console.log("📨 Email response:", data);
          if (data.success) {
            alert("Email sent successfully.");
            document.getElementById("emailInput").value = "";
            document.getElementById("emailMessage").value = "";
            document.getElementById("emailSection").style.display = "none";
          
            // Hide modal
            const modal = bootstrap.Modal.getInstance(document.getElementById("shareModal"));
            modal?.hide();
          } else {
            alert("Email failed: " + (data.message || "Unknown error"));
          }
        })
        .catch(err => {
          console.error("❌ Email error:", err);
          alert("Something went wrong while sending the email.");
        });
      });
    });

  });
});






// //fumctions

function applyFilters() {
  const client = document.getElementById("clientFilter").value;
  const category = document.getElementById("categoryFilter").value;
  const emp = document.getElementById("employeeFilter").value;
  const from = new Date(document.getElementById("fromDate").value);
  const to = new Date(document.getElementById("toDate").value);
  const search = document.getElementById("searchInput").value.toLowerCase();

  let visibleCount = 0;

  dataTable.rows().every(function () {
    const row = this.node();
    const rowClient = row.dataset.client;
    const rowCategory = row.dataset.category;
    const rowEmp = row.dataset.employee;
    const rowDate = new Date(row.dataset.date);
    const text = row.innerText.toLowerCase();

    let show = true;
    if (client && rowClient !== client) show = false;
    if (category && rowCategory !== category) show = false;
    if (emp && rowEmp !== emp) show = false;
    if (from && rowDate < from) show = false;
    if (to && rowDate > to) show = false;
    if (search && !text.includes(search)) show = false;

    $(row).toggle(show);
    if (show) visibleCount++;

    const noMsg = document.getElementById("noResultsMessage");
    const tableWrapper = document.getElementById("tableWrapper");
    const infoElement = document.querySelector(".dataTables_info");
    const paginateElement = document.querySelector(".dataTables_paginate");
      
    if (visibleCount === 0) {
      if (noMsg) noMsg.style.display = "block";
      if (tableWrapper) tableWrapper.style.display = "none";
      if (infoElement) infoElement.style.display = "none";
      if (paginateElement) paginateElement.style.display = "none";
    } else {
      if (noMsg) noMsg.style.display = "none";
      if (tableWrapper) tableWrapper.style.display = "";
      if (infoElement) infoElement.style.display = "";
      if (paginateElement) paginateElement.style.display = "";
    }

  });

  const noMsg = document.getElementById("noResultsMessage");
  if (noMsg) {
    noMsg.style.display = visibleCount === 0 ? "block" : "none";
  }

  dataTable.draw();
}


function exportPDF() {
  const table = document.getElementById("leadTable").cloneNode(true);
  table.querySelectorAll("thead th:first-child, tbody td:first-child").forEach(el => el.remove());
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  Array.from(table.querySelectorAll("td")).forEach(td => {
    const badge = td.querySelector(".badge");
    if (badge) {
      td.textContent = badge.innerText.trim();
    }
  });

  table.classList = "table table-bordered table-sm";
  table.style.fontSize = "10px";
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";
  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.border = "1px solid #ccc";
    th.style.padding = "6px";
    th.style.textAlign = "center";
  });

  table.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  const wrapper = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = "Verified Leads for Transfer";
  title.style.textAlign = "center";
  title.style.marginBottom = "15px";
  wrapper.appendChild(title);
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    filename: `Leads_${new Date().toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).save();
}


function filterCategoryByClient() {
  const selectedClientId = document.getElementById("clientFilter")?.value;
  const categoryDropdown = document.getElementById("categoryFilter");
  if (!categoryDropdown) return;

  // Always show "All"
  const allOption = categoryDropdown.querySelector("option[value='']");
  allOption.style.display = "";

  // Reset selection to "All"
  categoryDropdown.value = "";

  // Hide all category options
  categoryDropdown.querySelectorAll("option").forEach(opt => {
    if (opt.value !== "") opt.style.display = "none";
  });

  if (!selectedClientId) return;

  // Show only options related to this client
  categoryDropdown.querySelectorAll(".client-" + selectedClientId).forEach(opt => {
    opt.style.display = "";
  });
}

//? ========= share pdf generator =========
function generateShareablePDF(callback) {
  const table = document.getElementById("leadTable").cloneNode(true);

  // Remove checkbox column
  table.querySelectorAll("thead th:first-child, tbody td:first-child").forEach(el => el.remove());

  // Remove hidden rows
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  // Strip badge from status column only
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    const tds = row.querySelectorAll("td");
    const badge = tds[3]?.querySelector(".badge");
    if (badge) tds[3].textContent = badge.innerText.trim();
  });

  // Table styling
  table.className = "table table-bordered table-sm";
  table.style.fontSize = "10px";
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";

  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.border = "1px solid #ccc";
    th.style.padding = "6px";
    th.style.textAlign = "center";
  });

  table.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  // Wrapper
  const wrapper = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = "Verified Leads for Transfer";
  title.style.textAlign = "center";
  title.style.marginBottom = "15px";
  wrapper.appendChild(title);
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    filename: `Leads_${new Date().toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).outputPdf("blob").then(callback);
}
