# Chores Management Documentation

## Overview
The chores system allows parents to create, assign, and track chores for their children, with both individual coin rewards and family point rewards.

## Models

### Chore Model
```python
class Chore(db.Model):
    # Core Fields
    id: Integer, Primary Key
    title: String(100), Required
    description: Text, Optional
    coins: Integer, Default=0      # Individual reward
    points: Integer, Default=0     # Family points
    frequency: String(20)          # daily, weekly, monthly, once
    due_date: DateTime, Optional
    created_at: DateTime, Default=now
    status: String(20), Default='pending'
    completed_at: DateTime, Optional

    # Relationships
    family_id: ForeignKey('family.id')
    assigned_to_id: ForeignKey('user.id')
    created_by_id: ForeignKey('user.id')
```

## Controllers

### Chores Blueprint
```python
Blueprint: chores_bp
Prefix: /chores
Routes:
- / (list_chores)
- /create (create_chore)
- /<int:chore_id>/complete (complete_chore)
```

### Access Control
```python
@login_required
- All chore routes require authentication

@parent_required
- Chore creation
- Chore editing
- Chore deletion
```

## Templates

### List View (list.html)
```jinja
Components:
1. Statistics Cards
   - Pending count
   - Completed count
   - Overdue count

2. Pending Chores Table
   - Title with description tooltip
   - Points/Coins display
   - Assignment info
   - Due date (if set)
   - Complete action

3. Completed Chores Table
   - Title
   - Points earned
   - Completion info
   - Timestamp
```

### Forms

1. **Create Chore Form**
```html
Required Fields:
- Title
- Coins reward
- Points reward
- Frequency
- Assigned to

Optional Fields:
- Description
- Due date (with toggle)
```

## Reward System

### Individual Rewards
- Coins awarded to child upon completion
- Tracked in user.coins
- Used for personal rewards

### Family Rewards
- Points awarded to all family members
- Tracked in user.family_points
- Used for family goals

## Status Management
1. **Pending**
   - Default state
   - Awaiting completion
   - Can be completed by assigned child or parent

2. **Completed**
   - Marked when finished
   - Triggers reward distribution
   - Stores completion timestamp

3. **Overdue**
   - Past due date
   - Visual indicators
   - Still completable

## Future Enhancements
1. **Recurring Chores**
   - Automatic recreation
   - Pattern-based scheduling
   - History tracking

2. **Verification System**
   - Parent approval option
   - Photo evidence
   - Completion criteria

3. **Analytics**
   - Completion rates
   - Time tracking
   - Reward statistics