(function () {
  "use strict";

  var tbody = document.getElementById("clientsTbody");
  var emptyState = document.getElementById("emptyState");

  var form = document.getElementById("filtersForm");
  var fromDateEl = document.getElementById("fromDate");
  var toDateEl = document.getElementById("toDate");
  var resetBtn = document.getElementById("resetFilterBtn");

  var DATA_URL = window.ADMIN_CLIENTS_NEW_DATA_URL;

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function statusBadge(status) {
    if (Number(status) === 0) return '<span class="badge bg-success">Active</span>';
    return '<span class="badge bg-danger">Inactive</span>';
  }

  function buildRow(row, idx) {
    var addr =
      '<td class="addr-cell">' +
      "<div>Place : " + escapeHtml(row.place) + "</div>" +
      "<div>District : " + escapeHtml(row.district) + "</div>" +
      "<div>State : " + escapeHtml(row.state) + "</div>" +
      "</td>";

    return (
      "<tr>" +
      "<td>" + (idx + 1) + "</td>" +
      "<td>" + escapeHtml(row.reg_date) + "</td>" +
      "<td>" + escapeHtml(row.name) + "</td>" +
      "<td>" + escapeHtml(row.email) + "</td>" +
      "<td>" + escapeHtml(row.phone) + "</td>" +
      addr +
      "<td>" + statusBadge(row.status) + "</td>" +
      "</tr>"
    );
  }

  function setEmpty(isEmpty) {
    if (isEmpty) emptyState.classList.remove("d-none");
    else emptyState.classList.add("d-none");
  }

  function loadData() {
    var url = new URL(DATA_URL, window.location.origin);

    if (fromDateEl.value) url.searchParams.set("from_date", fromDateEl.value);
    if (toDateEl.value) url.searchParams.set("to_date", toDateEl.value);

    fetch(url.toString(), { method: "GET" })
      .then(function (res) { return res.json(); })
      .then(function (payload) {
        if (!payload || payload.success !== true) {
          tbody.innerHTML = "";
          setEmpty(true);
          return;
        }

        var data = payload.data || [];
        if (!data.length) {
          tbody.innerHTML = "";
          setEmpty(true);
          return;
        }

        var html = "";
        for (var i = 0; i < data.length; i++) {
          html += buildRow(data[i], i);
        }
        tbody.innerHTML = html;
        setEmpty(false);
      })
      .catch(function () {
        tbody.innerHTML = "";
        setEmpty(true);
      });
  }

  // on load
  document.addEventListener("DOMContentLoaded", function () {
    loadData();
  });

  // Apply (no reload)
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    loadData();
  });

  // Reset (clear inputs + reload data)
  resetBtn.addEventListener("click", function () {
    fromDateEl.value = "";
    toDateEl.value = "";
    loadData();
  });
})();
