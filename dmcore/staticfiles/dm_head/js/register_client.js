let timer;

// Attach keyup + blur handlers
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('keyup', function () {
        clearTimeout(timer);
        timer = setTimeout(() => {
            validateField(this);
        }, 250);
    });
    input.addEventListener('blur', function () {
        validateField(this);
        dbCheckField(this);
    });
});

// Regex + logic validation
function validateField(field) {
    const name = field.name;
    const value = field.value.trim();

    if (name.includes('phone')) {
        if (!/^\d{10}$/.test(value)) {
            showError(field, 'Phone must be exactly 10 digits');
        } else if (name.includes('alter')) {
            const mainName = name.replace('_alter', '');
            const mainValue = document.querySelector(`[name="${mainName}"]`)?.value.trim();
            if (value === mainValue) {
                showError(field, 'Alternate phone must be different from primary');
            } else {
                clearError(field);
            }
        } else {
            clearError(field);
        }
    }

    if (name.includes('email')) {
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) {
            showError(field, 'Email must contain @ and a valid domain (like .com)');
        } else if (name.includes('alter')) {
            const mainName = name.replace('_alter', '_primary');
            const mainValue = document.querySelector(`[name="${mainName}"]`)?.value.trim();
            if (value === mainValue) {
                showError(field, 'Alternate email must be different from primary');
            } else {
                clearError(field);
            }
        } else {
            const alterName = name.replace('_primary', '_alter');
            const alterValue = document.querySelector(`[name="${alterName}"]`)?.value.trim();
            if (value === alterValue && alterValue !== '') {
                showError(field, 'Primary email must be different from alternate');
            } else {
                clearError(field);
            }
        }
    }

    if (name.includes('website')) {
        if (!/^https?:\/\/.+\..+/.test(value)) {
            showError(field, 'Website must start with http:// or https://');
        } else {
            clearError(field);
        }
    }
}

// DB uniqueness check on blur
function dbCheckField(field) {
    const name = field.name;
    const value = field.value.trim();
    const clientId = document.querySelector('[name="client_id"]')?.value || '';
    if (!value) return;

    fetch(`/check-unique/?field=${name}&value=${encodeURIComponent(value)}&exclude_id=${clientId}`)
        .then(response => response.json())
        .then(data => {
            if (!data.is_unique) {
                showError(field, `${capitalize(name.replace(/_/g, ' '))} already exists`);
            } else {
                clearError(field);
            }
        });
}

// Show error under input
function showError(field, message) {
    field.classList.add('is-invalid');
    let error = field.nextElementSibling;
    if (!error || !error.classList.contains('invalid-feedback')) {
        error = document.createElement('div');
        error.className = 'invalid-feedback';
        field.parentNode.appendChild(error);
    }
    error.textContent = message;
}

// Clear error from input
function clearError(field) {
    field.classList.remove('is-invalid');
    let error = field.nextElementSibling;
    if (error && error.classList.contains('invalid-feedback')) {
        error.remove();
    }
}

// Copy personal → business address on checkbox
document.getElementById('sameAsPersonal').addEventListener('change', function () {
    const fields = ['address1', 'address2', 'address3', 'place', 'district', 'state'];
    fields.forEach(field => {
        const personal = document.querySelector(`[name="client_${field}"]`);
        const business = document.querySelector(`[name="client_business_${field}"]`);
        if (this.checked) {
            business.value = personal.value;
            business.readOnly = true;
        } else {
            business.readOnly = false;
        }
    });
});

// Capitalize helper
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Edit client handler
function editClient(clientId) {
    fetch(`/get-client/${clientId}/`)
        .then(response => response.json())
        .then(data => {
            for (const key in data) {
                const field = document.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            }

            let clientIdField = document.querySelector('[name="client_id"]');
            if (!clientIdField) {
                clientIdField = document.createElement('input');
                clientIdField.type = 'hidden';
                clientIdField.name = 'client_id';
                document.getElementById('registerClientForm').appendChild(clientIdField);
            }
            clientIdField.value = clientId;

            // Show update button, hide register button
            document.getElementById('registerBtn').style.display = 'none';
            document.getElementById('updateBtn').style.display = 'block';

            const modal = new bootstrap.Modal(document.getElementById('registerClientModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error loading client:', error);
            alert('Failed to load client data.');
        });
}

document.getElementById('registerClientModal').addEventListener('hidden.bs.modal', () => {
    const form = document.getElementById('registerClientForm');
    form.reset();
    form.querySelector('[name="client_id"]').value = ''; // clear hidden client_id
    document.getElementById('registerBtn').style.display = 'block';
    document.getElementById('updateBtn').style.display = 'none';
});

