# Family Management Documentation

## Overview
The family management system allows parents to manage their family members, including adding and editing children's accounts, and viewing family information.

## Controllers (family.py)
```python
Blueprint: family_bp
Prefix: /family
Routes:
- /members (GET)
- /add-child (POST)
- /edit-child/<int:child_id> (POST)
- /remove-member/<int:member_id> (POST)
```

### Access Control
```python
@parent_required
- Ensures user is a parent
- Redirects to index if not
- Required for all family management routes
```

### Key Features
1. **Member Management**
   - View all family members
   - Add new children
   - Edit child details
   - Remove family members
   - PIN management for children

2. **Data Validation**
   - PIN uniqueness within family
   - Required fields validation
   - Permission checks
   - Error handling

## Templates

### Family Members Page (members.html)
```jinja
Components:
1. Family Header
   - Family name display
   - Member count
   - Action buttons

2. Parents Section
   - Parent list table
   - Basic information display
   - No deletion allowed

3. Children Section
   - Children list table
   - PIN and coins display
   - Edit/Delete actions
   - Add child button

4. Modals
   - Add Child Modal
   - Edit Child Modal
```

### Form Structure
1. **Add Child Form**
```html
- Username input
- PIN input (4 digits)
- Validation messages
- Submit/Cancel buttons
```

2. **Edit Child Form**
```html
- Username field
- PIN field
- Coins field
- Current values pre-filled
- Validation feedback
```

## Data Flow
1. **Adding Child**
   ```
   Parent Action -> Validation -> Create User -> Update Family
   ```

2. **Editing Child**
   ```
   Form Submit -> Validate Changes -> Update User -> Refresh View
   ```

3. **Removing Member**
   ```
   Delete Request -> Verify Permissions -> Remove User -> Update Family
   ```

## Security Measures
1. **Access Control**
   - Parent-only access
   - Family membership verification
   - PIN collision prevention

2. **Data Protection**
   - Transaction management
   - Error handling
   - User feedback

3. **Validation Rules**
   - PIN format (4 digits)
   - Required fields
   - Unique constraints

## UI Components
1. **Tables**
   ```css
   .table {
       background: white;
       border-radius: 8px;
       overflow: hidden;
   }
   ```

2. **Member Cards**
   ```css
   .member-card {
       display: flex;
       align-items: center;
       padding: 1rem;
       background: white;
   }
   ```

3. **Action Buttons**
   ```css
   .btn-group {
       display: flex;
       gap: 0.5rem;
   }
   ```

## Error Handling
1. **User Feedback**
   - Success messages
   - Error notifications
   - Validation feedback
   - Confirmation dialogs

2. **Database Errors**
   - Transaction rollback
   - Error logging
   - User-friendly messages

## Future Enhancements
1. **Member Features**
   - Profile pictures
   - Activity history
   - Achievement badges
   - Role permissions

2. **Family Features**
   - Family settings
   - Notification system
   - Member statistics
   - Group activities 