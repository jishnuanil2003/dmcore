document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const statusFilter = document.getElementById("statusFilter");
  const fromDate = document.getElementById("fromDate");
  const toDate = document.getElementById("toDate");
  const rowCount = document.getElementById("rowCount");
  const tableBody = document.getElementById("leadTableBody");
  const paginationContainer = document.querySelector(".pagination");

  const rows = Array.from(tableBody.querySelectorAll("tr"));
  const noMatchRow = document.getElementById("noMatchRow");

  function filterTable() {
    const statusVal = statusFilter.value;
    const query = searchInput.value.toLowerCase();
    const from = fromDate.value ? new Date(fromDate.value) : null;
    const to = toDate.value ? new Date(toDate.value) : null;

    let visibleRows = [];

    rows.forEach(row => {
      const addedDate = new Date(row.children[1].textContent.trim());
      const rowStatus = row.children[6].textContent.trim().toLowerCase();
      const rowText = row.textContent.toLowerCase();

      const matchStatus =
        !statusVal ||
        (statusVal === "approved" && rowStatus === "approved") ||
        (statusVal === "pending" && rowStatus === "pending");

      const matchDate =
        (!from || addedDate >= from) &&
        (!to || addedDate <= to);

      const matchSearch = rowText.includes(query);

      if (matchStatus && matchDate && matchSearch) {
        row.style.display = "";
        visibleRows.push(row);
      } else {
        row.style.display = "none";
      }
    });

    if (visibleRows.length === 0 && rows.length > 0) {
      noMatchRow.style.display = "block";
    } else {
      noMatchRow.style.display = "none";
    }

    paginate(visibleRows);
  }

  function paginate(visibleRows) {
    const perPage = parseInt(rowCount.value);
    const totalPages = Math.ceil(visibleRows.length / perPage);

    paginationContainer.innerHTML = "";

    visibleRows.forEach((row, index) => {
      row.style.display = index < perPage ? "" : "none";
    });

    for (let i = 1; i <= totalPages; i++) {
      const li = document.createElement("li");
      li.className = "page-item";
      li.innerHTML = `<a href="#" class="page-link">${i}</a>`;
      li.addEventListener("click", e => {
        e.preventDefault();
        visibleRows.forEach((row, j) => {
          row.style.display = j >= (i - 1) * perPage && j < i * perPage ? "" : "none";
        });
        document.querySelectorAll(".page-item").forEach(p => p.classList.remove("active"));
        li.classList.add("active");
      });
      paginationContainer.appendChild(li);
    }

    if (paginationContainer.firstChild) {
      paginationContainer.firstChild.classList.add("active");
    }
  }

  // Event bindings
  searchInput.addEventListener("input", filterTable);
  statusFilter.addEventListener("change", filterTable);
  fromDate.addEventListener("change", filterTable);
  toDate.addEventListener("change", filterTable);
  rowCount.addEventListener("change", filterTable);

  document.getElementById("clearFilters")?.addEventListener("click", () => window.location.reload());
  document.getElementById("clearSearch")?.addEventListener("click", () => window.location.reload());

  filterTable();
});
