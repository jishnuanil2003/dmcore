document.addEventListener("DOMContentLoaded", function () {
  console.log("js loaded head verify page.js");

  //? ========== Lead Detail Offcanvas ==========
  document.querySelectorAll(".show-lead-details").forEach(btn => {
    btn.addEventListener("click", function () {
      const leadId = this.dataset.id;

      fetch(`/get-lead-details/${leadId}/`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            const ld = data.lead;
            document.getElementById("ld_name").textContent = ld.name;
            document.getElementById("ld_contact").textContent = ld.contact;
            document.getElementById("ld_email").textContent = ld.email;

            document.getElementById("ld_verified").classList.toggle("text-success", ld.verified);
            document.getElementById("ld_verified").textContent = ld.verified ? "Verified" : "Unverified";

            document.getElementById("ld_waste").classList.toggle("text-danger", ld.waste);
            document.getElementById("ld_waste").textContent = ld.waste ? "Marked as waste" : "Not a waste";

            document.getElementById("ld_incomplete").classList.toggle("text-warning", ld.incomplete);
            document.getElementById("ld_incomplete").textContent = ld.incomplete ? "Incomplete" : "Not Marked as incomplete";

            const more = document.getElementById("ld_more");
            more.innerHTML = "";
            data.details.forEach(field => {
              const div = document.createElement("div");
              div.className = "mb-2 d-flex justify-content-between align-items-center";
              div.innerHTML = `<span>${field.field_name}</span><span>${field.field_data}</span>`;
              more.appendChild(div);
            });

            new bootstrap.Offcanvas(document.getElementById("leadDetailCanvas")).show();
          }
        })
        .catch(err => console.error("Failed to fetch lead:", err));
    });
  });

  //? ========== Modal Toggle ==========
  document.getElementById("toggleSingle").addEventListener("click", () => {
    document.getElementById("addLeadForm").style.display = "block";
    document.getElementById("excelUploadForm").style.display = "none";
  });

  document.getElementById("toggleExcel").addEventListener("click", () => {
    document.getElementById("addLeadForm").style.display = "none";
    document.getElementById("excelUploadForm").style.display = "block";
  });

  //? ========== Form Validation ==========
  const emailInput = document.getElementById("lead_email");
  const contactInput = document.getElementById("lead_contact");
  const emailError = document.getElementById("email_error");
  const contactError = document.getElementById("contact_error");

  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  const phoneRegex = /^\d{10}$/;

  emailInput.addEventListener("input", () => {
    const val = emailInput.value.trim();
    emailError.textContent = !val ? "Email is required." : (!emailRegex.test(val) ? "Enter a valid email." : "");
  });

  contactInput.addEventListener("input", () => {
    const val = contactInput.value.trim();
    contactError.textContent = !val ? "Contact number is required." : (!phoneRegex.test(val) ? "Enter a valid 10-digit phone number." : "");
  });

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

  //? Add Lead (Single Entry) submission handler
  document.getElementById("addLeadForm").addEventListener("submit", function (e) {
    e.preventDefault();

    const isEmailValid = validateEmail();
    const isPhoneValid = validateContact();
    if (!isEmailValid || !isPhoneValid) return;

    const form = e.target;
    const formData = new FormData(form);

    fetch("/add-lead/", {
      method: "POST",
      headers: {
        "X-CSRFToken": formData.get("csrfmiddlewaretoken"),
      },
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          alert("Lead added successfully.");
          form.reset();
          bootstrap.Modal.getInstance(document.getElementById("addLeadModal")).hide();
          window.location.reload();
        } else {
          alert("Failed to add lead. Duplicate or invalid entry.");
        }
      })
      .catch(err => {
        console.error("AJAX error:", err);
        alert("Something went wrong. Try again.");
      });
  });

  //? ========== Status Change Logic ==========
  document.getElementById("statusApplyBtn").addEventListener("click", function () {
    const selectedStatus = document.getElementById("statusAction").value;
    const selectedLeads = Array.from(document.querySelectorAll("input[name='selected_leads']:checked")).map(cb => cb.value);

    if (!selectedStatus || selectedLeads.length === 0) {
      return;
    }

    fetch("/change-lead-status/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
      },
      body: JSON.stringify({ leads: selectedLeads, status: selectedStatus })
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.reload();
        } else {
          console.error("Backend responded with failure", data);
        }
      })
      .catch(err => console.error("Request failed", err));
  });

  //? ========== Filtering & Search ==========
  const leadTable = $("#leadTable").DataTable({
    searching: false,
    ordering: true,
    paging: false,
    info: false,
    order: [],
    columnDefs: [{ orderable: false, targets: "nosort" }]
  });

  document.getElementById("resetFilters")?.addEventListener("click", () => {
    location.reload();
  });

  function applyFiltersAndSearch() {
    const statusVal = document.getElementById("statusFilter").value;
    const empVal = document.getElementById("employeeFilter").value;
    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;
    const searchQuery = document.getElementById("searchInput").value.toLowerCase();
    const rowLimit = parseInt(document.getElementById("rowLimit").value) || Infinity;

    const rows = document.querySelectorAll("#leadTable tbody tr");
    let shown = 0;

    rows.forEach(row => {
      let show = true;
      const statusText = row.querySelector("td:nth-child(6)")?.innerText.toLowerCase().trim();
      const empId = row.querySelector("td:nth-child(2)")?.dataset.empId;
      const addedOn = row.querySelector("td:nth-child(2) small")?.innerText;
      const fromDate = row.querySelector("td:nth-child(2)")?.dataset.from;
      const toDate = row.querySelector("td:nth-child(2)")?.dataset.to;
      const rowText = row.innerText.toLowerCase();

      if (searchQuery && !rowText.includes(searchQuery)) show = false;
      if (empVal && empId !== empVal) show = false;

      const statusMap = {
        "unverified": "unverified",
        "verified": "verified",
        "waste": "waste",
        "not_waste": "not a waste",
        "incomplete": "incomplete",
        "not_incomplete": "not marked as incomplete",
        "repeated": "repeated"
      };
      if (statusVal && statusText !== statusMap[statusVal]) show = false;

      const addedDate = new Date(addedOn);
      if (start && addedDate < new Date(start)) show = false;
      if (end && addedDate > new Date(end)) show = false;
      if (fromDate && start && new Date(fromDate) < new Date(start)) show = false;
      if (toDate && end && new Date(toDate) > new Date(end)) show = false;

      row.style.display = show && shown < rowLimit ? "" : "none";
      if (show && shown < rowLimit) shown++;
    });

    updateFilterHeading();
  }

  function updateFilterHeading() {
    const statusVal = document.getElementById("statusFilter").value;
    const heading = document.getElementById("filterHeading");
    const labelMap = {
      "unverified": "Unverified Leads",
      "verified": "Verified Leads",
      "waste": "Wasted Leads",
      "not_waste": "Not Wasted Leads",
      "incomplete": "Incomplete Leads",
      "not_incomplete": "Not Incomplete Leads",
      "repeated": "Repeated Leads"
    };
    heading.textContent = labelMap[statusVal] || "All Leads";
  }

  ["statusFilter", "employeeFilter", "startDate", "endDate", "searchInput", "rowLimit"].forEach(id => {
    document.getElementById(id).addEventListener("change", applyFiltersAndSearch);
    document.getElementById(id).addEventListener("input", applyFiltersAndSearch);
  });

  // document.getElementById("resetFilters").addEventListener("click", function () {
  //   ["statusFilter", "employeeFilter", "startDate", "endDate", "searchInput", "rowLimit"].forEach(id => {
  //     const el = document.getElementById(id);
  //     if (el) el.value = "";
  //   });
  //   applyFiltersAndSearch();
  // });

  document.getElementById("searchInput").addEventListener("input", applyFiltersAndSearch);

  applyFiltersAndSearch();
});

//? ========== Select All Checkbox ==========
document.getElementById("checkAll").addEventListener("change", function () {
  const isChecked = this.checked;
  document.querySelectorAll("#leadTable tbody tr").forEach(row => {
    if (row.style.display !== "none") {
      const cb = row.querySelector("input[type='checkbox']");
      if (cb) cb.checked = isChecked;
    }
  });
});

//? ========== PDF Export ==========
document.getElementById("pdfBtn").addEventListener("click", function () {
  document.getElementById("pdfBtn")?.addEventListener("click", exportPDF);

function exportPDF() {
  const table = document.getElementById("leadTable").cloneNode(true);

  table.querySelectorAll("thead th:nth-child(1), thead th:nth-child(4), tbody td:nth-child(1), tbody td:nth-child(4)").forEach(el => el.remove());
  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.removeAttribute("aria-sort");
    th.removeAttribute("aria-label");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.border = "1px solid #ccc";
    th.style.padding = "6px";
    th.style.textAlign = "center";
  });

  table.classList.remove("table-dark", "table-striped", "table-hover");
  table.classList.add("table", "table-bordered", "table-sm");
  table.style.fontSize = "10px";
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";
  table.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  const wrapper = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = "Lead List";
  title.style.textAlign = "center";
  title.style.marginBottom = "15px";
  wrapper.appendChild(title);
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    filename: `Leads_${new Date().toISOString().split("T")[0]}.pdf`,
    image: { type: "jpeg", quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: "in", format: "letter", orientation: "portrait" }
  }).from(wrapper).save();
}
});

//? ========== Print ==========
document.getElementById("printBtn")?.addEventListener("click", () => {
  const table = document.getElementById("leadTable").cloneNode(true);

  // Remove checkbox and More column
  table.querySelectorAll("thead th:nth-child(1), thead th:nth-child(4), tbody td:nth-child(1), tbody td:nth-child(4)").forEach(el => el.remove());

  // Style headers
  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.fontWeight = "bold";
    th.style.textAlign = "center";
    th.style.padding = "6px";
    th.style.border = "1px solid #ccc";
  });

  // Style cells
  table.querySelectorAll("td").forEach(td => {
    td.style.textAlign = "center";
    td.style.border = "1px solid #ccc";
    td.style.padding = "4px";
  });

  // Apply table styles
  table.className = "table table-bordered table-sm";
  table.style.fontSize = "10px";
  table.style.width = "100%";
  table.style.borderCollapse = "collapse";

  // Remove filtered-out rows
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  // Wrapper with white background
  const wrapper = document.createElement("div");
  wrapper.style.padding = "20px";
  wrapper.style.fontFamily = "sans-serif";
  wrapper.style.backgroundColor = "#ffffff"; // force white
  wrapper.innerHTML = `<h3 style="text-align: center; margin-bottom: 15px;">Lead Report</h3>`;
  wrapper.appendChild(table);

  // Replace body with clean view
  const original = document.body.innerHTML;
  document.body.innerHTML = "";
  document.body.style.backgroundColor = "#ffffff"; // force body background
  document.body.appendChild(wrapper);

  setTimeout(() => {
    window.print();
    document.body.innerHTML = original;
    location.reload();
  }, 0);
});


//? ========== Share ==========

document.getElementById("shareViaEmail").addEventListener("click", () => {
  console.log("Clicked Email button");
  document.getElementById("emailSection").style.display = "block";
});

document.getElementById("shareViaWhatsApp").addEventListener("click", () => {
  console.log("Clicked WhatsApp button");
  document.getElementById("emailSection").style.display = "none";
  document.getElementById("sendWhatsApp")?.click();
});



// ? ========= share ==========
document.getElementById("shareViaWhatsApp")?.addEventListener("click", () => {
  console.log("Clicked WhatsApp button");

  generateShareablePDF(blob => {
    console.log("Generating and downloading PDF...");

    // Create a download link
    const file = new File([blob], "Lead_Report.pdf", { type: "application/pdf" });
    const fileURL = URL.createObjectURL(file);
    const a = document.createElement("a");
    a.href = fileURL;
    a.download = "Lead_Report.pdf";
    a.style.display = "none";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(fileURL);

    // Open WhatsApp Web
    const message = encodeURIComponent("Please find the lead list attached below.");
    const whatsappURL = `https://wa.me/?text=${message}`;
    console.log("Opening WhatsApp Web...");
    window.open(whatsappURL, "_blank");
  });
});



document.getElementById("sendEmail")?.addEventListener("click", () => {
  console.log("📨 Send Email clicked");

  const emailList = document.getElementById("emailInput").value.trim();
  const message = document.getElementById("emailMessage").value.trim();

  if (!emailList) {
    alert("Please enter at least one email address.");
    return;
  }

  generateShareablePDF(blob => {
    const formData = new FormData();
    formData.append("pdf", blob, "Lead_Report.pdf");
    formData.append("emails", emailList);
    formData.append("message", message);

   fetch("/send_lead_pdf_mail/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
      },
      body: formData
    })

    .then(res => res.json())
    .then(data => {
      console.log("📨 Email backend response:", data);
      if (data.success) {
        alert("Email sent successfully.");
        // 
        document.getElementById("emailInput").value = "";
        document.getElementById("emailMessage").value = "";
        document.getElementById("emailSection").style.display = "none";

        // Close modal
        const shareModal = bootstrap.Modal.getInstance(document.getElementById("shareModal"));
        shareModal.hide();
        // 
      } else {
        alert("Failed to send email. Please check addresses.");
      }
    })
    .catch(err => {
      console.error("Email send error:", err);
      alert("Something went wrong while sending email.");
    });
  });
});




//? ========= share pdf generator =========
function generateShareablePDF(callback) {
  const table = document.getElementById("leadTable").cloneNode(true);

  // Remove unwanted columns (checkbox, more)
  table.querySelectorAll("thead th:nth-child(1), thead th:nth-child(4), tbody td:nth-child(1), tbody td:nth-child(4)").forEach(el => el.remove());

  // Clean styles
  table.classList.remove("table-dark", "table-striped", "table-hover");
  table.classList.add("table", "table-bordered", "table-sm");
  table.style.width = "100%";
  table.style.fontSize = "10px";
  table.style.borderCollapse = "collapse";

  // Add styling to headers
  table.querySelectorAll("th").forEach(th => {
    th.removeAttribute("class");
    th.style.backgroundColor = "#333333";
    th.style.color = "#ffffff";
    th.style.border = "1px solid #ccc";
    th.style.textAlign = "center";
    th.style.padding = "6px";
  });

  // Add styling to cells
  table.querySelectorAll("td").forEach(td => {
    td.style.border = "1px solid #ccc";
    td.style.textAlign = "center";
    td.style.padding = "4px";
  });

  // Remove filtered-out rows
  Array.from(table.querySelectorAll("tbody tr")).forEach(row => {
    if (row.style.display === "none") row.remove();
  });

  const wrapper = document.createElement("div");
  const heading = document.createElement("h3");
  heading.textContent = "Lead Report";
  heading.style.textAlign = "center";
  heading.style.marginBottom = "10px";
  wrapper.appendChild(heading);
  wrapper.appendChild(table);

  html2pdf().set({
    margin: [0.4, 0.2],
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }).from(wrapper).outputPdf("blob").then(blob => {
    callback(blob);
  });
}
