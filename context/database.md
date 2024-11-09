# Database Schema and Relationships

## Core Models

### User Model
```python
class User(db.Model, UserMixin):
    id: Integer, Primary Key
    username: String(64), Unique
    email: String(120), Unique
    password_hash: String(128)
    pin: String(4)  # For children
    created_at: DateTime
    is_superuser: Boolean
    is_parent: Boolean
    family_id: ForeignKey('family.id')
    parent_id: ForeignKey('user.id')  # Self-referential
    coins: Integer
    family_points: Integer
```

### Family Model
```python
class Family(db.Model):
    id: Integer, Primary Key
    name: String(64)
    family_code: String(6), Unique
    created_at: DateTime
    members: Relationship('User')
    goals: Relationship('FamilyGoal')
    chores: Relationship('Chore')
    rewards: Relationship('Reward')
```

### Chore Model
```python
class Chore(db.Model):
    id: Integer, Primary Key
    title: String(100)
    description: Text
    coins: Integer
    points: Integer
    frequency: String(20)
    due_date: DateTime
    status: String(20)
    category_id: ForeignKey('chore_category.id')
    family_id: ForeignKey('family.id')
    assigned_to_id: ForeignKey('user.id')
    created_by_id: ForeignKey('user.id')
```

### ChoreCategory Model
```python
class ChoreCategory(db.Model):
    id: Integer, Primary Key
    name: String(50)
    color: String(7)
    icon: String(50)
    family_id: ForeignKey('family.id')
    created_by_id: ForeignKey('user.id')
    chores: Relationship('Chore')
```

### Reward Model
```python
class Reward(db.Model):
    id: Integer, Primary Key
    title: String(100)
    description: Text
    cost: Integer
    is_available: Boolean
    category_id: ForeignKey('reward_category.id')
    family_id: ForeignKey('family.id')
    created_by_id: ForeignKey('user.id')
    redemptions: Relationship('RewardRedemption')
```

### RewardCategory Model
```python
class RewardCategory(db.Model):
    id: Integer, Primary Key
    name: String(50)
    color: String(7)
    icon: String(50)
    family_id: ForeignKey('family.id')
    created_by_id: ForeignKey('user.id')
    rewards: Relationship('Reward')
```

### RewardRedemption Model
```python
class RewardRedemption(db.Model):
    id: Integer, Primary Key
    reward_id: ForeignKey('reward.id')
    user_id: ForeignKey('user.id')
    redeemed_at: DateTime
    status: String(20)
    cost: Integer
```

### FamilyGoal Model
```python
class FamilyGoal(db.Model):
    id: Integer, Primary Key
    title: String(100)
    description: Text
    points_required: Integer
    is_completed: Boolean
    family_id: ForeignKey('family.id')
    created_at: DateTime
    completed_at: DateTime
```

## Relationships Overview

### One-to-Many
- Family -> Users
- Family -> Chores
- Family -> Rewards
- Family -> Goals
- User -> CreatedChores
- User -> AssignedChores
- Category -> Chores/Rewards

### Many-to-Many
- Users <-> Rewards (through RewardRedemption)

### Self-Referential
- User -> User (Parent/Child)

## Data Integrity

### Cascading Deletes
```python
# Example configuration
family_id = db.Column(db.Integer, 
    db.ForeignKey('family.id', ondelete='CASCADE'))
```

### Unique Constraints
```python
UniqueConstraint('family_id', 'pin')  # Child PINs
UniqueConstraint('email')  # User emails
UniqueConstraint('family_code')  # Family codes
```

## Status Enums

### Chore Status
```python
CHORE_STATUS = {
    'pending': 'Not started',
    'completed': 'Finished',
    'overdue': 'Past due date'
}
```

### Reward Status
```python
REWARD_STATUS = {
    'pending': 'Awaiting approval',
    'approved': 'Redeemed',
    'denied': 'Rejected'
}
```

## Indexes
```python
Index('idx_user_email', User.email)
Index('idx_family_code', Family.family_code)
Index('idx_chore_status', Chore.status)
Index('idx_reward_availability', Reward.is_available)
```