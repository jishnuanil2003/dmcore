document.addEventListener("DOMContentLoaded", function () {
  const employeeSelect = document.getElementById("employeeSelect");
  const searchBtn = document.getElementById("searchBtn");
  const inProgressContainer = document.getElementById("inProgressContainer");
  const completedContainer = document.getElementById("completedContainer");

  if (!employeeSelect || !searchBtn || !inProgressContainer || !completedContainer) {
    console.warn("Works page elements not found. Check HTML ids.");
    return;
  }

  function getCSRFToken() {
    const name = "csrftoken";
    const cookies = document.cookie ? document.cookie.split(";") : [];
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        return decodeURIComponent(cookie.substring(name.length + 1));
      }
    }
    return "";
  }

  function clearContainer(container) {
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
  }

  function createWorkCard(item) {
    const card = document.createElement("div");
    card.className = "work-card";

    if (item.status === "completed") {
      card.classList.add("border-success");
    } else {
      card.classList.add("in_progress_border");
    }

    card.dataset.workId = item.work_id;
    card.dataset.sources = JSON.stringify(item.sources || []);

    const iconClass = item.status === "completed" ? "text-success" : "text-primary";

    card.innerHTML = `
      <div class="d-flex align-items-center gap-2">
        <i class="fa fa-file ${iconClass}"></i>
        <div class="ml-1">
          <h5 class="m-0">${item.client_name || "Unnamed client"}</h5>
          <p class="text-white small mb-0">${item.description || ""}</p>
        </div>
      </div>
    `;

    card.addEventListener("click", function () {
      const template = window.DM_WORK_DETAIL_URL_TEMPLATE;
      if (!template) {
        console.error("Detail URL template missing");
        return;
      }

      const url = template.replace("0/", item.work_id + "/");
      window.location.href = url;
    });

    return card;
  }

  function renderWorks(data) {
    clearContainer(inProgressContainer);
    clearContainer(completedContainer);

    if (!data.success) {
      console.error("Failed to load works", data.error);
      return;
    }

    if ((!data.in_progress || data.in_progress.length === 0) &&
        (!data.completed || data.completed.length === 0)) {
      const emptyMsg = document.createElement("p");
      emptyMsg.className = "text-white small";
      emptyMsg.textContent = "No works found.";
      inProgressContainer.appendChild(emptyMsg.cloneNode(true));
      completedContainer.appendChild(emptyMsg);
      return;
    }

    (data.in_progress || []).forEach(function (item) {
      inProgressContainer.appendChild(createWorkCard(item));
    });

    (data.completed || []).forEach(function (item) {
      completedContainer.appendChild(createWorkCard(item));
    });
  }

  // ---- NEW: fetch all employees on page load ----

  function fetchAllEmployees() {
    const allIds = Array.from(employeeSelect.options)
      .map(function (o) { return o.value; })
      .filter(function (v) { return v; });

    if (!allIds.length) {
      clearContainer(inProgressContainer);
      clearContainer(completedContainer);
      const emptyMsg = document.createElement("p");
      emptyMsg.className = "text-white small";
      emptyMsg.textContent = "No employees found.";
      inProgressContainer.appendChild(emptyMsg.cloneNode(true));
      completedContainer.appendChild(emptyMsg);
      return;
    }

    fetch("/dm/works/search-multi/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ employee_ids: allIds })
    })
      .then(function (res) { return res.json(); })
      .then(function (data) { renderWorks(data); })
      .catch(function (err) {
        console.error("Error fetching all works:", err);
      });
  }

  // existing search behavior (single employee)

  searchBtn.addEventListener("click", function () {
    const employeeId = employeeSelect.value;

    if (!employeeId) {
      alert("Select an employee first.");
      return;
    }

    const url = window.DM_WORKS_SEARCH_URL || "/dm/works/search/";

    const body = new URLSearchParams();
    body.append("employee_id", employeeId);

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-CSRFToken": getCSRFToken()
      },
      body: body.toString()
    })
      .then(function (response) {
        return response.json();
      })
      .then(function (data) {
        renderWorks(data);
      })
      .catch(function (error) {
        console.error("Error fetching works:", error);
      });
  });

  // initial load: all employees' works
  fetchAllEmployees();
});
