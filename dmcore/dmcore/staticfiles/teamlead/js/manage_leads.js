document.addEventListener("DOMContentLoaded", function () {
  const emailInput = document.getElementById("lead_email");
  const contactInput = document.getElementById("lead_contact");
  const emailError = document.getElementById("email_error");
  const contactError = document.getElementById("contact_error");

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const phoneRegex = /^\d{10}$/;

  function validateEmail() {
    const value = emailInput.value.trim();
    if (!value) {
      emailError.textContent = "Email is required.";
      return false;
    }
    if (!emailRegex.test(value)) {
      emailError.textContent = "Enter a valid email (e.g., user@example.com).";
      return false;
    }
    emailError.textContent = "";
    return true;
  }

  function validateContact() {
    const value = contactInput.value.trim();
    if (!value) {
      contactError.textContent = "Contact number is required.";
      return false;
    }
    if (!phoneRegex.test(value)) {
      contactError.textContent = "Enter a valid 10-digit phone number.";
      return false;
    }
    contactError.textContent = "";
    return true;
  }

  emailInput.addEventListener("input", validateEmail);
  contactInput.addEventListener("input", validateContact);

  const form = document.getElementById("addLeadForm");
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const isEmailValid = validateEmail();
    const isPhoneValid = validateContact();
    if (!isEmailValid || !isPhoneValid) return;

    const data = new FormData(form);
    fetch("/add-lead/", {
      method: "POST",
      body: data,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          window.location.reload();
        } else {
          window.location.href = window.location.href.split("#")[0];
        }
      })
      .catch((err) => {
        alert("Something went wrong.");
        console.error(err);
      });
  });

  // Offcanvas details view
  document.querySelectorAll(".show-lead-details").forEach((btn) => {
    btn.addEventListener("click", () => {
      const leadId = btn.dataset.id;
      fetch(`/get-lead-details/${leadId}/`)
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            const l = data.lead;
            document.getElementById("ld_name").innerText = l.name;
            document.getElementById("ld_contact").innerText = l.contact;
            document.getElementById("ld_email").innerText = l.email;

            const verifiedBadge = document.getElementById("ld_verified");
            if (l.verified) {
              verifiedBadge.className = "badge text-success";
              verifiedBadge.innerText = "Verified";
            } else {
              verifiedBadge.className = "badge text-danger";
              verifiedBadge.innerText = "Unverified";
            }

            const wasteBadge = document.getElementById("ld_waste");
            wasteBadge.className = l.waste ? "badge text-danger" : "badge text-secondary";
            wasteBadge.innerText = l.waste ? "Marked as Waste" : "Not a waste";

            const incompleteBadge = document.getElementById("ld_incomplete");
            incompleteBadge.className = l.incomplete ? "badge text-danger" : "badge text-success";
            incompleteBadge.innerText = l.incomplete ? "Marked as Incomplete" : "Not Marked as incomplete";


            const detailsDiv = document.getElementById("ld_more");
            detailsDiv.innerHTML = "";
            data.details.forEach((item) => {
              const p = document.createElement("p");
              p.innerHTML = `<strong>${item.field_name}</strong> : ${item.field_data}`;
              detailsDiv.appendChild(p);
            });

            new bootstrap.Offcanvas(document.getElementById("leadDetailCanvas")).show();
          }
        });
    });
  });

  // Table filtering
  const leadTable = $("#leadTable").DataTable({
    searching: false,
    ordering: true,
    paging: false,
    info: false,
    order: [],
    columnDefs: [{ orderable: false, targets: "nosort" }],
  });

  document.getElementById("searchInput").addEventListener("input", function () {
    const filter = this.value.toLowerCase();
    const rows = document.querySelectorAll("#leadTable tbody tr");
    rows.forEach((row) => {
      const rowText = row.innerText.toLowerCase();
      row.style.display = rowText.includes(filter) ? "" : "none";
    });
  });

  document.getElementById("clearSearch").addEventListener("click", function () {
    const input = document.getElementById("searchInput");
    input.value = "";
    const rows = document.querySelectorAll("#leadTable tbody tr");
    rows.forEach((row) => (row.style.display = ""));
  });
});
