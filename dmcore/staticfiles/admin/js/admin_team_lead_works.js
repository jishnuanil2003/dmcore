(function () {
  "use strict";

  var currentSection = "assigned";

  var teamLeadSelect = document.getElementById("teamLeadSelect");
  var fromDateInput = document.getElementById("fromDate");
  var toDateInput = document.getElementById("toDate");
  var applyFilterBtn = document.getElementById("applyFilterBtn");
  var resetFilterBtn = document.getElementById("resetFilterBtn");

  var panelTitle = document.getElementById("panelTitle");
  var worksThead = document.getElementById("worksThead");
  var worksTbody = document.getElementById("worksTbody");

  var dailyWorksModalEl = document.getElementById("dailyWorksModal");
  var dailyWorksTbody = document.getElementById("dailyWorksTbody");
  var dailyWorksTitle = document.getElementById("dailyWorksTitle");

  var contentRow = document.querySelector(".row.g-3");

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function getParams() {
    return {
      team_lead_id: teamLeadSelect ? teamLeadSelect.value : "",
      from_date: fromDateInput ? fromDateInput.value : "",
      to_date: toDateInput ? toDateInput.value : ""
    };
  }

  function buildQuery(params) {
    var esc = encodeURIComponent;
    var parts = [];
    Object.keys(params).forEach(function (k) {
      if (params[k] !== null && params[k] !== undefined && params[k] !== "") {
        parts.push(esc(k) + "=" + esc(params[k]));
      }
    });
    return parts.length ? ("?" + parts.join("&")) : "";
  }

  function hasSelection() {
    return !!(teamLeadSelect && teamLeadSelect.value);
  }

  function hideContent() {
    if (contentRow) contentRow.classList.add("d-none");
  }

  function showContent() {
    if (contentRow) contentRow.classList.remove("d-none");
  }

  function setActiveCard(section) {
    currentSection = section;
    var cards = document.querySelectorAll(".work-card");
    cards.forEach(function (c) {
      c.classList.toggle("active", c.getAttribute("data-section") === section);
    });

    if (section === "assigned") panelTitle.textContent = "Works Assigned";
    if (section === "ongoing") panelTitle.textContent = "Ongoing Works";
    if (section === "completed") panelTitle.textContent = "Completed Works";
  }

  function renderProgressBar(progress) {
    var p = Number(progress || 0);
    if (isNaN(p)) p = 0;
    if (p < 0) p = 0;
    if (p > 100) p = 100;

    return (
      '<div class="progress">' +
        '<div class="progress-bar" role="progressbar" style="width: ' + p + '%;" aria-valuenow="' + p + '" aria-valuemin="0" aria-valuemax="100">' +
          p + "%" +
        "</div>" +
      "</div>"
    );
  }

  function setTheadForSection(section) {
    if (section === "assigned") {
      worksThead.innerHTML =
        "<tr>" +
          "<th>No</th>" +
          '<th class="table_en_md">Start Date</th>' +
          '<th class="table_en_md">End Date</th>' +
          '<th class="table_en_xl">Executives Assigned</th>' +
          '<th class="table_en_xl">Task</th>' +
          '<th class="table_en_sm">Target</th>' +
          '<th class="table_en_sm">Achieved target</th>' +
          '<th class="table_en_md">Progress</th>' +
        "</tr>";
      return;
    }

    worksThead.innerHTML =
      "<tr>" +
        "<th>No</th>" +
        '<th class="table_en_md">Start Date</th>' +
        '<th class="table_en_md">End Date</th>' +
        '<th class="table_en_xl">Task Name</th>' +
        '<th class="table_en_md">Progress</th>' +
        '<th class="table_en_md">Daily works</th>' +
        '<th class="table_en_sm">Status</th>' +
      "</tr>";
  }

  function renderEmpty(msg, colspan) {
    worksTbody.innerHTML =
      '<tr><td colspan="' + colspan + '" class="py-4 text-white-50">' + escapeHtml(msg) + "</td></tr>";
  }

  function loadSection(section) {
    if (!hasSelection()) return;

    setTheadForSection(section);

    var urls = window.ADMIN_TL_WORKS_URLS || {};
    var endpoint = urls[section];

    if (!endpoint) {
      renderEmpty("Missing endpoint for " + section, 8);
      return;
    }

    var params = getParams();

    renderEmpty("Loading...", section === "assigned" ? 8 : 7);

    fetch(endpoint + buildQuery(params), {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || data.success !== true) {
          renderEmpty((data && data.message) ? data.message : "Failed to load", section === "assigned" ? 8 : 7);
          return;
        }

        var rows = data.rows || [];
        if (!rows.length) {
          renderEmpty("No records found.", section === "assigned" ? 8 : 7);
          return;
        }

        if (section === "assigned") {
          worksTbody.innerHTML = rows.map(function (row) {
            var leadCatsHtml = "";
            if (row.lead_categories && row.lead_categories.length) {
              leadCatsHtml =
                '<div class="text-start mt-2">' +
                  '<div class="small text-white-50">Lead Collection</div>' +
                  '<ul class="mb-0 ps-3">' +
                    row.lead_categories.map(function (c) {
                      return "<li class=\"small\">" + escapeHtml(c) + "</li>";
                    }).join("") +
                  "</ul>" +
                "</div>";
            }

            return (
              "<tr>" +
                "<td>" + escapeHtml(row.no) + "</td>" +
                "<td>" + escapeHtml(row.start_date) + "</td>" +
                "<td>" + escapeHtml(row.end_date) + "</td>" +
                "<td class=\"text-start\">" + escapeHtml(row.executives_assigned) + "</td>" +
                "<td class=\"text-start\">" + escapeHtml(row.task) + leadCatsHtml + "</td>" +
                "<td>" + escapeHtml(row.target) + "</td>" +
                "<td>" + escapeHtml(row.achieved_target) + "</td>" +
                "<td>" + renderProgressBar(row.progress) + "</td>" +
              "</tr>"
            );
          }).join("");
          return;
        }

        var statusClass = (section === "ongoing") ? "text-warning" : "text-success";
        var statusText = (section === "ongoing") ? "Ongoing" : "Completed";

        worksTbody.innerHTML = rows.map(function (row) {
          return (
            "<tr>" +
              "<td>" + escapeHtml(row.no) + "</td>" +
              "<td>" + escapeHtml(row.start_date) + "</td>" +
              "<td>" + escapeHtml(row.end_date) + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(row.task_name) + "</td>" +
              "<td>" + renderProgressBar(row.progress) + "</td>" +
              "<td>" +
                "<button type=\"button\" class=\"btn btn-outline-primary btn-sm js-daily\" data-work-id=\"" + escapeHtml(row.id) + "\" data-section=\"" + escapeHtml(section) + "\">View Details</button>" +
              "</td>" +
              "<td><span class=\"" + statusClass + "\">" + statusText + "</span></td>" +
            "</tr>"
          );
        }).join("");
      })
      .catch(function () {
        renderEmpty("Something gone wrong while loading data.", section === "assigned" ? 8 : 7);
      });
  }

  function loadDailyDetails(workAssignId, section) {
    var urls = window.ADMIN_TL_WORKS_URLS || {};
    var endpoint = urls.dailyDetails;

    dailyWorksTitle.textContent = (section === "ongoing") ? "Daily Works (Ongoing)" : "Daily Works (Completed)";
    dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">Loading...</td></tr>';

    fetch(endpoint + buildQuery({ work_assign_id: workAssignId }), {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || data.success !== true) {
          dailyWorksTbody.innerHTML =
            '<tr><td colspan="7" class="py-4 text-white-50">' + escapeHtml(data && data.message ? data.message : "Failed") + "</td></tr>";
          return;
        }

        var rows = data.rows || [];
        if (!rows.length) {
          dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">No daily works found.</td></tr>';
          return;
        }

        dailyWorksTbody.innerHTML = rows.map(function (row) {
          var statusVal = Number(row.status);
          var statusText = (statusVal === 1) ? "Verified" : "Pending";
          var statusClass = (statusVal === 1) ? "text-success" : "text-warning";

          return (
            "<tr>" +
              "<td>" + escapeHtml(row.no) + "</td>" +
              "<td>" + escapeHtml(row.date) + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(row.title) + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(row.description) + "</td>" +
              "<td>" + escapeHtml(row.achieved_target) + "</td>" +
              "<td>" + escapeHtml(row.verified_target) + "</td>" +
              "<td><span class=\"" + statusClass + "\">" + statusText + "</span></td>" +
            "</tr>"
          );
        }).join("");
      })
      .catch(function () {
        dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">Failed to load daily works.</td></tr>';
      });
  }

  document.addEventListener("click", function (e) {
    var card = e.target.closest(".work-card");
    if (card) {
      if (!hasSelection()) return;
      var section = card.getAttribute("data-section");
      setActiveCard(section);
      loadSection(section);
      return;
    }

    var btn = e.target.closest(".js-daily");
    if (btn) {
      var workId = btn.getAttribute("data-work-id");
      var section = btn.getAttribute("data-section");

      loadDailyDetails(workId, section);

      if (window.bootstrap && dailyWorksModalEl) {
        var modal = window.bootstrap.Modal.getOrCreateInstance(dailyWorksModalEl);
        modal.show();
      }
    }
  });

  if (applyFilterBtn) {
    applyFilterBtn.addEventListener("click", function () {
      loadSection(currentSection);
    });
  }

  if (resetFilterBtn) {
    resetFilterBtn.addEventListener("click", function () {
      if (fromDateInput) fromDateInput.value = "";
      if (toDateInput) toDateInput.value = "";
      loadSection(currentSection);
    });
  }

  if (teamLeadSelect) {
    teamLeadSelect.addEventListener("change", function () {
      if (!hasSelection()) {
        hideContent();
        return;
      }
      showContent();
      setActiveCard(currentSection);
      loadSection(currentSection);
    });
  }

  setActiveCard("assigned");
  if (teamLeadSelect) teamLeadSelect.value = "";
  hideContent();
})();
