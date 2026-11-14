(function () {
  "use strict";

  window.OC_SECTIONS = window.OC_SECTIONS || {};
  var cfg = window.__OC || {};
  var H = window.__OC_HELPERS || {};

  function progressBar(pct) {
    var v = parseInt(pct || 0, 10);
    if (isNaN(v)) v = 0;
    if (v < 0) v = 0;
    if (v > 100) v = 100;

    return (
      '<div class="progress" style="height: 14px;">' +
        '<div class="progress-bar d-flex align-items-center justify-content-center" ' +
          'role="progressbar" ' +
          'style="width: ' + v + '%;" ' +
          'aria-valuenow="' + v + '" aria-valuemin="0" aria-valuemax="100">' +
          '<span class="small fw-semibold">' + v + '%</span>' +
        "</div>" +
      "</div>"
    );
  }

  function taskCell(r) {
    var leads = r && r.lead_collections ? r.lead_collections : [];
    if (leads && leads.length) {
      var html = '<div>Lead Collection</div>';
      html += '<ul class="mb-0 ps-3">';
      leads.forEach(function (nm) {
        html += "<li>" + H.escapeHtml(nm) + "</li>";
      });
      html += "</ul>";
      return html;
    }
    return H.escapeHtml((r && r.task_name) ? r.task_name : "-");
  }

  function render(container, clientId) {
    container.innerHTML =
      '<div class="comn_table_bg p-3">' +
        '<h6 class="text-white mb-3">Ongoing Works</h6>' +

        '<div class="d-flex flex-wrap gap-2 align-items-end mb-3">' +
          '<div>' +
            '<div class="text-white-50 small mb-1">From date</div>' +
            '<input type="date" id="owFrom" class="form-control form-control-sm">' +
          "</div>" +
          '<div>' +
            '<div class="text-white-50 small mb-1">To date</div>' +
            '<input type="date" id="owTo" class="form-control form-control-sm">' +
          "</div>" +
          '<div class="d-flex gap-2">' +
            '<button class="btn btn-sm btn-primary" id="owApply">Apply</button>' +
            '<button class="btn btn-sm btn-secondary" id="owReset">Reset</button>' +
          "</div>" +
        "</div>" +

        '<div class="oc-table-wrap">' +
          '<table class="table table-dark table-striped align-middle mb-0">' +
            "<thead><tr>" +
              '<th style="width:60px;">No</th>' +
              "<th>Assigned Date</th>" +
              "<th>Start Date</th>" +
              "<th>End Date</th>" +
              "<th>Task Name</th>" +
              "<th>Executives Assigned</th>" +
              '<th style="width:90px;">Target</th>' +
              '<th style="width:140px;">Achieved Target</th>' +
              '<th style="width:240px;">Progress</th>' +
            "</tr></thead>" +
            '<tbody id="owBody"></tbody>' +
          "</table>" +
        "</div>" +
      "</div>";

    var fromEl = container.querySelector("#owFrom");
    var toEl = container.querySelector("#owTo");
    var body = container.querySelector("#owBody");

    function setEmpty(msg) {
      body.innerHTML =
        '<tr><td colspan="9" class="text-center text-white-50 py-4">' +
        H.escapeHtml(msg) +
        "</td></tr>";
    }

    function fetchRows(useDates) {
      var params = new URLSearchParams();
      params.set("client_id", clientId);

      if (useDates) {
        if (fromEl.value) params.set("from_date", fromEl.value);
        if (toEl.value) params.set("to_date", toEl.value);
      }

      body.innerHTML =
        '<tr><td colspan="9" class="text-center text-white-50 py-4">Loading...</td></tr>';

      fetch(cfg.ongoingWorksUrl + "?" + params.toString(), { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var rows = (data && data.success) ? (data.rows || []) : [];
          if (!rows.length) return setEmpty("No data");

          var html = "";
          rows.forEach(function (r, idx) {
            html += "<tr>";
            html += "<td>" + (idx + 1) + "</td>";
            html += "<td>" + H.escapeHtml(r.assigned_date || "-") + "</td>";
            html += "<td>" + H.escapeHtml(r.start_date || "-") + "</td>";
            html += "<td>" + H.escapeHtml(r.end_date || "-") + "</td>";
            html += "<td>" + taskCell(r) + "</td>";
            html += "<td>" + H.escapeHtml(r.executives_assigned || "-") + "</td>";
            html += "<td>" + H.escapeHtml(r.target) + "</td>";
            html += "<td>" + H.escapeHtml(r.achieved) + "</td>";
            html += "<td>" + progressBar(r.progress) + "</td>";
            html += "</tr>";
          });

          body.innerHTML = html;
        })
        .catch(function () {
          setEmpty("Failed to load");
        });
    }

    container.querySelector("#owApply").addEventListener("click", function () { fetchRows(true); });
    container.querySelector("#owReset").addEventListener("click", function () {
      fromEl.value = "";
      toEl.value = "";
      fetchRows(false);
    });

    fetchRows(false);
  }

  window.OC_SECTIONS.ongoing = { render: render };
})();
