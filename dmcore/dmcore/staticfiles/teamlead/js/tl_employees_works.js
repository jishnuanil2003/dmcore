(function () {
  var clientSelect = document.getElementById("clientSelect");
  var searchBtn = document.getElementById("searchBtn");
  var inProgressContainer = document.getElementById("inProgressContainer");
  var completedContainer = document.getElementById("completedContainer");

  if (!clientSelect || !searchBtn || !inProgressContainer || !completedContainer) {
    console.error("TL Works: required DOM elements not found.");
    return;
  }

  var SEARCH_URL = window.TL_WORKS_SEARCH_URL;
  var TL_ID = window.TL_ID;
  // NEW: multi-search URL
  var SEARCH_MULTI_URL = window.TL_WORKS_SEARCH_MULTI_URL;

  if (!SEARCH_URL || !TL_ID) {
    console.error("TL Works: missing SEARCH_URL or TL_ID.");
    return;
  }
  if (!SEARCH_MULTI_URL) {
    console.error("TL Works: missing SEARCH_MULTI_URL.");
    return;
  }

  // -----------------------------
  // helpers
  // -----------------------------
  function clearContainer(el) {
    while (el.firstChild) {
      el.removeChild(el.firstChild);
    }
  }

  function renderNoData(container, text) {
    var wrapper = document.createElement("div");
    wrapper.className = "text-center py-3";

    var p = document.createElement("p");
    p.className = "text-white small mb-0";
    p.textContent = text || "No data.";
    wrapper.appendChild(p);

    container.appendChild(wrapper);
  }

  function createWorkCard(item) {
    var card = document.createElement("div");
    card.className = "card work-card mb-3";

    var body = document.createElement("div");
    body.className = "card-body";

    var title = document.createElement("h6");
    title.className = "card-title text-light mb-1";
    title.textContent = item.client_name || "Unnamed Client";
    body.appendChild(title);

    var subtitle = document.createElement("p");
    subtitle.className = "small text-white mb-1";

    if (item.type === "lead_collection") {
      subtitle.textContent = item.title || "Lead collection";
      body.appendChild(subtitle);

      if (item.categories && item.categories.length > 0) {
        var ul = document.createElement("ul");
        ul.className = "small mb-0";
        item.categories.forEach(function (cat) {
          if (!cat) return;
          var li = document.createElement("li");
          li.textContent = cat;
          ul.appendChild(li);
        });
        body.appendChild(ul);
      }
    } else {
      subtitle.textContent = item.title || "Task";
      body.appendChild(subtitle);
    }

    card.appendChild(body);
    return card;
  }

  function renderCards(data) {
    clearContainer(inProgressContainer);
    clearContainer(completedContainer);

    var inProg = data.in_progress || [];
    var done = data.completed || [];

    if (!inProg.length) {
      renderNoData(inProgressContainer, "No pending works for this client.");
    } else {
      inProg.forEach(function (item) {
        inProgressContainer.appendChild(createWorkCard(item));
      });
    }

    if (!done.length) {
      renderNoData(completedContainer, "No completed works for this client.");
    } else {
      done.forEach(function (item) {
        completedContainer.appendChild(createWorkCard(item));
      });
    }
  }

  // ============================
  // NEW PART: multi-client helper
  // ============================

  function getAllClientIds() {
    var ids = [];
    var options = clientSelect.querySelectorAll("option");
    options.forEach(function (opt) {
      if (opt.value) {
        ids.push(opt.value);
      }
    });
    return ids;
  }

  function fetchWorksForClients(clientIds) {
    clearContainer(inProgressContainer);
    clearContainer(completedContainer);

    if (!clientIds || !clientIds.length) {
      renderNoData(inProgressContainer, "No clients found.");
      renderNoData(completedContainer, "No clients found.");
      return;
    }

    fetch(SEARCH_MULTI_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest"
      },
      body: JSON.stringify({
        tl_id: TL_ID,
        client_ids: clientIds
      })
    })
      .then(function (res) {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then(function (data) {
        if (!data.success) {
          console.warn("TL Works (multi): success = false", data);
          renderNoData(inProgressContainer, "No data found.");
          renderNoData(completedContainer, "No data found.");
          return;
        }
        renderCards(data);
      })
      .catch(function (err) {
        console.error("TL Works (multi): error fetching works:", err);
        renderNoData(inProgressContainer, "Error loading data.");
        renderNoData(completedContainer, "Error loading data.");
      });
  }

  // ============================
  // EXISTING: single-client fetch
  // ============================

  function fetchWorksForClient() {
    var clientId = clientSelect.value;
    clearContainer(inProgressContainer);
    clearContainer(completedContainer);

    if (!clientId) {
      // if nothing selected, you can either:
      // 1) show "select client" (old behaviour)
      // 2) or show all clients (uncomment line below)
      //
      // fetchWorksForClients(getAllClientIds());
      renderNoData(inProgressContainer, "Select a client and click search.");
      renderNoData(completedContainer, "Select a client and click search.");
      return;
    }

    var url =
      SEARCH_URL +
      "?tl_id=" +
      encodeURIComponent(TL_ID) +
      "&client_id=" +
      encodeURIComponent(clientId);

    fetch(url, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest"
      }
    })
      .then(function (res) {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then(function (data) {
        if (!data.success) {
          console.warn("TL Works: API returned success = false", data);
          renderNoData(inProgressContainer, "No data found for this client.");
          renderNoData(completedContainer, "No data found for this client.");
          return;
        }
        renderCards(data);
      })
      .catch(function (err) {
        console.error("TL Works: error fetching works:", err);
        renderNoData(inProgressContainer, "Error loading data.");
        renderNoData(completedContainer, "Error loading data.");
      });
  }

  // click handler stays the same
  searchBtn.addEventListener("click", function () {
    fetchWorksForClient();
  });

  // ============================
  // INITIAL LOAD: ALL CLIENTS
  // ============================

  var allClientIds = getAllClientIds();
  if (allClientIds.length) {
    fetchWorksForClients(allClientIds);
  } else {
    clearContainer(inProgressContainer);
    clearContainer(completedContainer);
    renderNoData(inProgressContainer, "No clients found.");
    renderNoData(completedContainer, "No clients found.");
  }
})();
