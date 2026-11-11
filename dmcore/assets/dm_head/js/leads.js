document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("searchInput");
  input.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    document.querySelectorAll("#leadTable tbody tr").forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(searchTerm) ? "" : "none";
    });
  });
});


// search
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearch");
  const rows = document.querySelectorAll("#leadTable tbody tr");

  function filterRows() {
    const searchTerm = input.value.toLowerCase();
    rows.forEach(row => {
      const rowText = row.textContent.toLowerCase();
      row.style.display = rowText.includes(searchTerm) ? "" : "none";
    });
  }

  input.addEventListener("input", filterRows);
  clearBtn.addEventListener("click", function () {
    input.value = "";
    filterRows();
  });
});
