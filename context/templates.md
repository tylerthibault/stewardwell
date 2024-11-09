# Templates Documentation

## Directory Structure
```
app/templates/
├── base.html                # Base template with common structure
├── partials/               # Reusable template parts
│   ├── _navbar.html        # Top navigation for non-auth users
│   ├── _sidebar.html       # Side navigation for auth users
│   └── _flash_messages.html # Flash message display
├── auth/                   # Authentication templates
│   ├── login.html          # Main login options
│   ├── parent_login.html   # Parent-specific login
│   ├── child_login.html    # Child PIN login
│   └── register.html       # Registration form
└── main/                   # Main application templates
    ├── index.html          # Landing page
    ├── dashboard.html      # User dashboard
    └── reset_db.html       # Database reset (dev only)
```

## Template Inheritance
1. **Base Template (base.html)**
   ```jinja
   {% block title %}{% endblock %}
   {% if current_user.is_authenticated %}
       {% block authenticated_content %}{% endblock %}
   {% else %}
       {% block content %}{% endblock %}
   {% endif %}
   ```

2. **Authenticated Pages**
   ```jinja
   {% extends "base.html" %}
   {% block authenticated_content %}
   <!-- Content for logged-in users -->
   {% endblock %}
   ```

3. **Public Pages**
   ```jinja
   {% extends "base.html" %}
   {% block content %}
   <!-- Content for non-authenticated users -->
   {% endblock %}
   ```

## Partial Templates
1. **Navbar (_navbar.html)**
   - Logo/Brand
   - Login/Register links
   - Responsive toggle

2. **Sidebar (_sidebar.html)**
   - User welcome
   - Role-based navigation
   - Logout option

3. **Flash Messages (_flash_messages.html)**
   - Success/Error messages
   - Dismissible alerts

## Common Components
1. **Forms**
   ```jinja
   {{ form.hidden_tag() }}
   {{ form.field.label }}
   {{ form.field(class="form-control") }}
   {% if form.field.errors %}
       {% for error in form.field.errors %}
           <span class="text-danger">{{ error }}</span>
       {% endfor %}
   {% endif %}
   ```

2. **Cards**
   ```jinja
   <div class="card">
       <div class="card-header">
           <h3>{{ title }}</h3>
       </div>
       <div class="card-body">
           {{ content }}
       </div>
   </div>
   ```

3. **Member Display**
   ```jinja
   <div class="member-card">
       <div class="member-avatar">{{ member.username[:2].upper() }}</div>
       <div class="member-info">
           <h4>{{ member.username }}</h4>
           <p>{{ member.role }}</p>
       </div>
   </div>
   ```

## Template Variables
1. **User Information**
   - current_user.username
   - current_user.is_parent
   - current_user.is_superuser
   - current_user.family

2. **Flash Messages**
   - category (success, danger, info)
   - message content

3. **Form Data**
   - form.errors
   - form.field.data
   - form.validate_on_submit()

## JavaScript Integration
1. **Form Validation**
   ```javascript
   document.getElementById('form-id').addEventListener('submit', function(e) {
       // Validation logic
   });
   ```

2. **Dynamic UI**
   ```javascript
   document.getElementById('toggle-id').addEventListener('change', function() {
       // UI update logic
   });
   ```

## Future Templates
1. **Chores Management**
   - chores/list.html
   - chores/create.html
   - chores/edit.html

2. **Rewards System**
   - rewards/store.html
   - rewards/inventory.html
   - rewards/redeem.html

3. **Family Goals**
   - goals/list.html
   - goals/create.html
   - goals/progress.html 

## Settings Templates
1. **Profile Settings (profile.html)**
   ```jinja
   - Username update form
   - Email update form
   - Password change form
   - Family code display (for parents)
   ```

2. **Join Family (join_family.html)**
   ```jinja
   - Family code input
   - Submit request button
   - Form validation
   - Error messages
   ```

3. **Pending Requests (pending_requests.html)**
   ```jinja
   - Request list table
   - Accept/Reject buttons
   - User information display
   - Timestamp information
   ```

## Template Components
[Previous components remain...]

4. **Join Request Display**
   ```jinja
   <div class="request-item">
       <div class="user-info">{{ request.user.username }}</div>
       <div class="timestamp">{{ request.created_at }}</div>
       <div class="actions">
           <button>Accept</button>
           <button>Reject</button>
       </div>
   </div>
   ```

## Navigation Updates
1. **Sidebar Conditions**
   ```jinja
   {% if not current_user.family %}
       <a href="{{ url_for('settings.join_family') }}">Join Family</a>
   {% endif %}
   
   {% if current_user.is_parent %}
       <a href="{{ url_for('settings.pending_requests') }}">Join Requests</a>
   {% endif %}
   ```