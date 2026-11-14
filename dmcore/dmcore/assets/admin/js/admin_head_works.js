(function () {
  "use strict";

  var headSelect = document.getElementById("headSelect");
  var contentArea = document.getElementById("contentArea");
  var tableTitle = document.getElementById("tableTitle");
  var tableThead = document.getElementById("tableThead");
  var tableTbody = document.getElementById("tableTbody");
  var emptyState = document.getElementById("emptyState");

  var fromDate = document.getElementById("fromDate");
  var toDate = document.getElementById("toDate");
  var applyFilterBtn = document.getElementById("applyFilterBtn");
  var resetFilterBtn = document.getElementById("resetFilterBtn");

  var cards = Array.prototype.slice.call(document.querySelectorAll(".work-card.clickable"));

  var currentView = "clients";

  function qs(obj) {
    var parts = [];
    Object.keys(obj).forEach(function (k) {
      if (obj[k] === null || obj[k] === undefined || obj[k] === "") return;
      parts.push(encodeURIComponent(k) + "=" + encodeURIComponent(String(obj[k])));
    });
    return parts.length ? "?" + parts.join("&") : "";
  }

  function fetchJson(url) {
    return fetch(url, {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" }
    }).then(function (res) {
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res.json();
    });
  }

  function setActiveCard(view) {
    cards.forEach(function (c) {
      if (c.getAttribute("data-view") === view) c.classList.add("active");
      else c.classList.remove("active");
    });
  }

  function showEmpty(show) {
    if (show) emptyState.classList.remove("d-none");
    else emptyState.classList.add("d-none");
  }

  function clearTable() {
    tableThead.innerHTML = "";
    tableTbody.innerHTML = "";
    showEmpty(false);
  }

  function renderThead(cols, classes) {
    var tr = document.createElement("tr");
    cols.forEach(function (col, i) {
      var th = document.createElement("th");
      th.textContent = col;
      if (classes && classes[i]) th.className = classes[i];
      tr.appendChild(th);
    });
    tableThead.innerHTML = "";
    tableThead.appendChild(tr);
  }

  function renderRows(rows, renderer) {
    tableTbody.innerHTML = "";
    if (!rows || !rows.length) {
      showEmpty(true);
      return;
    }
    showEmpty(false);

    rows.forEach(function (row, idx) {
      var tr = renderer(row, idx + 1);
      tableTbody.appendChild(tr);
    });
  }

  function td(text) {
    var el = document.createElement("td");
    el.textContent = text;
    return el;
  }

  function tdHtml(node) {
    var el = document.createElement("td");
    el.appendChild(node);
    return el;
  }

  function statusSpan(statusText) {
    var span = document.createElement("span");
    if ((statusText || "").toLowerCase() === "completed") span.className = "text-success";
    else span.className = "text-warning";
    span.textContent = statusText || "-";
    return span;
  }

  function progressBarNode(val) {
    var n = Number(val);
    if (isNaN(n)) n = 0;
    if (n < 0) n = 0;
    if (n > 100) n = 100;

    var wrap = document.createElement("div");
    wrap.className = "progress";
    wrap.style.height = "10px";

    var bar = document.createElement("div");
    bar.className = "progress-bar";
    bar.setAttribute("role", "progressbar");
    bar.style.width = n + "%";
    bar.setAttribute("aria-valuenow", String(n));
    bar.setAttribute("aria-valuemin", "0");
    bar.setAttribute("aria-valuemax", "100");

    wrap.appendChild(bar);
    return wrap;
  }

  function addressBlock(place, district, state) {
    var d = document.createElement("div");

    var l1 = document.createElement("div");
    l1.textContent = "Place : " + (place || "-");
    d.appendChild(l1);

    var l2 = document.createElement("div");
    l2.textContent = "District : " + (district || "-");
    d.appendChild(l2);

    var l3 = document.createElement("div");
    l3.textContent = "State : " + (state || "-");
    d.appendChild(l3);

    return d;
  }

  function taskNameBlock(taskName, categoryName) {
    var block = document.createElement("div");
    block.className = "task-name-block";

    var l1 = document.createElement("div");
    l1.className = "line1";
    l1.textContent = taskName || "-";
    block.appendChild(l1);

    if (categoryName) {
      var l2 = document.createElement("div");
      l2.className = "line2";
      l2.textContent = "• " + categoryName;
      block.appendChild(l2);
    }

    return block;
  }

  function getSelectedHeadId() {
    return headSelect ? headSelect.value : "";
  }

  function getFilterPayload() {
    return {
      from: fromDate ? fromDate.value : "",
      to: toDate ? toDate.value : ""
    };
  }

  function hideContent() {
    if (contentArea) contentArea.classList.add("d-none");
    clearTable();
  }

  function showContent() {
    if (contentArea) contentArea.classList.remove("d-none");
  }

  function loadView(view) {
    currentView = view;
    setActiveCard(view);
    clearTable();

    var headId = getSelectedHeadId();
    if (!headId) {
      hideContent();
      return;
    }

    showContent();

    var filters = getFilterPayload();

    if (view === "clients") {
      tableTitle.textContent = "Client Details";
      renderThead(
        ["No", "Registered Date", "Name", "Email", "Phone", "Address"],
        ["", "table_en_lsm", "table_en_lsm", "table_en_md", "table_en_lsm", "table_en_md"]
      );

      var payloadClients = {
        head_id: headId,
        from: filters.from,
        to: filters.to
      };

      fetchJson("/ad/works/head/api/clients/" + qs(payloadClients))
        .then(function (data) {
          var rows = (data && data.rows) ? data.rows : [];
          renderRows(rows, function (r, no) {
            var tr = document.createElement("tr");
            tr.appendChild(td(String(no)));
            tr.appendChild(td(r.registered_date || "-"));
            tr.appendChild(td(r.name || "-"));
            tr.appendChild(td(r.email || "-"));
            tr.appendChild(td(r.phone || "-"));
            tr.appendChild(tdHtml(addressBlock(r.place, r.district, r.state)));
            return tr;
          });
        })
        .catch(function () {
          showEmpty(true);
        });

      return;
    }

    if (view === "client-works") {
      tableTitle.textContent = "Client Works";
      renderThead(
        ["No", "Registered Date", "Client Name", "Task Name", "Description", "Progress", "Work Status"],
        ["", "table_en_lsm", "table_en_lsm", "table_en_md", "table_en_md", "table_en_lsm", "table_en_lsm"]
      );

      var payloadClientWorks = {
        head_id: headId,
        from: filters.from,
        to: filters.to
      };

      fetchJson("/ad/works/head/api/client-works/" + qs(payloadClientWorks))
        .then(function (data) {
          var rows = (data && data.rows) ? data.rows : [];
          renderRows(rows, function (r, no) {
            var tr = document.createElement("tr");
            tr.appendChild(td(String(no)));
            tr.appendChild(td(r.registered_date || "-"));
            tr.appendChild(td(r.client_name || "-"));
            tr.appendChild(tdHtml(taskNameBlock(r.task_name || "-", r.category_name || "")));
            tr.appendChild(td(r.description || "-"));
            tr.appendChild(tdHtml(progressBarNode(r.progress)));
            tr.appendChild(tdHtml(statusSpan(r.work_status)));
            return tr;
          });
        })
        .catch(function () {
          showEmpty(true);
        });

      return;
    }

    if (view === "assigned") {
      tableTitle.textContent = "Works Assigned";
      renderThead(
        ["No", "Created Date", "End Date", "Client", "Assigned Team Leads", "Progress", "Work Status"],
        ["", "table_en_lsm", "table_en_lsm", "table_en_lsm", "table_en_md", "table_en_lsm", "table_en_lsm"]
      );

      var payloadAssigned = {
        head_id: headId,
        from: filters.from,
        to: filters.to
      };

      fetchJson("/ad/works/head/api/assigned/" + qs(payloadAssigned))
        .then(function (data) {
          var rows = (data && data.rows) ? data.rows : [];
          renderRows(rows, function (r, no) {
            var tr = document.createElement("tr");
            tr.appendChild(td(String(no)));
            tr.appendChild(td(r.created_date || "-"));
            tr.appendChild(td(r.end_date || "-"));
            tr.appendChild(td(r.client || "-"));
            tr.appendChild(td(r.assigned_team_leads || "-"));
            tr.appendChild(tdHtml(progressBarNode(r.progress)));
            tr.appendChild(tdHtml(statusSpan(r.work_status)));
            return tr;
          });
        })
        .catch(function () {
          showEmpty(true);
        });

      return;
    }
  }

  function loadHeads() {
    fetchJson("/ad/works/head/api/heads/")
      .then(function (data) {
        var heads = (data && data.heads) ? data.heads : [];
        headSelect.innerHTML = '<option value="">- Select -</option>';

        heads.forEach(function (h) {
          var opt = document.createElement("option");
          opt.value = String(h.id);
          opt.textContent = h.name || "-";
          headSelect.appendChild(opt);
        });

        headSelect.value = "";
        hideContent();
        setActiveCard(currentView);
      })
      .catch(function () {
        headSelect.innerHTML = '<option value="">- Select -</option>';
        headSelect.value = "";
        hideContent();
      });
  }

  function bindEvents() {
    if (headSelect) {
      headSelect.addEventListener("change", function () {
        if (!headSelect.value) {
          hideContent();
          return;
        }
        loadView(currentView);
      });
    }

    cards.forEach(function (c) {
      c.addEventListener("click", function () {
        if (!getSelectedHeadId()) return;
        var view = c.getAttribute("data-view");
        loadView(view);
      });
    });

    if (applyFilterBtn) {
      applyFilterBtn.addEventListener("click", function () {
        loadView(currentView);
      });
    }

    if (resetFilterBtn) {
      resetFilterBtn.addEventListener("click", function () {
        if (fromDate) fromDate.value = "";
        if (toDate) toDate.value = "";
        loadView(currentView);
      });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindEvents();
    setActiveCard(currentView);
    hideContent();
    loadHeads();
  });
})();
