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
        '</div>' +
      '</div>'
    );
  }
  

  function statusPill(st) {
    // 0 ongoing, 1 submitted
    if (parseInt(st, 10) === 1) {
      return '<span class="oc-status oc-status-success">Submitted</span>';
    }
    return '<span class="oc-status oc-status-warning">Ongoing</span>';
  }

  function render(container, clientId) {
    container.innerHTML =
      '<div class="comn_table_bg p-3">' +
        '<h6 class="text-white mb-3">Registered Works</h6>' +

        '<div class="d-flex flex-wrap gap-2 align-items-end mb-3">' +
          '<div>' +
            '<div class="text-white-50 small mb-1">From date</div>' +
            '<input type="date" id="rwFrom" class="form-control form-control-sm">' +
          '</div>' +
          '<div>' +
            '<div class="text-white-50 small mb-1">To date</div>' +
            '<input type="date" id="rwTo" class="form-control form-control-sm">' +
          '</div>' +
          '<div class="d-flex gap-2">' +
            '<button class="btn btn-sm btn-primary" id="rwApply">Apply</button>' +
            '<button class="btn btn-sm btn-secondary" id="rwReset">Reset</button>' +
          '</div>' +
        '</div>' +

        '<div class="oc-table-wrap">' +
          '<table class="table table-dark table-striped align-middle mb-0">' +
            '<thead><tr>' +
              '<th style="width:60px;">No</th>' +
              '<th>Create Date</th>' +
              '<th>End Date</th>' +
              '<th>Assigned Team Leads</th>' +
              '<th style="width:240px;">Progress</th>' +
              '<th style="width:140px;">Work Status</th>' +
            '</tr></thead>' +
            '<tbody id="rwBody"></tbody>' +
          '</table>' +
        '</div>' +
      '</div>';

    var fromEl = container.querySelector("#rwFrom");
    var toEl = container.querySelector("#rwTo");
    var body = container.querySelector("#rwBody");

    function setEmpty(msg) {
      body.innerHTML = '<tr><td colspan="6" class="text-center text-white-50 py-4">' + H.escapeHtml(msg) + '</td></tr>';
    }

    function fetchRows(useDates) {
      var params = new URLSearchParams();
      params.set("client_id", clientId);
      if (useDates) {
        if (fromEl.value) params.set("from_date", fromEl.value);
        if (toEl.value) params.set("to_date", toEl.value);
      }

      body.innerHTML = '<tr><td colspan="6" class="text-center text-white-50 py-4">Loading...</td></tr>';

      fetch(cfg.registeredWorksUrl + "?" + params.toString(), { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
          var rows = (data && data.success) ? (data.rows || []) : [];
          if (!rows.length) return setEmpty("No data");

          var html = "";
          rows.forEach(function (r, idx) {
            html += "<tr>";
            html += "<td>" + (idx + 1) + "</td>";
            html += "<td>" + H.escapeHtml(r.create_date || "-") + "</td>";
            html += "<td>" + H.escapeHtml(r.end_date || "-") + "</td>";
            html += "<td>" + H.escapeHtml(r.team_leads || "Not Assigned") + "</td>";
            html += "<td>" + progressBar(r.progress) + "</td>";
            html += "<td>" + statusPill(r.work_status) + "</td>";
            html += "</tr>";
          });
          body.innerHTML = html;
        })
        .catch(function () {
          setEmpty("Failed to load");
        });
    }

    container.querySelector("#rwApply").addEventListener("click", function () { fetchRows(true); });
    container.querySelector("#rwReset").addEventListener("click", function () {
      fromEl.value = "";
      toEl.value = "";
      fetchRows(false);
    });

    fetchRows(false);
  }

  window.OC_SECTIONS.registered = { render: render };
})();
