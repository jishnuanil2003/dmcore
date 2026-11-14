document.addEventListener("DOMContentLoaded", function () {
  function getCsrfToken() {
    var match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  }

  var modalEl = document.getElementById("employeeEditModal");
  if (!modalEl || !window.bootstrap) return;
  var modal = bootstrap.Modal.getOrCreateInstance(modalEl);

  var empIdEl = document.getElementById("emp_id");

  var fields = {
    name: document.getElementById("emp_name"),
    employee_code: document.getElementById("emp_employee_code"),
    contact_number: document.getElementById("emp_contact_number"),
    email: document.getElementById("emp_email"),
    address_line1: document.getElementById("emp_address_line1"),
    address_line2: document.getElementById("emp_address_line2"),
    address_line3: document.getElementById("emp_address_line3"),
    pin: document.getElementById("emp_pin"),
    location: document.getElementById("emp_location"),
    district: document.getElementById("emp_district"),
    state: document.getElementById("emp_state"),
  };

  function setField(key, val) {
    if (fields[key]) fields[key].value = val || "";
  }

  function getPayloadFromFields() {
    return {
      emp_id: empIdEl.value,
      name: fields.name.value || "",
      contact_number: fields.contact_number.value || "",
      email: fields.email.value || "",
      address_line1: fields.address_line1.value || "",
      address_line2: fields.address_line2.value || "",
      address_line3: fields.address_line3.value || "",
      pin: fields.pin.value || "",
      location: fields.location.value || "",
      district: fields.district.value || "",
      state: fields.state.value || "",
    };
  }

  document.addEventListener("click", function (e) {
    var btn = e.target.closest(".emp-modal-btn");
    if (!btn) return;

    var empId = btn.getAttribute("data-emp-id");
    if (!empId) return;

    fetch("/ad/employee/details/?emp_id=" + encodeURIComponent(empId), {
      method: "GET",
      headers: { "X-Requested-With": "XMLHttpRequest" },
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (!data.success) {
          alert(data.message || "Failed");
          return;
        }
        var emp = data.employee || {};
        empIdEl.value = emp.id || empId;

        setField("name", emp.name);
        setField("employee_code", emp.employee_code);
        setField("contact_number", emp.contact_number);
        setField("email", emp.email);
        setField("address_line1", emp.address_line1);
        setField("address_line2", emp.address_line2);
        setField("address_line3", emp.address_line3);
        setField("pin", emp.pin);
        setField("location", emp.location);
        setField("district", emp.district);
        setField("state", emp.state);

        modal.show();
      })
      .catch(function () {
        alert("Network error");
      });
  });

  var btnActivate = document.getElementById("btnActivateEmployee");
  btnActivate.addEventListener("click", function () {
    var payload = getPayloadFromFields();
    payload.activate = true;
  
    fetch("/ad/employee/update/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(payload),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (!data.success) {
          alert(data.message || "Activate failed");
          return;
        }
  
        modal.hide();
        window.location.reload();
      })
      .catch(function (err) {
        console.error(err);
        alert("Network error");
      });
  });
  
});
