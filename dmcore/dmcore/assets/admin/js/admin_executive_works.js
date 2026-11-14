(function () {
  "use strict";

  var currentSection = "ongoing";

  var executiveSelect = document.getElementById("executiveSelect");
  var fromDateInput = document.getElementById("fromDate");
  var toDateInput = document.getElementById("toDate");
  var applyFilterBtn = document.getElementById("applyFilterBtn");
  var resetFilterBtn = document.getElementById("resetFilterBtn");

  var panelTitle = document.getElementById("panelTitle");
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
    return !!(executiveSelect && executiveSelect.value);
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
    panelTitle.textContent = (section === "ongoing") ? "Ongoing Works" : "Completed Works";
  }

  function renderProgressBar(progress) {
    var p = Number(progress || 0);
    if (isNaN(p)) p = 0;
    if (p < 0) p = 0;
    if (p > 100) p = 100;

    return (
      '<div class="progress">' +
        '<div class="progress-bar" role="progressbar" style="width:' + p + '%" aria-valuenow="' + p + '" aria-valuemin="0" aria-valuemax="100">' +
          p + "%" +
        "</div>" +
      "</div>"
    );
  }

  function renderEmpty(msg) {
    worksTbody.innerHTML =
      '<tr><td colspan="7" class="py-4 text-white-50">' + escapeHtml(msg) + "</td></tr>";
  }

  function getParams() {
    return {
      executive_id: executiveSelect ? executiveSelect.value : "",
      mode: currentSection,
      from: fromDateInput ? fromDateInput.value : "",
      to: toDateInput ? toDateInput.value : ""
    };
  }

  function loadSection(section) {
    if (!hasSelection()) return;

    setActiveCard(section);

    var urls = window.ADMIN_EXEC_WORKS_URLS || {};
    if (!urls.list) {
      renderEmpty("Missing list endpoint.");
      return;
    }

    var params = getParams();
    renderEmpty("Loading...");

    fetch(urls.list + buildQuery(params), {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || data.success !== true) {
          renderEmpty((data && data.message) ? data.message : "Failed to load");
          return;
        }

        var rows = data.rows || [];
        if (!rows.length) {
          renderEmpty("No records found.");
          return;
        }

        var statusClass = (section === "ongoing") ? "text-warning" : "text-success";
        var statusText = (section === "ongoing") ? "Ongoing" : "Completed";

        worksTbody.innerHTML = rows.map(function (row, idx) {
          var btn = "-";
          if (row.task_assign_id) {
            btn =
              '<button type="button" class="btn btn-outline-primary btn-sm js-daily" ' +
              'data-task-assign-id="' + escapeHtml(row.task_assign_id) + '" data-section="' + escapeHtml(section) + '">' +
              "View Details</button>";
          }

          return (
            "<tr>" +
              "<td>" + (idx + 1) + "</td>" +
              "<td>" + escapeHtml(row.start_date || "-") + "</td>" +
              "<td>" + escapeHtml(row.end_date || "-") + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(row.task_name || "-") + "</td>" +
              "<td>" + renderProgressBar(row.progress) + "</td>" +
              "<td>" + btn + "</td>" +
              "<td><span class=\"" + statusClass + "\">" + statusText + "</span></td>" +
            "</tr>"
          );
        }).join("");
      })
      .catch(function () {
        renderEmpty("Something gone wrong while loading data.");
      });
  }

  function loadDailyDetails(taskAssignId, section) {
    var urls = window.ADMIN_EXEC_WORKS_URLS || {};
    if (!urls.daily) {
      dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">Missing daily endpoint.</td></tr>';
      return;
    }

    dailyWorksTitle.textContent = (section === "ongoing") ? "Daily Works (Ongoing)" : "Daily Works (Completed)";
    dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">Loading...</td></tr>';

    fetch(urls.daily + buildQuery({ task_assign_id: taskAssignId, mode: section }), {
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

        var items = data.items || [];
        if (!items.length) {
          dailyWorksTbody.innerHTML = '<tr><td colspan="7" class="py-4 text-white-50">No daily works found.</td></tr>';
          return;
        }

        dailyWorksTbody.innerHTML = items.map(function (it, idx) {
          return (
            "<tr>" +
              "<td>" + (idx + 1) + "</td>" +
              "<td>" + escapeHtml(it.date || "-") + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(it.title || "-") + "</td>" +
              "<td class=\"text-start\">" + escapeHtml(it.description || "-") + "</td>" +
              "<td>" + escapeHtml(it.achieved_target) + "</td>" +
              "<td>" + escapeHtml(it.verified_target) + "</td>" +
              "<td><span class=\"" + ((it.status || "").toLowerCase() === "verified" ? "text-success" : "text-warning") + "\">" + escapeHtml(it.status || "-") +"</span></td>"  +
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
      loadSection(section);
      return;
    }

    var btn = e.target.closest(".js-daily");
    if (btn) {
      var taskAssignId = btn.getAttribute("data-task-assign-id");
      var section = btn.getAttribute("data-section") || currentSection;

      loadDailyDetails(taskAssignId, section);

      if (window.bootstrap && dailyWorksModalEl) {
        window.bootstrap.Modal.getOrCreateInstance(dailyWorksModalEl).show();
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

  if (executiveSelect) {
    executiveSelect.value = "";
    executiveSelect.addEventListener("change", function () {
      if (!hasSelection()) {
        hideContent();
        return;
      }
      showContent();
      setActiveCard(currentSection);
      loadSection(currentSection);
    });
  }

  setActiveCard("ongoing");
  hideContent();
})();
