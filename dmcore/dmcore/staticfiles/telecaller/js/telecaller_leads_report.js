document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("reportTableBody");
  const searchInput = document.getElementById("searchInput");
  const rowLimit = document.getElementById("rowCount");
  const pagination = document.getElementById("pagination");
  const dateCards = document.querySelectorAll(".date-card");
  const leadsTable = document.getElementById("leadsTable");
  const printBtn = document.getElementById("printBtn");
  const pdfBtn = document.getElementById("pdfBtn");
  const excelBtn = document.getElementById("excelBtn");

  let allLeads = [];
  let filteredLeads = [];

  leadsTable.style.display = "none";

  function fetchAllLeads() {
    fetch("/get-all-leads-telecaller/")
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          allLeads = data.leads || [];
          console.log("✅ All leads fetched:", allLeads.length);
          console.table(allLeads);
        } else {
          console.warn("⚠ Failed to load leads:", data.message);
        }
      })
      .catch(err => console.error("❌ Fetch error:", err));
  }

  fetchAllLeads();

  dateCards.forEach(card => {
    card.addEventListener("click", () => {
      const date = card.dataset.date;
      filteredLeads = allLeads.filter(l => l.assigned_date === date);
      console.log(`📅 Selected Date: ${date} | Leads: ${filteredLeads.length}`);
      renderTable(filteredLeads);
      leadsTable.style.display = "table";
      dateCards.forEach(c => c.classList.remove("border-primary"));
      card.classList.add("border", "border-primary");
    });
  });

  function renderTable(data) {
    tableBody.innerHTML = "";
    if (data.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" class="text-center text-white">No Leads Found</td></tr>`;
      pagination.innerHTML = "";
      return;
    }
    paginate(data);
  }

  function paginate(data) {
    const perPage = parseInt(rowLimit.value) || 10;
    const pages = Math.ceil(data.length / perPage);
    pagination.innerHTML = "";
    tableBody.innerHTML = "";

    const showPage = (pageNum) => {
      tableBody.innerHTML = "";
      const start = (pageNum - 1) * perPage;
      const end = start + perPage;
      const pageData = data.slice(start, end);
      pageData.forEach((row, index) => {
        tableBody.innerHTML += `
          <tr>
            <td>${index + 1}</td>
            <td>${row.assigned_date}</td>
            <td>${row.name}</td>
            <td>${row.email}</td>
            <td>${row.contact}</td>
            <td>${row.status}</td>
            <td><button class="btn btn-sm btn-outline-info view-details" data-id="${row.id}" data-bs-toggle="offcanvas" data-bs-target="#leadDetailsCanvas">Details</button></td>
          </tr>`;
      });
    };

    for (let i = 1; i <= pages; i++) {
      const btn = document.createElement("button");
      btn.className = "btn btn-sm btn-outline-light me-1";
      btn.textContent = i;
      btn.addEventListener("click", () => {
        showPage(i);
        Array.from(pagination.children).forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
      });
      pagination.appendChild(btn);
    }

    if (pages > 0) {
      pagination.firstChild.classList.add("active");
      showPage(1);
    }
  }

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();
    const filtered = filteredLeads.filter(row =>
      Object.values(row).some(val => val?.toString().toLowerCase().includes(query))
    );
    renderTable(filtered);
  });

  rowLimit.addEventListener("change", () => renderTable(filteredLeads));

  document.addEventListener("click", function (e) {
    if (e.target.classList.contains("view-details")) {
      const leadId = e.target.dataset.id;

      fetch(`/lead_data_collection_hr/${leadId}/`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            document.getElementById("leadName").textContent = data.lead.name;
            document.getElementById("leadEmail").textContent = data.lead.email;
            document.getElementById("leadPhone").textContent = data.lead.contact;
            document.getElementById("leadAddedDate").textContent = data.lead.added_date;
            document.getElementById("clientName").textContent = data.client.name;
            document.getElementById("clientBusiness").textContent = data.client.business;
            document.getElementById("clientCategory").textContent = data.category || "-";
            document.getElementById("collectedByName").textContent = data.collected_by.name;
            document.getElementById("collectedCategory").textContent = data.category || "-";

            fetch(`/get-followup-data/${leadId}/`)
              .then(res => res.json())
              .then(extra => {
                if (extra.success) {
                  document.getElementById("followupDetailsContent").innerHTML = extra.details.length > 0
                    ? extra.details.map(d => `
                        <div class="mb-2">
                          <p><strong>Date:</strong> ${d.date}</p>
                          <p><strong>Response:</strong> ${d.response}</p>
                          <p><strong>Next Follow Up:</strong> ${d.next}</p>
                          <p><strong>Status:</strong> ${d.status}</p>
                          <hr>
                        </div>`).join("")
                    : "<p>No follow-up details available.</p>";

                  document.getElementById("followupHistoryContent").innerHTML = extra.history.length > 0
                    ? extra.history.map(h => `
                        <div class="mb-2">
                          <p><strong>Date:</strong> ${h.date}</p>
                          <p><strong>Allocated to:</strong> ${h.telecaller}</p>
                          <p><strong>Note:</strong> ${h.note}</p>
                          <p><strong>Status:</strong> ${h.status}</p>
                          <hr>
                        </div>`).join("")
                    : "<p>No follow-up history available.</p>";

                  document.getElementById("recordingsContent").innerHTML = extra.recordings.length > 0
                    ? extra.recordings.map(r => `
                        <div class="mb-3">
                          <p><strong>Date:</strong> ${r.date}</p>
                          <audio controls src="${r.url}" class="w-100"></audio>
                        </div>`).join("")
                    : "<p>No recordings found.</p>";
                }
              });
          }
        });
    }
  });

  // 🖨 Print
  printBtn.addEventListener("click", () => {
    const table = leadsTable.cloneNode(true);
    table.querySelectorAll("thead tr").forEach(row => row.deleteCell(6));
    table.querySelectorAll("tbody tr").forEach(row => row.deleteCell(6));
    const win = window.open("", "", "width=900,height=650");
    win.document.write(`
      <html><head><title>Leads Report</title>
      <style>
        body { background: white; color: black; font-family: sans-serif; padding: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th { background-color: #000; color: #fff; border: 1px solid #000; padding: 6px; }
        td { border: 1px solid #000; padding: 4px; text-align: center; }
      </style></head><body>
      <h2 style="text-align:center;">Lead List</h2>
      ${table.outerHTML}
      </body></html>`);
    win.document.close();
    win.print();
  });

  // 📄 PDF
  pdfBtn.addEventListener("click", () => {
    const table = leadsTable.cloneNode(true);
    table.querySelectorAll("thead tr").forEach(row => row.deleteCell(6));
    table.querySelectorAll("tbody tr").forEach(row => row.deleteCell(6));

table.querySelectorAll("th").forEach(th => {
  th.style.backgroundColor = "#000";
  th.style.color = "#fff";
  th.style.fontWeight = "bold";
  th.style.border = "1px solid #000";
  th.style.padding = "6px";
  th.style.textAlign = "center";
});

table.querySelectorAll("td").forEach(td => {
  td.style.backgroundColor = "#fff";
  td.style.color = "#000";
  td.style.border = "1px solid #000";
  td.style.padding = "4px";
  td.style.textAlign = "center";
});


    table.querySelectorAll("td").forEach(td => {
      td.style.border = "1px solid #000";
      td.style.padding = "4px";
      td.style.textAlign = "center";
    });

    const wrapper = document.createElement("div");
    wrapper.style.backgroundColor = "#fff";
    wrapper.style.color = "#000";

    const title = document.createElement("h3");
    title.textContent = "Lead List";
    title.style.textAlign = "center";
    wrapper.appendChild(title);
    wrapper.appendChild(table);

    html2pdf().set({
      margin: [0.4, 0.2],
      filename: `Leads_${new Date().toISOString().split("T")[0]}.pdf`,
      image: { type: "jpeg", quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
    }).from(wrapper).save();
  });

  // 📊 Excel
  excelBtn.addEventListener("click", () => {
    const rows = Array.from(leadsTable.querySelectorAll("tbody tr")).filter(r => r.style.display !== "none");
    const data = [["No", "Assigned Date", "Lead Name", "Email", "Phone Number", "Status"]];
    rows.forEach(row => {
      const cells = row.querySelectorAll("td");
      if (cells.length >= 6) {
        data.push([
          cells[0].innerText, cells[1].innerText, cells[2].innerText,
          cells[3].innerText, cells[4].innerText, cells[5].innerText
        ]);
      }
    });

    const wb = XLSX.utils.book_new();
    const ws = XLSX.utils.aoa_to_sheet(data);
    XLSX.utils.book_append_sheet(wb, ws, "Leads");
    XLSX.writeFile(wb, `Leads_${new Date().toISOString().split("T")[0]}.xlsx`);
  });
});
