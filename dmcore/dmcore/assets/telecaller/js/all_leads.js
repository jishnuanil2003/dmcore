document.addEventListener("DOMContentLoaded", function () {
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
          const rawStatus = row.children[6].textContent.toLowerCase();
          const allocDate = new Date(row.children[7].textContent);
          const rowText = row.textContent.toLowerCase();

          const matchStatus = !status || rawStatus.includes(status);
          const matchDate =
              (!fromDate.value || allocDate >= from) &&
              (!toDate.value || allocDate <= to);
          const matchSearch = rowText.includes(query);

          if (matchStatus && matchDate && matchSearch) {
              row.dataset.filtered = "true";
              visibleRows++;
          } else {
              row.dataset.filtered = "false";
              row.style.display = "none";
          }
      });

      document.getElementById("noLeadsRow")?.remove();

      if (visibleRows === 0) {
          const noRow = document.createElement("tr");
          noRow.id = "noLeadsRow";
          noRow.innerHTML =
              `<td colspan="8" class="text-center text-white">No Leads Found</td>`;
          tableBody.appendChild(noRow);
      }

      paginate(1);
  }

  function paginate(page = 1) {
    const perPage = parseInt(rowCount.value);

    const filteredRows = rows.filter(
        row => row.dataset.filtered === "true"
    );

    const totalPages = Math.ceil(filteredRows.length / perPage);

    paginationContainer.innerHTML = "";

    filteredRows.forEach(row => {
        row.style.display = "none";
    });

    const start = (page - 1) * perPage;
    const end = start + perPage;

    filteredRows.slice(start, end).forEach(row => {
        row.style.display = "";
    });

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement("li");
        li.className = `page-item ${i === page ? "active" : ""}`;

        li.innerHTML = `
            <a href="#" class="page-link">${i}</a>
        `;

        li.addEventListener("click", function (e) {
            e.preventDefault();
            paginate(i);
        });

        paginationContainer.appendChild(li);
    }
}

  searchInput.addEventListener("input", filterTable);
  statusFilter.addEventListener("change", filterTable);
  fromDate.addEventListener("change", filterTable);
  toDate.addEventListener("change", filterTable);
  rowCount.addEventListener("change", () => paginate(1));

  document.getElementById("clearFilters")?.addEventListener("click", () => window.location.reload());
  clearBtn?.addEventListener("click", () => {
    searchInput.value = "";
    filterTable();
  });

  filterTable();
});
