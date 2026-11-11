(function () {
  "use strict";

  var cfg = window.__OC || {};
  var clientSelect = document.getElementById("clientSelect");
  var sectionMount = document.getElementById("sectionMount");
  var cardButtons = Array.prototype.slice.call(document.querySelectorAll(".admin-oc-card"));

  var state = { clientId: "", section: "registered" };

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  function setActiveCard(section) {
    cardButtons.forEach(function (btn) {
      btn.classList.toggle("active", btn.getAttribute("data-section") === section);
    });
  }

  function requireClient() {
    if (!state.clientId) {
      alert("Select client first");
      return false;
    }
    return true;
  }

  function renderSection() {
    if (!requireClient()) {
      sectionMount.innerHTML = "";
      return;
    }

    var mod = window.OC_SECTIONS && window.OC_SECTIONS[state.section];
    if (!mod || typeof mod.render !== "function") {
      sectionMount.innerHTML = '<div class="text-white-50">Section not wired.</div>';
      return;
    }
    mod.render(sectionMount, state.clientId);
  }

  function loadDropdown() {
    fetch(cfg.dropdownUrl, { credentials: "same-origin" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        var html = '<option value="" selected disabled>Select client</option>';

        if (data && data.success && Array.isArray(data.clients)) {
          data.clients.forEach(function (c) {
            html += '<option value="' + escapeHtml(c.id) + '">' + escapeHtml(c.name || "-") + "</option>";
          });
          clientSelect.disabled = false;
        } else {
          clientSelect.disabled = true;
        }

        clientSelect.innerHTML = html;
      })
      .catch(function () {
        clientSelect.disabled = true;
      });
  }

  clientSelect.addEventListener("change", function () {
    state.clientId = clientSelect.value || "";
    sectionMount.innerHTML = "";
  });

  cardButtons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var sec = btn.getAttribute("data-section");
      state.section = sec;
      setActiveCard(sec);
      renderSection();
    });
  });

  window.__OC_HELPERS = { escapeHtml: escapeHtml };

  setActiveCard(state.section);
  loadDropdown();
})();
