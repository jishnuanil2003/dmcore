// When opening the modal, fetch client data and load tasks
console.log("does this work")
function openWorkModal(clientId) {
    console.log('openWorkModal called with clientId:', clientId);
    fetch(`/get-client/${clientId}/`)
        .then(res => res.json())
        .then(data => {
            document.getElementById('workClientId').value = clientId;
            document.getElementById('workCompanyId').value = data.company_id || '';
            document.getElementById('client_name').value = data.client_name;
            document.getElementById('business_name').value = data.client_business_name;

            loadTasks();
        });
}

// Load common tasks
function loadTasks() {
    fetch('/get-tasks/')
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById('taskCheckboxes');
            container.innerHTML = '';
            data.tasks.forEach(task => {
                const div = document.createElement('div');
                div.className = 'col-md-4 mb-2';

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.name = 'task_ids[]';
                checkbox.value = task.id;
                checkbox.className = 'form-check-input me-2 task-checkbox';

                div.appendChild(checkbox);
                div.append(` ${task.name}`);
                container.appendChild(div);
            });
        });
}

// Toggle + / - button for additional task
document.getElementById('addTaskToggleBtn').addEventListener('click', () => {
    const section = document.getElementById('additionalTaskContainer');
    const btn = document.getElementById('addTaskToggleBtn');
    const isVisible = section.style.display === 'block';
    section.style.display = isVisible ? 'none' : 'block';
    btn.classList.toggle('btn-outline-success', isVisible);
    btn.classList.toggle('btn-outline-danger', !isVisible);
    btn.textContent = isVisible ? '+' : '-';
});

// Clear form
document.getElementById('clearWorkFormBtn').addEventListener('click', () => {
    const form = document.getElementById('createWorkForm');

    Array.from(form.elements).forEach(el => {
        if (!el.readOnly && el.type !== 'hidden' && el.type !== 'button' && el.type !== 'submit') {
            if (el.type === 'checkbox' || el.type === 'radio') {
                el.checked = false;
            } else {
                el.value = '';
            }
        }
    });

    document.querySelectorAll('#taskCheckboxes input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.getElementById('additionalTaskContainer').style.display = 'none';
    document.getElementById('addTaskToggleBtn').classList.add('btn-outline-success');
    document.getElementById('addTaskToggleBtn').classList.remove('btn-outline-danger');
    document.getElementById('addTaskToggleBtn').textContent = '+';
});



// Submit form
document.getElementById('createWorkBtn').addEventListener('click', () => {
    const form = document.getElementById('createWorkForm');
    const formData = new FormData(form);
    const newTask = document.getElementById('newTaskInput').value.trim();
    if (newTask) formData.append('new_task', newTask);

    fetch('/create-work/', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        if (data.success) window.location.reload();
    });
});
