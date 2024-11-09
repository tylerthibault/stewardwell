# JavaScript Documentation

## Core Functionality

### Form Validation
```javascript
// Registration Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.querySelector('.registration-form');
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            // Form validation logic
        });
    }
});

// PIN Input Validation
function validatePinInput(input) {
    input.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, '').slice(0, 4);
    });
}
```

### Dynamic UI Elements

1. **Parent Registration Toggle**
```javascript
// Toggle Family Name Field
document.getElementById('is_parent').addEventListener('change', function() {
    const familyNameGroup = document.querySelector('.family-name-group');
    familyNameGroup.style.display = this.checked ? 'block' : 'none';
});
```

2. **Modal Handling**
```javascript
// Bootstrap Modal Initialization
const modal = new bootstrap.Modal(document.getElementById('addChildModal'));

// Modal Event Handlers
modal._element.addEventListener('shown.bs.modal', function() {
    document.querySelector('input[name="username"]').focus();
});
```

3. **Flash Messages**
```javascript
// Auto-dismiss Flash Messages
document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
    setTimeout(function() {
        bootstrap.Alert.getOrCreateInstance(alert).close();
    }, 5000);
});
```

## Utility Functions

1. **Data Formatting**
```javascript
// Date Formatting
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Number Formatting
function formatCurrency(number) {
    return number.toLocaleString('en-US');
}
```

2. **Form Helpers**
```javascript
// Form Reset with Confirmation
function resetFormWithConfirmation(formElement) {
    if (confirm('Are you sure you want to reset the form?')) {
        formElement.reset();
    }
}

// Form Data Serialization
function serializeForm(form) {
    return new FormData(form);
}
```

## Event Handlers

1. **Sidebar Navigation**
```javascript
// Mobile Sidebar Toggle
document.querySelector('.sidebar-toggle').addEventListener('click', function() {
    document.querySelector('.sidebar').classList.toggle('active');
});

// Close Sidebar on Outside Click (Mobile)
document.addEventListener('click', function(e) {
    const sidebar = document.querySelector('.sidebar');
    const toggle = document.querySelector('.sidebar-toggle');
    if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});
```

2. **Table Interactions**
```javascript
// Sortable Tables
function initSortableTable(tableElement) {
    tableElement.querySelectorAll('th[data-sort]').forEach(header => {
        header.addEventListener('click', () => {
            // Sorting logic
        });
    });
}
```

## AJAX Requests

1. **Data Fetching**
```javascript
// Generic Fetch Function
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
            },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}
```

2. **Form Submissions**
```javascript
// Async Form Submit
async function submitFormAsync(form, url) {
    try {
        const formData = new FormData(form);
        const response = await fetch(url, {
            method: 'POST',
            body: formData
        });
        return await response.json();
    } catch (error) {
        console.error('Error submitting form:', error);
        throw error;
    }
}
```

## Future Implementations

1. **Real-time Updates**
```javascript
// WebSocket Connection
const socket = new WebSocket('ws://your-server-url');
socket.addEventListener('message', function(event) {
    // Handle real-time updates
});
```

2. **Charts and Visualizations**
```javascript
// Chart.js Integration
function initializeCharts() {
    const ctx = document.getElementById('statsChart').getContext('2d');
    new Chart(ctx, {
        // Chart configuration
    });
}
```

3. **Drag and Drop**
```javascript
// Task Reordering
function initializeDragDrop() {
    new Sortable(document.querySelector('.task-list'), {
        // Sortable configuration
    });
}
```

## Error Handling

```javascript
// Global Error Handler
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    // Error reporting logic
});

// AJAX Error Handler
function handleAjaxError(error) {
    console.error('AJAX error:', error);
    // Show user-friendly error message
}
```

## Performance Considerations

1. **Debouncing**
```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
```

2. **Lazy Loading**
```javascript
// Image Lazy Loading
document.addEventListener('DOMContentLoaded', function() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                observer.unobserve(img);
            }
        });
    });
    lazyImages.forEach(img => imageObserver.observe(img));
});
```

## Form Handlers

### Category Creation in Chore Form
```javascript
document.querySelector('#addChoreModal form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (categorySelect.value === 'new') {
        // Create new category via AJAX
        const response = await fetch('/chores/categories/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: document.getElementById('new_category_name').value,
                color: document.getElementById('new_category_color').value,
                icon: document.getElementById('new_category_icon').value
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            document.getElementById('category_id').value = result.category_id;
        }
    }
    
    this.submit();
});
```

### Due Date Toggle
```javascript
document.getElementById('has_due_date').addEventListener('change', function() {
    const dueDateContainer = document.getElementById('due_date_container');
    const dueDateInput = document.getElementById('due_date');
    
    dueDateContainer.style.display = this.checked ? 'block' : 'none';
    dueDateInput.required = this.checked;
    
    if (!this.checked) {
        dueDateInput.value = '';
    }
});
```

### Family Code Copy
```javascript
function copyFamilyCode() {
    const code = familyCodeElement.textContent;
    navigator.clipboard.writeText(code).then(() => {
        // Visual feedback
        button.classList.add('btn-success');
        setTimeout(() => {
            button.classList.remove('btn-success');
        }, 2000);
    });
}
```

## Input Handlers

### Auto-Uppercase Input
```javascript
document.getElementById('family_code').addEventListener('input', function(e) {
    this.value = this.value.toUpperCase();
});
```

### Category Select Handler
```javascript
function handleCategorySelect(selectElement) {
    const newCategoryContainer = document.getElementById('new_category_container');
    const categoryIdInput = document.getElementById('category_id');
    
    if (selectElement.value === 'new') {
        newCategoryContainer.style.display = 'block';
        categoryIdInput.value = '';
    } else {
        newCategoryContainer.style.display = 'none';
        categoryIdInput.value = selectElement.value;
    }
}
```

## Bootstrap Initializations

### Tooltips
```javascript
var tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
);
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});
```

## Future Enhancements

### Real-time Updates
```javascript
// WebSocket connection for live updates
const socket = new WebSocket('ws://your-server/ws');
socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    updateUI(data);
};
```

### Drag-and-Drop
```javascript
// Sortable chore lists
new Sortable(choresList, {
    animation: 150,
    ghostClass: 'sortable-ghost',
    onEnd: function(evt) {
        updateChoreOrder(evt.oldIndex, evt.newIndex);
    }
});
```

### Form Validation
```javascript
function validateChoreForm() {
    const title = document.getElementById('title').value;
    const points = document.getElementById('points').value;
    const coins = document.getElementById('coins').value;
    
    if (!title || !points || !coins) {
        showError('Please fill in all required fields');
        return false;
    }
    return true;
}
``` 