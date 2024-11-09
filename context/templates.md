# Templates Documentation

## Layout Structure
1. **Base Template (base.html)**
   ```jinja
   - Common head elements
   - Navigation includes
   - Flash messages
   - Content blocks
   - Common scripts
   ```

2. **Dashboard Template (dashboard.html)**
   ```jinja
   Components:
   - Family header with name
   - Statistics cards (members, chores, points)
   - Member cards with chores
   - Activity feed (future)
   ```

3. **Chores Templates**
   ```jinja
   list.html:
   - Chore statistics
   - Pending chores table
   - Completed chores table
   - Add chore modal
   
   categories.html:
   - Category cards
   - Category management
   - Edit/delete modals
   ```

## Component Structure

### Dashboard Components
1. **Member Card with Chores**
   ```jinja
   <div class="member-card-with-chores">
       <div class="member-header">
           <div class="member-avatar">{{ initials }}</div>
           <div class="member-info">
               <h4>{{ username }}</h4>
               <p>{{ coins }} coins</p>
           </div>
       </div>
       <div class="member-chores">
           {% for chore in pending_chores %}
               <div class="chore-item">...</div>
           {% endfor %}
       </div>
   </div>
   ```

2. **Chore Item**
   ```jinja
   <div class="chore-item">
       <div class="chore-info">
           <span class="chore-title">{{ title }}</span>
           <div class="chore-rewards">
               <span class="coins-badge">{{ coins }}</span>
               <span class="points-badge">{{ points }}</span>
           </div>
       </div>
       <div class="chore-due-date">{{ due_date }}</div>
   </div>
   ```

### Chore Management Components
1. **Add Chore Form**
   ```jinja
   <form action="{{ url_for('chores.create_chore') }}" method="POST">
       - Title input
       - Description textarea
       - Coins/Points inputs
       - Category select/create
       - Frequency select
       - Due date toggle
       - Assign to select
   </form>
   ```

2. **Category Management**
   ```jinja
   <div class="category-card">
       - Category header with icon
       - Color indicator
       - Chore count
       - Edit/Delete actions
   </div>
   ```

## Template Inheritance
```jinja
base.html
├── authenticated_content block
│   ├── dashboard.html
│   ├── chores/list.html
│   └── chores/categories.html
└── content block
    └── auth templates
```

## Common Components
1. **Statistics Cards**
   ```jinja
   <div class="dashboard-cards">
       <div class="card">
           <h3>{{ title }}</h3>
           <div class="stat">{{ value }}</div>
           <p>{{ description }}</p>
       </div>
   </div>
   ```

2. **Action Buttons**
   ```jinja
   <div class="btn-group">
       <button class="btn btn-primary">
           <i class="fas {{ icon }}"></i> {{ text }}
       </button>
   </div>
   ```

## Modal Patterns
1. **Add/Edit Forms**
   ```jinja
   <div class="modal fade" id="modalId">
       <div class="modal-dialog">
           <div class="modal-content">
               <div class="modal-header">...</div>
               <div class="modal-body">
                   <form>...</form>
               </div>
           </div>
       </div>
   </div>
   ```

2. **Confirmation Dialogs**
   ```jinja
   <div class="modal fade" id="confirmModal">
       <div class="modal-dialog">
           <div class="modal-content">
               <div class="modal-body">
                   <p>{{ confirmation_message }}</p>
               </div>
               <div class="modal-footer">
                   <form method="POST">...</form>
               </div>
           </div>
       </div>
   </div>
   ```

## JavaScript Integration
1. **Form Handlers**
   ```javascript
   document.querySelector('form').addEventListener('submit', async (e) => {
       e.preventDefault();
       // Form submission logic
   });
   ```

2. **Dynamic UI Updates**
   ```javascript
   document.getElementById('toggle').addEventListener('change', function() {
       // Toggle visibility logic
   });
   ```

## Future Enhancements
1. **Real-time Updates**
   - WebSocket integration
   - Live chore completion
   - Instant notifications

2. **Enhanced Interactivity**
   - Drag-and-drop chores
   - Interactive rewards
   - Progress animations