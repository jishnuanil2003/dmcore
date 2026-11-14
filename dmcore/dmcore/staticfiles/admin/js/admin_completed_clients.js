(function () {
  "use strict";

  var dataUrl = window.__completedClientsDataUrl;

  var clientSelect = document.getElementById("clientSelect");
  var fromDateInput = document.getElementById("fromDate");
  var toDateInput = document.getElementById("toDate");
  var applyFilterBtn = document.getElementById("applyFilterBtn");
  var resetFilterBtn = document.getElementById("resetFilterBtn");
  var clientsTbody = document.getElementById("clientsTbody");

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function renderDropdown(clients) {
    var html = '<option value="" selected disabled>Select Client</option>';

    for (var i = 0; i < clients.length; i++) {
      var c = clients[i];
      html +=
        '<option value="' +
        escapeHtml(c.id) +
        '">' +
        escapeHtml(c.client_name || "-") +
        "</option>";
    }

    clientSelect.innerHTML = html;
  }

  function renderEmptyMessage(message) {
    clientsTbody.innerHTML =
      '<tr><td colspan="7" class="text-center text-white-50 py-4">' +
      escapeHtml(message) +
      "</td></tr>";
  }

  function renderTable(rows) {
    if (!rows || rows.length === 0) {
      renderEmptyMessage("No completed data found for this client.");
      return;
    }

    var html = "";
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];

      var addressHtml =
        '<div><span class="text-white-50">Place :</span> ' +
        escapeHtml(r.place || "-") +
        "</div>" +
        '<div><span class="text-white-50">District :</span> ' +
        escapeHtml(r.district || "-") +
        "</div>" +
        '<div><span class="text-white-50">State :</span> ' +
        escapeHtml(r.state || "-") +
        "</div>";

      html += "<tr>";
      html += "<td>" + (i + 1) + "</td>";
      html += "<td>" + escapeHtml(r.registered_date) + "</td>";
      html += "<td>" + escapeHtml(r.client_name) + "</td>";
      html += "<td>" + escapeHtml(r.email) + "</td>";
      html += "<td>" + escapeHtml(r.phone) + "</td>";
      html += "<td>" + addressHtml + "</td>";
      html +=
        '<td class="text-success fw-semibold">' +
        escapeHtml(r.status || "Completed") +
        "</td>";
      html += "</tr>";
    }

    clientsTbody.innerHTML = html;
  }

  function buildQueryForSelectedClient(includeDates) {
    var clientId = clientSelect.value;

    if (!clientId) return "";

    var params = new URLSearchParams();
    params.set("client_id", clientId);

    if (includeDates) {
      var fromDate = fromDateInput.value;
      var toDate = toDateInput.value;

      if (fromDate) params.set("from_date", fromDate);
      if (toDate) params.set("to_date", toDate);
    }

    return params.toString();
  }

  function fetchData(qs, refreshDropdown) {
    if (!qs) {
      renderEmptyMessage("Select a client to view completed details.");
      return;
    }

    clientsTbody.innerHTML =
      '<tr><td colspan="7" class="text-center text-white-50 py-4">Loading...</td></tr>';

    var url = dataUrl + "?" + qs;

    fetch(url, { method: "GET" })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data || data.success !== true) {
          renderEmptyMessage("Failed to load.");
          return;
        }

        if (refreshDropdown) {
          renderDropdown(data.clients || []);
        }

        renderTable(data.rows || []);
      })
      .catch(function () {
        renderEmptyMessage("Network error.");
      });
  }

  clientSelect.addEventListener("change", function () {
    fetchData(buildQueryForSelectedClient(false), false);
  });

  applyFilterBtn.addEventListener("click", function () {
    fetchData(buildQueryForSelectedClient(true), false);
  });

  resetFilterBtn.addEventListener("click", function () {
    fromDateInput.value = "";
    toDateInput.value = "";

    fetchData(buildQueryForSelectedClient(false), false);
  });

  renderEmptyMessage("Select a client to view completed details.");
  fetch(dataUrl, { method: "GET" })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      if (!data || data.success !== true) {
        return;
      }
      renderDropdown(data.clients || []);
    })
    .catch(function () {
    });
})();
