document.addEventListener("DOMContentLoaded", function () {
  const checkboxes = document.querySelectorAll(".leadCheckbox");
  const selectedCount = document.getElementById("selectedCount");
  const selectAll = document.getElementById("selectAll");
  const searchInput = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearch");
  const tableBody = document.getElementById("leadTableBody");
  const paginationContainer = document.querySelector(".pagination");
  const rowCount = document.getElementById("rowCount");
  const statusFilter = document.getElementById("statusFilter");
  const fromDate = document.getElementById("fromDate");
  const toDate = document.getElementById("toDate");

  let rows = Array.from(tableBody.querySelectorAll("tr"));

  function filterTable() {
    const status = statusFilter.value.toLowerCase();
    const from = new Date(fromDate.value);
    const to = new Date(toDate.value);
    const query = searchInput.value.toLowerCase();

    let visibleRows = 0;

    rows.forEach(row => {
      const leadStatus = row.children[7].textContent.toLowerCase();
      const allocDate = new Date(row.children[8].textContent);
      const rowText = row.textContent.toLowerCase();

      const matchStatus = !status || leadStatus.includes(status);
      const matchDate = (!fromDate.value || allocDate >= from) && (!toDate.value || allocDate <= to);
      const matchSearch = rowText.includes(query);

      if (matchStatus && matchDate && matchSearch) {
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
      noRow.innerHTML = `<td colspan="7" class="text-center text-white">No Leads Found</td>`;
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

  function updateSelectedCount() {
    selectedCount.textContent = document.querySelectorAll(".leadCheckbox:checked").length;
  }

  checkboxes.forEach(cb => cb.addEventListener("change", updateSelectedCount));
  selectAll.addEventListener("change", () => {
    const isChecked = selectAll.checked;
    checkboxes.forEach(cb => cb.checked = isChecked);
    updateSelectedCount();
  });

  document.getElementById("acceptSelected").addEventListener("click", () => {
    const selectedIds = Array.from(document.querySelectorAll(".leadCheckbox:checked")).map(cb => cb.dataset.id);
    if (!selectedIds.length) return;

    fetch("/accept-leads/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ lead_ids: selectedIds })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        alert("Accepted: " + data.updated);
        location.reload();
      } else {
        alert("Failed to accept leads.");
      }
    });
  });

  function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  }

  searchInput.addEventListener("input", filterTable);
  statusFilter.addEventListener("change", filterTable);
  fromDate.addEventListener("change", filterTable);
  toDate.addEventListener("change", filterTable);
  rowCount.addEventListener("change", paginate);

  filterTable();
});

document.getElementById('clearFilters')?.addEventListener('click', function () {
  window.location.reload();
});