(function () {
  "use strict";

  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  function setText(id, val) {
    var el = document.getElementById(id);
    if (!el) return;
    el.textContent = String(val);
  }

  function fetchCounts() {
    var wrap = document.querySelector(".admin-works-wrap");
    if (!wrap) return;

    var companyId = wrap.getAttribute("data-company-id");
    var url = window.ADMIN_WORKS_COUNTS_URL;
    if (!url) return;

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
      },
      body: JSON.stringify({ company_id: companyId }),
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (!data || !data.success) {
          return;
        }

        var c = data.counts || {};
        setText("countHead", c.head || 0);
        setText("countTL", c.team_lead || 0);
        setText("countExe", c.executive || 0);
        setText("countClient", c.client || 0);
      })
      .catch(function () {
      });
  }

  document.addEventListener("DOMContentLoaded", function () {
    fetchCounts();

    document.querySelectorAll(".works-card").forEach(function (card) {
      card.addEventListener("click", function () {
        // Placeholder: you can redirect based on card.dataset.card
        // Example:
        // if (card.dataset.card === "client") window.location.href = "/admin/clients/";
      });
    });
  });
})();
