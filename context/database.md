# Database Schema and Relationships

## Entity Relationship Diagram
```
User
├── has_one Family (through family_id)
├── has_many Children (self-referential through parent_id)
├── has_one Parent (self-referential through parent_id)
├── has_many FamilyGoals (through Family)
├── has_many AssignedChores (as assigned_to)
└── has_many CreatedChores (as created_by)

Family
├── has_many Users (members)
├── has_many FamilyGoals
└── has_many Chores

Chore
├── belongs_to Family
├── belongs_to AssignedUser (User)
└── belongs_to CreatedByUser (User)

FamilyGoal
└── belongs_to Family
```

## Table Relationships

### User -> Family
- One-to-Many relationship
- User.family_id -> Family.id
- Bidirectional relationship through `family` backref

### User -> User (Parent/Child)
- Self-referential relationship
- User.parent_id -> User.id
- Parent has many children
- Child belongs to one parent

### Family -> FamilyGoal
- One-to-Many relationship
- FamilyGoal.family_id -> Family.id
- Lazy loading enabled for goals

### Family -> Chore
- One-to-Many relationship
- Chore.family_id -> Family.id
- Lazy loading enabled for chores

### User -> Chore
- Two relationships:
  1. Assigned chores (assigned_to)
  2. Created chores (created_by)
- Both are One-to-Many

## Indexes
- User.username (unique)
- User.email (unique)
- User.pin (unique within family)
- Family.name
- Family.family_code (unique)

## Constraints
- User.username: required, unique
- User.email: required, unique
- User.password_hash: required
- User.pin: optional
- Family.name: required
- Family.family_code: required, unique
- FamilyGoal.title: required
- FamilyGoal.family_id: required
- Chore.title: required
- Chore.family_id: required
- Chore.created_by_id: required

## Status Fields
1. **Chore Status**
   ```python
   status_types = {
       'pending': 'Awaiting completion',
       'completed': 'Successfully finished',
       'overdue': 'Past due date'
   }
   ```

2. **Join Request Status**
   ```python
   status_types = {
       'pending': 'Awaiting response',
       'accepted': 'Request approved',
       'rejected': 'Request denied'
   }
   ```

## Future Tables
1. **ChoreCompletion**
   - Belongs to Chore
   - Belongs to User
   - Has timestamp
   - Has verification status

2. **Rewards**
   - Belongs to Family
   - Has cost
   - Has inventory

3. **Transactions**
   - Belongs to User
   - Polymorphic (Chore/Reward)
   - Has amount