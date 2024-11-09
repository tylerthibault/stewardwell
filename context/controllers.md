# Controllers Documentation

## Overview
Each controller is organized as a Flask Blueprint with specific responsibilities and access controls.

## Main Controller (main.py)
```python
Blueprint: main_bp
Routes:
- / (index)
- /dashboard
- /reset-db (dev only)
- /seed-db (dev only)
```

### Dashboard Features
- Family statistics aggregation
- Member activity tracking
- Chore status overview
- Points/coins display

## Auth Controller (auth.py)
```python
Blueprint: auth_bp
Routes:
- /login
- /parent-login
- /child-login
- /register
- /logout
```

### Authentication Features
- Dual login system (parent/child)
- PIN-based child authentication
- Email/password parent auth
- Family code validation

## Family Controller (family.py)
```python
Blueprint: family_bp
Routes:
- /members
- /add-parent
- /add-child
- /edit-child/<id>
- /remove-member/<id>
```

### Family Management
- Member CRUD operations
- PIN management
- Coins/points tracking
- Family code generation

## Chores Controller (chores.py)
```python
Blueprint: chores_bp
Routes:
- / (list)
- /create
- /<id>/complete
- /categories
- /categories/create
- /categories/<id>/edit
- /categories/<id>/delete
```

### Chore Features
- Category management
- Assignment system
- Completion tracking
- Reward distribution

## Rewards Controller (rewards.py)
```python
Blueprint: rewards_bp
Routes:
- / (list)
- /create
- /<id>/redeem
- /<id>/toggle
- /categories
- /categories/create
- /redemption/<id>/<action>
```

### Reward Features
- Category organization
- Availability toggle
- Redemption system
- Approval workflow

## Goals Controller (goals.py)
```python
Blueprint: goals_bp
Routes:
- / (list)
- /create
- /<id>/complete
- /<id>/delete
```

### Goal Features
- Family-wide objectives
- Points tracking
- Completion celebration
- Progress monitoring

## Common Decorators
```python
@login_required
- Ensures authentication
- Redirects to login

@parent_required
- Verifies parent status
- Protects parent routes

@superuser_required
- Checks admin privileges
- Controls system access
```

## Error Handling
```python
try:
    # Database operations
    db.session.commit()
    flash('Success message', 'success')
except Exception as e:
    db.session.rollback()
    flash('Error message', 'danger')
```

## Response Patterns
1. **Success Response**
   ```python
   return redirect(url_for('blueprint.route'))
   ```

2. **Error Response**
   ```python
   flash('Error message', 'danger')
   return redirect(url_for('blueprint.route'))
   ```

3. **API Response**
   ```python
   return jsonify({
       'status': 'success',
       'data': result
   })
   ```

## Access Control
1. **Route Protection**
   ```python
   @login_required
   @parent_required
   def protected_route():
       pass
   ```

2. **Data Validation**
   ```python
   if not all([required_fields]):
       flash('Please provide all required fields.', 'danger')
       return redirect(url_for('blueprint.route'))
   ```

3. **Ownership Verification**
   ```python
   if item.family_id != current_user.family_id:
       flash('Unauthorized access.', 'danger')
       return redirect(url_for('blueprint.route'))
   ```

## Transaction Management
```python
try:
    db.session.add(item)
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

## Future Enhancements
1. **Real-time Updates**
   - WebSocket integration
   - Live notifications
   - Activity feed

2. **Advanced Features**
   - Bulk operations
   - Import/export
   - Reporting system

3. **API Development**
   - REST endpoints
   - Mobile app support
   - Third-party integration

## Goals Controller (goals.py)
- List family goals with categories
- Create new goals and categories
- Complete goals and deduct points
- Delete goals
- Category management (create, edit, delete)

## Chores Controller (chores.py)
- List and manage chores with categories
- Create/edit/delete chores
- Mark chores complete
- Category management
- Clone chores between children

## Rewards Controller (rewards.py)
- List and manage rewards with categories
- Create/edit/delete rewards
- Handle redemptions
- Toggle reward availability
- Category management

## Common Features
- Category Management:
  - Create categories with name, color, icon
  - Edit category details
  - Delete categories (preserves items)
  - JSON API for dynamic creation