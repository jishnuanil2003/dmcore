document.addEventListener("DOMContentLoaded", function () {
  const tableBody = document.getElementById("leadTableBody");
  const rows = Array.from(tableBody.querySelectorAll("tr"));
  const rowCount = document.getElementById("rowCount");
  const searchInput = document.getElementById("searchInput");
  const clearSearch = document.getElementById("clearSearch");
  const statusFilter = document.getElementById("statusFilter");
  const fromDate = document.getElementById("fromDate");
  const toDate = document.getElementById("toDate");
  const paginationContainer = document.querySelector(".pagination");

  function filterTable() {
    const query = searchInput.value.toLowerCase();
    const status = statusFilter.value.toLowerCase();
    const from = new Date(fromDate.value);
    const to = new Date(toDate.value);
    let visibleRows = 0;

    rows.forEach(row => {
      const rowText = row.textContent.toLowerCase();
      const leadStatus = row.children[7].textContent.toLowerCase();
      const allocDate = new Date(row.children[9].textContent);

      const matchSearch = rowText.includes(query);
      const matchStatus = !status || leadStatus.includes(status);
      const matchDate = (!fromDate.value || allocDate >= from) && (!toDate.value || allocDate <= to);

      if (matchSearch && matchStatus && matchDate) {
        row.style.display = "";
        visibleRows++;
      } else {
        row.style.display = "none";
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

  function paginate() {
    const perPage = parseInt(rowCount.value);
    const visibleRows = Array.from(rows).filter(r => r.style.display !== "none");
    const totalPages = Math.ceil(visibleRows.length / perPage);
    paginationContainer.innerHTML = "";

    visibleRows.forEach((row, i) => {
      row.style.display = (i < perPage) ? "" : "none";
    });

    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.className = "page-item";
      li.innerHTML = `<a href="#" class="page-link">${i}</a>`;
      li.addEventListener("click", (e) => {
        e.preventDefault();
        visibleRows.forEach((row, j) => {
          row.style.display = (j >= (i - 1) * perPage && j < i * perPage) ? "" : "none";
        });
        document.querySelectorAll(".page-item").forEach(p => p.classList.remove("active"));
        li.classList.add("active");
      });
      paginationContainer.appendChild(li);
    }

    if (totalPages > 0) paginationContainer.firstChild.classList.add("active");
  }

  document.getElementById('clearFilters')?.addEventListener('click', () => window.location.reload());
  clearSearch?.addEventListener('click', () => {
    searchInput.value = '';
    filterTable();
  });

  searchInput?.addEventListener("input", filterTable);
  statusFilter?.addEventListener("change", filterTable);
  fromDate?.addEventListener("change", filterTable);
  toDate?.addEventListener("change", filterTable);
  rowCount?.addEventListener("change", paginate);

  filterTable();

  // ==========================================
  // Bulk Waste Modal Logic (newly added below)
  // ==========================================
  const wasteBtn = document.querySelector(".btn-danger"); // top waste button
  const wasteModal = new bootstrap.Modal(document.getElementById("wasteSelectionModal"));
  const reasonModal = new bootstrap.Modal(document.getElementById("wasteReasonModal"));

  const selectAll = document.getElementById("selectAllWaste");
  const proceedBtn = document.getElementById("proceedToWasteBtn");
  const confirmBtn = document.getElementById("confirmBulkWasteBtn");

  wasteBtn?.addEventListener("click", () => wasteModal.show());

  selectAll?.addEventListener("change", function () {
    document.querySelectorAll(".wasteCheckbox").forEach(cb => cb.checked = this.checked);
  });

  proceedBtn?.addEventListener("click", () => {
    const selected = Array.from(document.querySelectorAll(".wasteCheckbox:checked")).map(cb => cb.value);
    if (selected.length === 0) {
      alert("Select at least one lead.");
      return;
    }
    reasonModal.show();
  });

  confirmBtn?.addEventListener("click", () => {
    const selected = Array.from(document.querySelectorAll(".wasteCheckbox:checked")).map(cb => cb.value);
    const reason = document.getElementById("bulkWasteReason").value.trim();

    if (!reason) {
      alert("Please provide a reason.");
      return;
    }

    const payload = {
      lead_ids: JSON.stringify(selected),
      status: "Waste Lead",
      reason: reason
    };

    console.log("📤 Sending Waste Request:", payload);

    fetch("/bulk-update-leads/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: new URLSearchParams(payload)
    })
    .then(res => res.json())
    .then(data => {
      console.log("✅ Server Response:", data);
      if (data.success) {
        alert("Leads marked as waste.");
        location.reload();
      } else {
        alert("Failed to mark leads.");
      }
    })
    .catch(error => {
      console.error("❌ Error in fetch:", error);
      alert("Something went wrong.");
    });

    reasonModal.hide();
    wasteModal.hide();
  });


const blurOverlay = document.getElementById("blurOverlay");
const reasonModalEl = document.getElementById("wasteReasonModal");

reasonModalEl.addEventListener("show.bs.modal", () => {
  blurOverlay.style.display = "block";
});
reasonModalEl.addEventListener("hidden.bs.modal", () => {
  blurOverlay.style.display = "none";
});

const recallBtn = document.getElementById("btnrecall");

if (recallBtn) {
  recallBtn.addEventListener("click", function () {
    const leadId = this.getAttribute("data-lead-id");

    fetch(`/recall-lead/${leadId}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
      }
    })
      .then(res => res.json())
      .then(data => {
        console.log("✅ Recall response:", data);
        if (data.success) {
          alert("Lead recalled successfully.");
          location.reload();
        } else {
          alert("Failed to recall lead.");
        }
      })
      .catch(err => {
        console.error("Recall error:", err);
        alert("Something went wrong.");
      });
  });
}



});
