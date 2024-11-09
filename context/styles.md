# Styles Documentation

## Design System

### Color Palette
```css
:root {
    --primary-color: #4169E1;    /* Royal Blue */
    --secondary-color: #4CAF50;  /* Green */
    --background-color: #f8f9fa; /* Light Gray */
    --text-color: #333333;       /* Dark Gray */
    --border-color: #e0e0e0;     /* Light Gray */
    --sidebar-bg: #2C3E7B;       /* Dark Blue */
    --shadow: 0 2px 4px rgba(0,0,0,0.05);
}
```

### Typography
```css
body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    font-size: 16px;
}

h1 { font-size: 2.5rem; }
h2 { font-size: 2rem; }
h3 { font-size: 1.75rem; }
h4 { font-size: 1.5rem; }
```

### Layout Components

1. **Container**
```css
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}
```

2. **Grid System**
```css
.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}
```

3. **Flexbox Layouts**
```css
.flex-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
}
```

### UI Components

1. **Buttons**
```css
.btn {
    padding: 0.75rem 1.5rem;
    border-radius: 6px;
    font-size: 0.95rem;
    transition: all 0.2s ease;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
}
```

2. **Cards**
```css
.card {
    background: white;
    border-radius: 12px;
    box-shadow: var(--shadow);
    padding: 1.5rem;
}
```

3. **Forms**
```css
.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 0.95rem;
}

.form-label {
    font-weight: 500;
    margin-bottom: 0.5rem;
}
```

### Navigation

1. **Sidebar**
```css
.sidebar {
    width: 250px;
    background-color: var(--sidebar-bg);
    height: 100vh;
    position: fixed;
}

.menu-item {
    padding: 0.75rem 1.5rem;
    color: rgba(255, 255, 255, 0.8);
    transition: all 0.3s ease;
}
```

2. **Navbar**
```css
.navbar {
    background: white;
    box-shadow: var(--shadow);
    padding: 0.75rem 0;
}
```

### Utilities

1. **Spacing**
```css
.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-3 { margin-top: 1rem; }
.mt-4 { margin-top: 1.5rem; }
.mt-5 { margin-top: 2rem; }
```

2. **Text Utilities**
```css
.text-primary { color: var(--primary-color); }
.text-muted { color: #666; }
.text-center { text-align: center; }
```

### Responsive Design

1. **Breakpoints**
```css
/* Mobile */
@media (max-width: 767px) {
    .container { padding: 0 0.5rem; }
    .grid { grid-template-columns: 1fr; }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1199px) {
    .grid { grid-template-columns: repeat(2, 1fr); }
}
```

2. **Mobile Navigation**
```css
@media (max-width: 767px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .sidebar.active {
        transform: translateX(0);
    }
}
```

### Animations

1. **Transitions**
```css
.transition-all {
    transition: all 0.3s ease;
}

.hover-lift:hover {
    transform: translateY(-2px);
}
```

2. **Loading States**
```css
.loading {
    opacity: 0.7;
    pointer-events: none;
}

.spinner {
    animation: spin 1s linear infinite;
}
```

## Chore-Specific Styles

### Chore Cards
```css
.chore-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}

.chore-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.chore-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color);
}

.chore-status {
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
}

.status-pending {
    background-color: var(--primary-color);
    color: white;
}

.status-completed {
    background-color: var(--secondary-color);
    color: white;
}

.status-overdue {
    background-color: #dc3545;
    color: white;
}
```

### Chore Tables
```css
.chore-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: white;
    border-radius: 8px;
    overflow: hidden;
}

.chore-table th {
    background-color: #f8f9fa;
    padding: 1rem;
    font-weight: 600;
    text-align: left;
}

.chore-table td {
    padding: 1rem;
    border-top: 1px solid #dee2e6;
}

.chore-table tr:hover {
    background-color: #f8f9fa;
}
```

### Reward Indicators
```css
.reward-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.85rem;
}

.coins-badge {
    background-color: #ffd700;
    color: #000;
}

.points-badge {
    background-color: #4CAF50;
    color: white;
}
```

### Form Elements
```css
.chore-form {
    max-width: 600px;
    margin: 0 auto;
}

.reward-input-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}

.due-date-toggle {
    margin-bottom: 1rem;
}

.due-date-field {
    transition: all 0.3s ease;
}
``` 