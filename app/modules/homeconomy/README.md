# Homeconomy Module

The Homeconomy module is a comprehensive chore management system designed for families. It allows parents to create and manage chores, rewards, and family goals while enabling children to earn coins and contribute to family goals through completing tasks.

## Features

### For Parents
- Create and manage family chores
- Set coin and point rewards for chores
- Create rewards that children can purchase with coins
- Set family goals that require collective points
- Verify completed chores
- Monitor children's progress and earnings
- Manage reward fulfillment

### For Children
- View available chores
- Mark chores as completed
- Earn coins (individual) and points (family)
- Purchase rewards with earned coins
- Track progress towards family goals

## Core Components

### Chores
- Name and description
- Coin reward (individual)
- Point reward (family contribution)
- Frequency (daily, weekly, monthly, one-time)
- Assignment capability
- Verification system

### Rewards
- Name and description
- Coin cost
- Quantity management
- Fulfillment tracking

### Goals
- Family-wide objectives
- Point requirements
- Achievement tracking
- Progress monitoring

### Economy System
- Individual coin tracking
- Family point pooling
- Reward store
- Goal achievement system

## Database Schema

### Chore
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- coins_reward: Integer
- points_reward: Integer
- frequency: String
- created_at: DateTime
- is_active: Boolean
- family_id: Integer (Foreign Key)
- assigned_to: Integer (Foreign Key)
```

### CompletedChore
```python
- id: Integer (Primary Key)
- completed_at: DateTime
- verified: Boolean
- verified_at: DateTime
- verified_by_id: Integer (Foreign Key)
- chore_id: Integer (Foreign Key)
- child_id: Integer (Foreign Key)
```

### Reward
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- coin_cost: Integer
- quantity: Integer
- created_at: DateTime
- is_active: Boolean
- family_id: Integer (Foreign Key)
```

### ClaimedReward
```python
- id: Integer (Primary Key)
- claimed_at: DateTime
- fulfilled: Boolean
- fulfilled_at: DateTime
- fulfilled_by_id: Integer (Foreign Key)
- reward_id: Integer (Foreign Key)
- child_id: Integer (Foreign Key)
```

### Goal
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- points_required: Integer
- created_at: DateTime
- achieved_at: DateTime
- is_active: Boolean
- family_id: Integer (Foreign Key)
```

## Usage

### Parent Interface
```python
# Create a new chore
chore = Chore(
    name="Clean Room",
    description="Make bed, pick up toys, vacuum",
    coins_reward=50,
    points_reward=100,
    frequency="daily",
    family_id=family.id
)

# Create a reward
reward = Reward(
    name="Movie Night",
    description="Choose a movie for family movie night",
    coin_cost=200,
    family_id=family.id
)

# Create a family goal
goal = Goal(
    name="Family Vacation",
    description="Earn points for our summer vacation",
    points_required=5000,
    family_id=family.id
)
```

### Child Interface
```python
# Complete a chore
completed_chore = CompletedChore(
    chore_id=chore.id,
    child_id=child.id
)

# Claim a reward
claimed_reward = ClaimedReward(
    reward_id=reward.id,
    child_id=child.id
)
```

## Integration

The Homeconomy module integrates with the main StewardWell application through:
1. User authentication and authorization
2. Family management system
3. Parent-child relationships
4. Points and coins economy

## Future Enhancements
- Chore scheduling system
- Recurring chores automation
- Achievement badges
- Progress statistics and reports
- Mobile app integration
- Notification system
