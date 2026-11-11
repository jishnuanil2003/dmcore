document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const fromDate = document.getElementById("fromDate");
  const toDate = document.getElementById("toDate");
  const nextFollowUpDate = document.getElementById("nextFollowUpDate");
  const rowCount = document.getElementById("rowCount");
  const tableBody = document.getElementById("leadTableBody");
  const paginationContainer = document.querySelector(".pagination");
  const offcanvas = new bootstrap.Offcanvas('#updateOffcanvas');
  let rows = Array.from(tableBody.querySelectorAll("tr"));

  function filterTable() {
    const statusVal = statusFilter.value.toLowerCase();
    const from = new Date(fromDate.value);
    const to = new Date(toDate.value);
    const nextDate = new Date(nextFollowUpDate.value);
    const query = searchInput.value.toLowerCase();
    let visibleRows = 0;

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const rowStatus = row.children[8].textContent.trim().toLowerCase();
      const allocDate = new Date(row.children[9].textContent.trim());
      const followDate = new Date(row.children[10].textContent.trim());

      const matchSearch = text.includes(query);
      const matchStatus = !statusVal || rowStatus.includes(statusVal);
      const matchFrom = !fromDate.value || allocDate >= from;
      const matchTo = !toDate.value || allocDate <= to;
      const matchNext = !nextFollowUpDate.value || followDate.toDateString() === nextDate.toDateString();

      if (matchSearch && matchStatus && matchFrom && matchTo && matchNext) {
        row.dataset.filtered = "true";
        visibleRows++;
    } else {
        row.dataset.filtered = "false";
    }
    });

    document.getElementById("noLeadsRow")?.remove();
    if (visibleRows === 0) {
      const noRow = document.createElement("tr");
      noRow.id = "noLeadsRow";
      noRow.innerHTML = `<td colspan="8" class="text-center text-white">No Leads Found</td>`;
      tableBody.appendChild(noRow);
    }

    paginate();
  }

let currentPage = 1;

function paginate() {

    rows.forEach(row => {
        if (row.dataset.filtered === "false") {
            row.style.display = "none";
        }
    });

    const perPage = parseInt(rowCount.value);

    const filteredRows = rows.filter(row =>
        row.dataset.filtered !== "false"
    );

    const totalPages = Math.ceil(filteredRows.length / perPage);

    paginationContainer.innerHTML = "";

    filteredRows.forEach((row, index) => {

        const start = (currentPage - 1) * perPage;
        const end = start + perPage;

        row.style.display =
            (index >= start && index < end)
                ? ""
                : "none";
    });

    for (let i = 1; i <= totalPages; i++) {

        const li = document.createElement("li");

        li.className =
            `page-item ${i === currentPage ? "active" : ""}`;

        li.innerHTML =
            `<a href="#" class="page-link">${i}</a>`;

        li.addEventListener("click", function(e) {

            e.preventDefault();

            currentPage = i;

            paginate();
        });

        paginationContainer.appendChild(li);
    }
}

  document.querySelectorAll(".openOffcanvasBtn").forEach(btn => {
    btn.addEventListener("click", () => {
      const leadId = btn.dataset.id;
      console.log("Opening offcanvas for leadId:", leadId);
      document.getElementById("leadId").value = leadId;

      fetch(`/lead_data_collection_hr/${leadId}/`)
        .then(res => res.json())
        .then(data => {
          console.log("Lead data fetched============:", data);
          console.log("🧪 Next follow-up from backend:", data.next_followup);
          if (data.success) {
            document.getElementById("leadName").textContent = data.lead.name;
            document.getElementById("leadEmail").textContent = data.lead.email;
            document.getElementById("leadPhone").textContent = data.lead.contact;
            document.getElementById("leadAddedDate").textContent = data.lead.added_date;
            document.getElementById("clientName").textContent = data.client.name;
            document.getElementById("clientBusiness").textContent = data.client.business;
            document.getElementById("telecallerName").textContent = data.telecaller.name;
            document.getElementById("collectedByName").textContent = data.collected_by.name;
            document.getElementById("clientCategory").textContent = data.category || "-";
            document.getElementById("collectedCategory").textContent = data.category || "-";
            document.getElementById("currentStatus").textContent = data.current_status || "-";
            document.getElementById("nextFollowDateDisplay").textContent = data.next_followup || "-";

            offcanvas.show();

            fetch(`/get-followup-data/${leadId}/`)
              .then(res => res.json())
              .then(extra => {
                console.log("Follow-up extra fetched:", extra);
                if (extra.success) {
                  document.getElementById("followupDetailsContent").innerHTML = extra.details.map(d =>
                    `<div class="mb-2">
                      <h6>${d.telecaller}</h6>
                      <p><strong>Date:</strong> ${d.date}</p>
                      <p><strong>Response:</strong> ${d.response}</p>
                      <p><strong>Next Follow Up:</strong> ${d.next}</p>
                      <p><strong>Status:</strong> ${d.status}</p>
                      <hr>
                    </div>`).join("");

                  document.getElementById("followupHistoryContent").innerHTML = extra.history.map(h =>
                    `<div class="mb-2">
                      <h6>${h.client}</h6>
                      <p><strong>Date:</strong> ${h.date}</p>
                      <p><strong>Allocated to:</strong> ${h.telecaller}</p>
                      <p><strong>Note:</strong> ${h.note}</p>
                      <p><strong>Status:</strong> <strong>${h.status}</strong></p>
                      <hr>
                    </div>`).join("");

                  document.getElementById("recordingsContent").innerHTML = extra.recordings.map(r =>
                    `<div class="mb-3">
                      <p><strong>Date:</strong> ${r.date}</p>
                      <audio controls src="${r.url}" class="w-100"></audio>
                    </div>`).join("");


                  document.getElementById("leadSource").textContent =
                        extra.more_details.source || "-";

                    let html = "";

                    extra.more_details.fields.forEach(function(field){

                        html += `
                            <p class="mb-1">
                                <strong>${field.field_name} :</strong>
                                <span>${field.field_data}</span>
                            </p>
                        `;

                    });

                    document.getElementById("leadExtraFields").innerHTML = html;
                }
              })
              .catch(err => console.error("Follow-up data fetch error:", err));
          } else {
            console.warn("Failed to load lead data:", data.message);
            alert("Failed to load lead data.");
          }
        })
        .catch(error => {
          console.error("Fetch error:", error);
          alert("An error occurred while loading lead data.");
        });
    });
  });


const wasteModal = new bootstrap.Modal(document.getElementById("wasteModal"));

document.getElementById("markWasteBtn").addEventListener("click", () => {
  const leadId = document.getElementById("leadId").value;
  console.log("Waste status triggered for lead:", leadId);
  document.getElementById("wasteReason").value = "";
  wasteModal.show();
});

document.getElementById("confirmWasteBtn").addEventListener("click", () => {
  const leadId = document.getElementById("leadId").value;
  const reason = document.getElementById("wasteReason").value.trim();

  if (!reason) {
    alert("Please provide a reason.");
    return;
  }

  fetch("/update-lead-status/", {
    method: "POST",
    headers: {
      "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      lead_id: leadId,
      status: "Waste Lead",
      reason: reason
    })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Lead marked as waste.");
        location.reload();
      } else {
        alert("Failed to update status.");
      }
    });

  wasteModal.hide();
});


  // Status change buttons
  document.getElementById("btnLeadJoined").addEventListener("click", () => {
    const leadId = document.getElementById("leadId").value;
    console.log("Status Change: Lead Joined", leadId);
    updateLeadStatus(leadId, "Lead Joined");
  });

  document.getElementById("btnLeadClosed").addEventListener("click", () => {
    const leadId = document.getElementById("leadId").value;
    console.log("Status Change: Lead Closed", leadId);
    updateLeadStatus(leadId, "Lead Closed");
  });



  function updateLeadStatus(leadId, status, reason = "") {
    const formData = new FormData();
    formData.append("lead_id", leadId);
    formData.append("status", status);
    if (reason) formData.append("reason", reason);

    fetch("/update-lead-status/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert("Lead status updated.");
          location.reload();
        } else {
          alert("Failed to update status.");
        }
      })
      .catch(err => {
        console.error("Status update error:", err);
        alert("An error occurred while updating status.");
      });
  }

  document.getElementById("followupForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    for (const [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }

    fetch("/submit-followup-update/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert("Follow-up updated.");
          location.reload();
        } else {
          alert("Update failed.");
        }
      });
  });

  searchInput.addEventListener("input", filterTable);
  statusFilter.addEventListener("change", filterTable);
  fromDate.addEventListener("change", filterTable);
  toDate.addEventListener("change", filterTable);
  nextFollowUpDate.addEventListener("change", filterTable);
  rowCount.addEventListener("change", function () {
    currentPage = 1;
    paginate();
});
  document.getElementById("clearFilters").addEventListener("click", () => location.reload());

  document.getElementById("clearSearch").addEventListener("click", () => {
    location.reload()
  });


  filterTable();
});
