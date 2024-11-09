# Styles Documentation

## Core Variables
```css
:root {
    --primary-color: #4169E1;
    --secondary-color: #4CAF50;
    --background-color: #f8f9fa;
    --text-color: #333;
    --border-color: #e0e0e0;
    --shadow: 0 2px 4px rgba(0,0,0,0.05);
    --sidebar-bg: #2C3E7B;
}
```

## Layout Components

### Sidebar
```css
.sidebar {
    width: 250px;
    background-color: var(--sidebar-bg);
    color: white;
    padding: 1.5rem 0;
    position: fixed;
    height: 100vh;
}

.main-content {
    margin-left: 250px;
    padding: 2rem;
}
```

### Content Container
```css
.content-container {
    padding: 1.5rem;
}

.page-header {
    margin-bottom: 2rem;
}
```

## Card Components

### Base Card
```css
.card {
    background: white;
    border-radius: 12px;
    box-shadow: var(--shadow);
    border: none;
    margin-bottom: 1.5rem;
}

.card-header {
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    padding: 1rem;
}
```

### Statistics Cards
```css
.dashboard-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}

.stat {
    font-size: 2.5rem;
    font-weight: 600;
    color: var(--primary-color);
}
```

## Reward System Styles

### Reward Cards
```css
.reward-card {
    height: 100%;
    transition: transform 0.2s ease;
}

.reward-card:hover {
    transform: translateY(-2px);
}

.reward-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
}

.reward-actions {
    display: flex;
    gap: 0.5rem;
}
```

### Category Accordion
```css
.accordion-button:not(.collapsed) {
    background-color: #f8f9fa;
    box-shadow: none;
}

.accordion-item {
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1rem;
}

.accordion-button {
    padding: 1rem;
    font-weight: 500;
}

.accordion-body {
    padding: 1.5rem;
    background-color: white;
}
```

### Reward Badges
```css
.coins-badge {
    background-color: #ffd700;
    color: #000;
    padding: 0.4em 0.6em;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
}

.points-badge {
    background-color: #4CAF50;
    color: white;
    padding: 0.4em 0.6em;
    border-radius: 4px;
}
```

## Toast Notifications

### Toast Container
```css
.toast-container {
    position: fixed;
    top: 1rem;
    right: 1rem;
    z-index: 1050;
}

.toast {
    min-width: 250px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    margin-bottom: 1rem;
}
```

### Toast Variants
```css
.toast.bg-success {
    background-color: #28a745 !important;
}

.toast.bg-danger {
    background-color: #dc3545 !important;
}

.toast.bg-warning {
    background-color: #ffc107 !important;
    color: #000 !important;
}

.toast.bg-info {
    background-color: #17a2b8 !important;
}
```

### Toast Animations
```css
@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.toast.showing {
    animation: slideIn 0.3s ease forwards;
}

.toast.hide {
    animation: slideIn 0.3s ease reverse forwards;
}
```

## Form Components

### Input Groups
```css
.input-group {
    margin-bottom: 1rem;
}

.input-group-text {
    background-color: #f8f9fa;
    border-color: var(--border-color);
}

.form-control-color {
    width: 100%;
    height: 38px;
}
```

### Modal Styles
```css
.modal-content {
    border-radius: 12px;
    overflow: hidden;
}

.modal-header {
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
}

.modal-footer {
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
}
```

## Responsive Design

### Mobile Navigation
```css
@media (max-width: 768px) {
    .sidebar {
        transform: translateX(-100%);
        transition: transform 0.3s ease;
    }
    
    .main-content {
        margin-left: 0;
    }
    
    .sidebar.active {
        transform: translateX(0);
    }
}
```

### Grid Adjustments
```css
@media (max-width: 992px) {
    .dashboard-cards {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 576px) {
    .dashboard-cards {
        grid-template-columns: 1fr;
    }
}
```

## Utility Classes

### Spacing
```css
.mt-4 { margin-top: 1.5rem; }
.mb-4 { margin-bottom: 1.5rem; }
.ms-2 { margin-left: 0.5rem; }
.me-2 { margin-right: 0.5rem; }
```

### Flexbox
```css
.d-flex { display: flex; }
.justify-content-between { justify-content: space-between; }
.align-items-center { align-items: center; }
.flex-column { flex-direction: column; }
```

### Text
```css
.text-muted { color: #6c757d; }
.text-center { text-align: center; }
.font-weight-bold { font-weight: 600; }
```

## Application Styles

### Sidebar Navigation
The sidebar uses a dark theme with hover effects and collapsible sections.

### HTML Structure
```html
<div class="sidebar">
    <div class="sidebar-header">
        <h3>Title</h3>
    </div>
    <ul class="nav flex-column">
        <!-- Menu Items -->
        <li class="nav-item">
            <a class="nav-link collapsed" href="#submenu" 
               data-bs-toggle="collapse" 
               aria-expanded="false">
                <i class="fas fa-icon"></i> Menu Title
                <i class="fas fa-chevron-down float-end"></i>
            </a>
            <div class="collapse" id="submenu">
                <ul class="nav flex-column">
                    <!-- Submenu Items -->
                </ul>
            </div>
        </li>
    </ul>
</div>
```

### CSS Styles
```css
/* Sidebar Container */
.sidebar {
    min-width: 250px;
    max-width: 250px;
    min-height: 100vh;
    background: #343a40;
    color: #fff;
    transition: all 0.3s;
}

/* Navigation Links */
.sidebar .nav-link {
    color: rgba(255, 255, 255, 0.8);
    padding: 10px 20px;
    transition: all 0.3s;
}

.sidebar .nav-link:hover {
    color: #fff;
    background: rgba(255, 255, 255, 0.1);
}

/* Icons */
.sidebar .nav-link i {
    margin-right: 10px;
    width: 20px;
    text-align: center;
}

/* Dropdown Arrow Animation */
.sidebar .nav-link[aria-expanded="true"] .fa-chevron-down {
    transform: rotate(180deg);
}

.sidebar .nav-link .fa-chevron-down {
    transition: transform 0.3s;
}

/* Header */
.sidebar-header {
    padding: 20px;
    background: rgba(0, 0, 0, 0.1);
}

.sidebar-header h3 {
    margin: 0;
    font-size: 1.5rem;
}

/* Submenu */
.sidebar .collapse .nav-link {
    padding-left: 40px;
}

.sidebar .nav-item {
    margin-bottom: 5px;
}

.sidebar .collapse {
    background: rgba(0, 0, 0, 0.1);
}
```

### Features
- Dark theme with light text
- Hover effects on menu items
- Collapsible submenus
- Icon support (FontAwesome)
- Smooth transitions
- Nested navigation structure

### Menu Structure
1. Home
2. Family Section
   - Family Dashboard
   - Members (parent only)
3. Economy Module
   - Chores
   - Rewards
   - Goals
4. Settings (parent only)
5. Logout

### Usage Notes
- Uses Bootstrap 5 classes
- Requires FontAwesome icons
- Supports nested navigation
- Parent-only sections controlled by user role
- Responsive design
- Smooth animations for dropdowns
``` 