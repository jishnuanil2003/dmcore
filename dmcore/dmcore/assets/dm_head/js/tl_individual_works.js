(function () {
  function startWhenReady() {
    if (!window.bootstrap) {
      setTimeout(startWhenReady, 50);
      return;
    }
    init();
  }

  function init() {
    const EP = window.TL_IND_ENDPOINTS || {};

    const tbody = document.getElementById("worksTbody");
    const searchInput = document.getElementById("searchInput");

    const taskDetailsModalEl = document.getElementById("taskDetailsModal");
    const workDetailsModalEl = document.getElementById("workDetailsModal");
    const verifyModalEl = document.getElementById("verifyModal");
    const promotionModalEl = document.getElementById("promotionModal");

    const taskDetailsErr = document.getElementById("taskDetailsErr");
    const taskDetailsBody = document.getElementById("taskDetailsBody");

    const tdClient = document.getElementById("tdClient");
    const tdTaskName = document.getElementById("tdTaskName");
    const tdAllocated = document.getElementById("tdAllocated");
    const tdAccepted = document.getElementById("tdAccepted");
    const tdDesc = document.getElementById("tdDesc");
    const tdTarget = document.getElementById("tdTarget");
    const tdAchieved = document.getElementById("tdAchieved");

    const promoWrap = document.getElementById("promoWrap");
    const promoGrid = document.getElementById("promoGrid");

    const openWorkDetailsBtn = document.getElementById("openWorkDetailsBtn");
    const workDetailsTbody = document.getElementById("workDetailsTbody");

    const vTarget = document.getElementById("vTarget");
    const vAchieved = document.getElementById("vAchieved");
    const vVerified = document.getElementById("vVerified");
    const verifySaveBtn = document.getElementById("verifySaveBtn");

    const promoErr = document.getElementById("promoErr");
    const promoBody = document.getElementById("promoBody");
    const promoList = document.getElementById("promoList");

    const taskModal = taskDetailsModalEl ? new bootstrap.Modal(taskDetailsModalEl) : null;
    const workModal = workDetailsModalEl ? new bootstrap.Modal(workDetailsModalEl) : null;
    const verifyModal = verifyModalEl ? new bootstrap.Modal(verifyModalEl, { backdrop: "static", keyboard: false }) : null;
    const promoModal = promotionModalEl ? new bootstrap.Modal(promotionModalEl) : null;

    let allRows = [];
    let activeWorkId = null;
    let verifyTaskDetailId = null;

    function esc(s) {
      return String(s || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function postForm(url, body) {
      return fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": EP.csrf || "",
          "X-Requested-With": "XMLHttpRequest"
        },
        body: body
      }).then(r => r.json().catch(() => ({})));
    }

    function progressClasses(p) {
      if (p <= 20) return "bg-danger text-white";
      if (p <= 60) return "bg-warning text-dark";
      return "bg-success text-white";
    }

    function buildActionDd(workId) {
      return `
        <div class="dropdown action_dd">
          <a class="btn btn-link text-white p-0" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            <i class="fa-solid fa-ellipsis-vertical"></i>
          </a>
          <ul class="dropdown-menu dropdown-menu-end">
            <li><a class="dropdown-item js-task-details" href="#" data-id="${workId}">Task details</a></li>
            <li><a class="dropdown-item js-work-details" href="#" data-id="${workId}">Work Details</a></li>
            <li><a class="dropdown-item text-danger js-remove-task" href="#" data-id="${workId}">Remove task</a></li>
          </ul>
        </div>
      `;
    }

    function renderTable(rows) {
      if (!tbody) return;

      if (!rows.length) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center text-white">No data found</td></tr>`;
        return;
      }

      tbody.innerHTML = rows.map((r, idx) => {
        const p = Math.max(0, Math.min(100, Number(r.progress || 0)));

        const taskCell = r.task_html ? r.task_html : esc(r.task);

        return `
          <tr>
            <td>${idx + 1}</td>
            <td>${esc(r.employee)}</td>
            <td>${esc(r.client_name)}</td>
            <td>${taskCell}</td>
            <td>${esc(r.start_date)}</td>
            <td>${esc(r.due_date)}</td>
            <td>
              <div class="progress" style="height: 18px;">
                <div class="progress-bar ${progressClasses(p)}" role="progressbar"
                  style="width: ${p}%;"
                  aria-valuenow="${p}" aria-valuemin="0" aria-valuemax="100">
                  ${p}%
                </div>
              </div>
            </td>
            <td class="text-center">${buildActionDd(r.id)}</td>
          </tr>
        `;
      }).join("");
    }

    function applySearch() {
      const q = (searchInput ? searchInput.value : "").trim().toLowerCase();
      if (!q) {
        renderTable(allRows);
        return;
      }

      const filtered = allRows.filter(r => {
        const blob = `${r.employee} ${r.client_name} ${r.task} ${r.start_date} ${r.due_date}`.toLowerCase();
        return blob.includes(q);
      });
      renderTable(filtered);
    }

    function taskDetailsUrl(id) {
      return (EP.taskDetails || "").replace("/0/", "/" + id + "/");
    }

    function workDetailsUrl(id) {
      return (EP.workDetails || "").replace("/0/", "/" + id + "/");
    }

    function promoDetailsUrl(id) {
      return (EP.promoDetails || "").replace("/0/", "/" + id + "/");
    }

    function loadList() {
      if (!EP.list) {
        allRows = [];
        renderTable([]);
        return;
      }

      fetch(EP.list, { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(r => r.json().catch(() => ({})))
        .then(data => {
          if (!data || !data.success) {
            allRows = [];
            renderTable([]);
            return;
          }
          allRows = data.rows || [];
          applySearch();
        })
        .catch(() => {
          allRows = [];
          renderTable([]);
        });
    }

    function openTaskDetails(workId) {
      activeWorkId = workId;

      if (taskDetailsErr) taskDetailsErr.classList.add("d-none");
      if (taskDetailsBody) taskDetailsBody.classList.add("d-none");

      fetch(taskDetailsUrl(workId), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(r => r.json().catch(() => ({})))
        .then(res => {
          if (!res || !res.success) {
            if (taskDetailsErr) taskDetailsErr.classList.remove("d-none");
            return;
          }

          const d = res.data || {};
          if (tdClient) tdClient.value = d.client_name || "";

          if (tdTaskName) {
            if (d.task_html) tdTaskName.innerHTML = d.task_html;
            else tdTaskName.textContent = d.task_text || d.task_name || "";
          }

          if (tdAllocated) tdAllocated.value = d.allocated_date || "";
          if (tdAccepted) tdAccepted.value = d.accepted_date || "";
          if (tdDesc) tdDesc.textContent = d.description || "";
          if (tdTarget) tdTarget.value = d.task_target != null ? String(d.task_target) : "";
          if (tdAchieved) tdAchieved.value = d.achieved_target != null ? String(d.achieved_target) : "";

          if (promoGrid) promoGrid.innerHTML = "";
          if (promoWrap) {
            if (d.promo_any && Array.isArray(d.promo) && d.promo.length) {
              promoWrap.classList.remove("d-none");
              if (promoGrid) {
                promoGrid.innerHTML = d.promo.map(p => `
                  <div class="col-md-4 col-sm-12">
                    <div class="promo_chip">
                      <div class="lbl">${esc(p.platform)}</div>
                      <div class="fw-bold">${esc(p.target)}</div>
                    </div>
                  </div>
                `).join("");
              }
            } else {
              promoWrap.classList.add("d-none");
            }
          }

          if (taskDetailsBody) taskDetailsBody.classList.remove("d-none");
        })
        .catch(() => {
          if (taskDetailsErr) taskDetailsErr.classList.remove("d-none");
        });

      if (taskModal) taskModal.show();
    }

    function openWorkDetails(workId) {
      activeWorkId = workId;

      if (workDetailsTbody) {
        workDetailsTbody.innerHTML = `<tr><td colspan="9" class="text-center text-white">Loading...</td></tr>`;
      }

      fetch(workDetailsUrl(workId), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(r => r.json().catch(() => ({})))
        .then(res => {
          const rows = (res && res.success && res.rows) ? res.rows : [];
          if (!rows.length) {
            if (workDetailsTbody) {
              workDetailsTbody.innerHTML = `<tr><td colspan="9" class="text-center text-white">No data found</td></tr>`;
            }
            return;
          }

          if (workDetailsTbody) {
            workDetailsTbody.innerHTML = rows.map(r => {
              const fileCell = r.file ? `<a class="btn btn-outline-light btn-sm" href="${esc(r.file)}" target="_blank">View</a>` : "-";
              const promoBtn = r.has_promo ? `<button type="button" class="btn btn-light btn-sm js-promo" data-id="${r.id}">View</button>` : "-";

              const verCell = (Number(r.status) === 1)
                ? `<span class="text-success fw-bold">Verified</span>`
                : `<button type="button" class="btn btn-sm text-warning js-verify"
                    data-id="${r.id}"
                    data-target="${esc(r.target)}"
                    data-achieved="${esc(r.achieved_targets)}"
                    data-verified="${esc(r.verified_targets)}">Pending</button>`;

              return `
                <tr>
                  <td>${esc(r.date)}</td>
                  <td>${esc(r.title)}</td>
                  <td>${esc(r.description)}</td>
                  <td>${fileCell}</td>
                  <td>${promoBtn}</td>
                  <td>${esc(r.target)}</td>
                  <td>${esc(r.achieved_targets)}</td>
                  <td>${esc(r.verified_targets)}</td>
                  <td>${verCell}</td>
                </tr>
              `;
            }).join("");
          }
        })
        .catch(() => {
          if (workDetailsTbody) {
            workDetailsTbody.innerHTML = `<tr><td colspan="9" class="text-center text-white">No data found</td></tr>`;
          }
        });

      if (workModal) workModal.show();
    }

    function openVerify(tdId, target, achieved, verified) {
      verifyTaskDetailId = tdId;

      if (vTarget) vTarget.value = String(target != null ? target : "");
      if (vAchieved) vAchieved.value = String(achieved != null ? achieved : "");
      if (vVerified) vVerified.value = String(verified != null ? verified : "");

      if (verifyModal) verifyModal.show();
    }

    function saveVerify(e) {
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }

      if (!verifyTaskDetailId) return;

      const val = (vVerified ? vVerified.value : "").trim();
      if (val === "" || isNaN(Number(val))) return;

      const body = `task_detail_id=${encodeURIComponent(String(verifyTaskDetailId))}&verified_targets=${encodeURIComponent(String(val))}`;

      postForm(EP.verifySave, body).then(res => {
        if (!res || !res.success) return;

        if (verifyModal) verifyModal.hide();
        if (activeWorkId) openWorkDetails(activeWorkId);
      });
    }

    function openPromotion(taskDetailId) {
      if (promoErr) promoErr.classList.add("d-none");
      if (promoBody) promoBody.classList.add("d-none");
      if (promoList) promoList.innerHTML = "";

      fetch(promoDetailsUrl(taskDetailId), { headers: { "X-Requested-With": "XMLHttpRequest" } })
        .then(r => r.json().catch(() => ({})))
        .then(res => {
          const rows = (res && res.success && res.rows) ? res.rows : [];
          if (!rows.length) {
            if (promoErr) promoErr.classList.remove("d-none");
            return;
          }

          if (promoBody) promoBody.classList.remove("d-none");
          if (promoList) {
            promoList.innerHTML = rows.map(p => `
              <div class="promo_item">
                <div class="row g-2">
                  <div class="col-md-4 col-sm-12">
                    <div class="lbl">platform:</div>
                    <div class="fw-bold">${esc(p.platform)}</div>
                  </div>
                  <div class="col-md-4 col-sm-12">
                    <div class="lbl">target:</div>
                    <div class="fw-bold">${esc(p.target)}</div>
                  </div>
                  <div class="col-md-4 col-sm-12">
                    <div class="lbl">screenshots:</div>
                    ${p.screenshots ? `<a class="btn btn-outline-light btn-sm" href="${esc(p.screenshots)}" target="_blank">View</a>` : "-"}
                  </div>
                  <div class="col-12">
                    <div class="lbl">achieved_text</div>
                    <div class="box_dark">${esc(p.achieved_text)}</div>
                  </div>
                  <div class="col-12">
                    <div class="lbl">urls</div>
                    <div class="box_dark">${esc(p.urls)}</div>
                  </div>
                  <div class="col-12">
                    <div class="lbl">remarks</div>
                    <div class="box_dark">${esc(p.remarks)}</div>
                  </div>
                </div>
              </div>
            `).join("");
          }
        })
        .catch(() => {
          if (promoErr) promoErr.classList.remove("d-none");
        });

      if (promoModal) promoModal.show();
    }

    function removeTask(workId) {
      const body = `work_id=${encodeURIComponent(String(workId))}`;
      postForm(EP.removeTask, body).then(res => {
        if (!res || !res.success) return;
        loadList();
      });
    }

    document.addEventListener("click", function (e) {
      const t = e.target.closest("a,button");
      if (!t) return;

      if (t.classList.contains("js-task-details")) {
        e.preventDefault();
        openTaskDetails(t.getAttribute("data-id"));
        return;
      }

      if (t.classList.contains("js-work-details")) {
        e.preventDefault();
        openWorkDetails(t.getAttribute("data-id"));
        return;
      }

      if (t.classList.contains("js-remove-task")) {
        e.preventDefault();
        removeTask(t.getAttribute("data-id"));
        return;
      }

      if (t.classList.contains("js-verify")) {
        e.preventDefault();
        openVerify(
          t.getAttribute("data-id"),
          t.getAttribute("data-target"),
          t.getAttribute("data-achieved"),
          t.getAttribute("data-verified")
        );
        return;
      }

      if (t.classList.contains("js-promo")) {
        e.preventDefault();
        openPromotion(t.getAttribute("data-id"));
        return;
      }
    });

    if (openWorkDetailsBtn) {
      openWorkDetailsBtn.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (activeWorkId) openWorkDetails(activeWorkId);
      });
    }

    if (verifySaveBtn) {
      verifySaveBtn.addEventListener("click", saveVerify);
    }

    if (searchInput) {
      searchInput.addEventListener("input", applySearch);
    }

    if (workDetailsModalEl) {
      workDetailsModalEl.addEventListener("hidden.bs.modal", function () {
        loadList();
      });
    }

    loadList();
  }

  startWhenReady();
})();
