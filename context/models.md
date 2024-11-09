# Models Documentation

## Base Model Mixins and Utilities
```python
UserMixin
- Provides authentication properties
- Required by Flask-Login
- Implements is_authenticated, is_active, etc.
```

## User Model
```python
class User(db.Model, UserMixin):
    # Core Fields
    id: Integer, Primary Key
    username: String(64), Unique, Required
    email: String(120), Unique, Required
    password_hash: String(128), Required
    pin: String(4), Unique, Optional
    created_at: DateTime, Default=now

    # Flags
    is_superuser: Boolean, Default=False
    is_parent: Boolean, Default=False

    # Relationships
    family_id: ForeignKey('family.id')
    parent_id: ForeignKey('user.id')
    children: Relationship('User')

    # Virtual Wallet
    coins: Integer, Default=0
    family_points: Integer, Default=0

## User Model Details

### Authentication Fields
```python
username: String(64)
- Unique across system
- Required for all users
- Used for display and login

email: String(120)
- Unique across system
- Required for parents
- Auto-generated for children

password_hash: String(128)
- BCrypt hashed
- Required for parents
- Generated for children

pin: String(4)
- Optional, used for children
- Must be numeric
- Unique within family
```

### Role Fields
```python
is_superuser: Boolean
- System administration access
- Can manage all families
- Can reset database

is_parent: Boolean
- Family management access
- Can add/remove members
- Can manage children
```

### Relationship Fields
```python
family_id: Integer
- Foreign key to Family
- Nullable for users without family
- Required for active members

parent_id: Integer
- Self-referential to User
- Used for parent-child relationship
- Nullable for parents
```

### Virtual Wallet Fields
```python
coins: Integer
- Individual reward currency
- Used by children
- Earned through chores

family_points: Integer
- Family-wide achievement points
- Shared among family members
- Used for family goals
```

## Family Model
```python
class Family(db.Model):
    # Core Fields
    id: Integer, Primary Key
    name: String(64), Required
    created_at: DateTime, Default=now

    # Relationships
    members: Relationship('User')
    goals: Relationship('FamilyGoal')

## Family Model Details

### Core Fields
```python
name: String(64)
- Family display name
- Required
- Used in UI

family_code: String(6)
- Unique identifier
- Auto-generated
- Used for child login
```

### Relationships
```python
members: List[User]
- All family members
- Includes parents and children
- Bidirectional relationship

goals: List[FamilyGoal]
- Family objectives
- Shared among members
- Progress tracking
```

### Methods
```python
generate_family_code()
- Creates unique 6-character code
- Uses uppercase letters and numbers
- Ensures uniqueness
```

## FamilyGoal Model
```python
class FamilyGoal(db.Model):
    # Core Fields
    id: Integer, Primary Key
    title: String(100), Required
    description: Text
    points_required: Integer, Default=0
    is_completed: Boolean, Default=False
    created_at: DateTime, Default=now
    completed_at: DateTime, Nullable

    # Relationships
    family_id: ForeignKey('family.id')
```

## Join Request Model
```python
class FamilyJoinRequest(db.Model):
    # Core Fields
    id: Integer, Primary Key
    user_id: ForeignKey('user.id')
    family_id: ForeignKey('family.id')
    status: String(20), Default='pending'
    created_at: DateTime, Default=now
    resolved_at: DateTime, Nullable

    # Relationships
    user: Relationship('User', backref='join_requests')
    family: Relationship('Family', backref='join_requests')
```

## Join Request Model Details

### Status Management
```python
status: String(20)
- pending: Initial state
- accepted: Request approved
- rejected: Request denied
```

### Timestamps
```python
created_at: DateTime
- Request creation time
- Auto-set on creation

resolved_at: DateTime
- Resolution timestamp
- Set on accept/reject
```

### Validation Rules
1. **User Constraints**
   - One pending request per family
   - Cannot request current family
   - Must be authenticated

2. **Family Constraints**
   - Must exist
   - Must be active
   - Must have parent

3. **Status Transitions**
   - pending -> accepted
   - pending -> rejected
   - No other transitions allowed

## Future Models

### Chore Model
```python
class Chore(db.Model):
    # Core Fields
    id: Integer, Primary Key
    title: String(100), Required
    description: Text, Optional
    coins: Integer, Default=0
    points: Integer, Default=0
    frequency: String(20)
    due_date: DateTime, Optional
    status: String(20), Default='pending'
    completed_at: DateTime, Optional

    # Relationships
    family_id: ForeignKey('family.id')
    assigned_to_id: ForeignKey('user.id')
    created_by_id: ForeignKey('user.id')

    # Relationship definitions
    assigned_to: Relationship('User')
    created_by: Relationship('User')
    family: Relationship('Family')
```

### Chore Status Types
```python
status_types = {
    'pending': 'Awaiting completion',
    'completed': 'Successfully finished',
    'overdue': 'Past due date'
}
```

### Frequency Options
```python
frequency_types = {
    'once': 'One-time task',
    'daily': 'Repeats daily',
    'weekly': 'Repeats weekly',
    'monthly': 'Repeats monthly'
}
```

### ChoreCompletion Model
```python
class ChoreCompletion(db.Model):
    id: Integer, Primary Key
    chore_id: ForeignKey('chore.id')
    user_id: ForeignKey('user.id')
    completed_at: DateTime
    points_earned: Integer
```

### Reward Model
```python
class Reward(db.Model):
    id: Integer, Primary Key
    title: String(100)
    description: Text
    cost: Integer
    family_id: ForeignKey('family.id')
    inventory: Integer
```

### Transaction Model
```python
class Transaction(db.Model):
    id: Integer, Primary Key
    user_id: ForeignKey('user.id')
    amount: Integer
    type: String  # chore, reward
    reference_id: Integer  # chore_id or reward_id
    created_at: DateTime
``` 