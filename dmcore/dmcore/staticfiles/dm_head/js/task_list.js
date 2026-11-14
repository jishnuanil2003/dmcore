function openEditModal(id, name, description) {
    document.getElementById('editTaskId').value = id;
    document.getElementById('editTaskName').value = name;
    document.getElementById('editTaskDescription').value = description;
    var myModal = new bootstrap.Modal(document.getElementById('editTaskModal'));
    myModal.show();
}

// Initialize Bootstrap tooltips
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
});