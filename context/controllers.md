# Controllers Documentation

## Structure
Each controller is organized as a Flask Blueprint with specific responsibilities:

## Main Controller (main.py)
```python
Blueprint: main_bp
Prefix: /
Routes:
- / (index)
- /dashboard
- /reset-db (development only)
```

### Key Features
- Landing page rendering
- Dashboard data aggregation
- Database management tools
- Protected routes with @login_required

## Auth Controller (auth.py)
```python
Blueprint: auth_bp
Prefix: None
Routes:
- /login
- /parent-login
- /child-login
- /register
- /logout
```

### Key Features
- User registration
- Parent authentication
- Child PIN authentication
- Session management
- Form validation

## Admin Controller (admin.py)
```python
Blueprint: admin_bp
Prefix: /admin
Routes:
- /users
- /users/<int:user_id>/toggle-superuser
```

### Key Features
- User management interface
- Superuser controls
- Protected with @superuser_required
- User role management

## Family Controller (family.py)
```python
Blueprint: family_bp
Prefix: /family
Routes:
- /members (GET)
- /add-parent (POST)
- /add-child (POST)
- /edit-child/<int:child_id> (POST)
- /remove-member/<int:member_id> (POST)
```

### Key Features
- Family member management
- Child account creation and editing
- Parent account creation
- Member removal
- PIN management
- Coins management
- Protected with @parent_required

### Child Management
1. **Adding Children**
   - Username validation
   - PIN generation (4 digits)
   - Family association
   - Initial coin balance
   - Parent relationship

2. **Editing Children**
   - Update username
   - Change PIN
   - Modify coin balance
   - PIN collision prevention within family

3. **Removing Members**
   - Safety checks
   - Parent protection
   - Cascade deletion
   - Family integrity maintenance

### Parent Management
1. **Adding Parents**
   - Email validation
   - Password hashing
   - Family association
   - Role assignment

2. **Parent Privileges**
   - Member management
   - Child account control
   - Family settings access
   - PIN management

### Data Validation
1. **PIN Validation**
   - 4-digit requirement
   - Numeric only
   - Family-scoped uniqueness
   - Collision prevention

2. **User Validation**
   - Username uniqueness
   - Email format
   - Password requirements
   - Role verification

### Security Measures
1. **Access Control**
   - Parent-only routes
   - Family membership verification
   - Child protection
   - Data isolation

2. **Error Handling**
   - Transaction management
   - Rollback on failure
   - User feedback
   - Logging

## Custom Decorators
```python
@login_required
- Ensures user is authenticated
- Redirects to login page if not

@superuser_required
- Ensures user is superuser
- Redirects to index if not
- Requires authentication

@parent_required
- Ensures user is a parent
- Redirects to index if not
- Requires authentication
```

## Error Handling
- Flash messages for user feedback
- Database transaction management
- Exception handling
- Logging for debugging

## Future Controllers
1. Chores Controller
   - Chore creation
   - Assignment
   - Completion tracking
   - Reward distribution

2. Rewards Controller
   - Reward creation
   - Point management
   - Redemption system
   - Inventory tracking

3. Goals Controller
   - Family goal setting
   - Progress tracking
   - Achievement system
   - Celebration events 

## Settings Controller (settings.py)
```python
Blueprint: settings_bp
Prefix: /settings
Routes:
- / (profile)
- /join-family
- /pending-requests
- /handle-request/<int:request_id>/<string:action>
```

### Key Features
- Profile management
- Password changes
- Family joining system
- Join request handling
- Parent approval system

### Access Control
- Profile: @login_required
- Join Family: @login_required
- Pending Requests: @login_required + @parent_required
- Handle Request: @login_required + @parent_required

### Request Flow
1. User submits join request with family code
2. Parent receives notification in pending requests
3. Parent can accept or reject request
4. On acceptance, user is added to family

## Chores Controller (chores.py)
```python
Blueprint: chores_bp
Prefix: /chores
Routes:
- / (list_chores)
- /create (create_chore)
- /<int:chore_id>/complete (complete_chore)
```

### Key Features
- Chore creation and assignment
- Completion tracking
- Reward distribution
- Due date management
- Parent/Child specific views

### Access Control
- List: @login_required
- Create: @login_required + @parent_required
- Complete: @login_required (with ownership check)

### Data Flow
1. **Chore Creation**
   ```
   Parent Action -> Validation -> Create Chore -> Assign to Child
   ```

2. **Chore Completion**
   ```
   Child Action -> Verify Assignment -> Mark Complete -> Award Rewards
   ```

3. **Reward Distribution**
   ```
   Complete Chore -> Award Coins to Child -> Award Points to Family
   ```