document.querySelectorAll('.add-field-category').forEach(btn => {
  btn.addEventListener('click', function () {
    const categoryId = this.dataset.categoryid;
    document.getElementById('addFieldForm').reset();
    document.getElementById('add_field_category_id').value = categoryId;

    fetch(`/get-category/${categoryId}/`)
      .then(res => res.json())
      .then(data => {
        document.getElementById('add_field_client').value = data.client_name;
        document.getElementById('add_field_category').value = data.collection_for;

        document.getElementById('edit_client_id').value = data.client_id;
        document.getElementById('edit_work_id').value = data.work_id;

        const modal = new bootstrap.Modal(document.getElementById('addFieldModal'));
        modal.show();
      });
  });
});

document.getElementById('addFieldForm').addEventListener('submit', function (e) {
  e.preventDefault();
  const formData = new FormData(this);

  fetch('/add-field/', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
    if (data.success) location.reload();
  });
});

document.querySelectorAll('.edit-lead-field').forEach(button => {
  button.addEventListener('click', function () {
    const fieldId = this.dataset.fieldId;
    fetch(`/get-field/${fieldId}/`)
      .then(response => response.json())
      .then(data => {
        if (data.error) throw new Error(data.error);
        document.getElementById('edit_field_id').value = fieldId;
        document.getElementById('edit_field_name').value = data.name || '';
        document.getElementById('edit_field_description').value = data.description || '';
        document.getElementById('edit_field_question_id').value = data.question_id || '';
        new bootstrap.Modal(document.getElementById('editFieldModal')).show();
      })
      .catch(error => alert(error.message));
  });
});

document.getElementById('editFieldForm').addEventListener('submit', function (e) {
  e.preventDefault();
  fetch('/edit-field/', {method: 'POST', body: new FormData(this)})
    .then(response => response.json())
    .then(data => {
      alert(data.message);
      if (data.success) location.reload();
    });
});

document.getElementById('btnClearAddField').addEventListener('click', function () {
  document.querySelector('#addFieldForm input[name="field_name"]').value = '';
  document.querySelector('#addFieldForm textarea[name="description"]').value = '';
  document.getElementById('add_field_question_id').value = '';
});
