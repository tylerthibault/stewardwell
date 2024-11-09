# Database Models

## User
- Primary user model for authentication and profile
- Fields: username, email, password_hash, pin, is_parent, is_superuser
- Relationships: family, children, created_chores, created_rewards, created_goals, created_goal_categories

## Family
- Groups users together as a family unit
- Fields: name, family_code
- Relationships: members, chores, rewards, goals, goal_categories

## ChoreCategory
- Organizes chores into groups
- Fields: name, color (hex), icon (FontAwesome)
- Relationships: chores, family, created_by

## Chore
- Represents tasks assigned to children
- Fields: title, description, coins, points, frequency, due_date, status
- Relationships: category, family, assigned_to, created_by

## RewardCategory
- Organizes rewards into groups
- Fields: name, color (hex), icon (FontAwesome)
- Relationships: rewards, family, created_by

## Reward
- Represents items/privileges children can purchase
- Fields: title, description, cost, is_available
- Relationships: category, family, created_by, redemptions

## RewardRedemption
- Tracks reward purchases and approvals
- Fields: status, cost, redeemed_at
- Relationships: reward, user

## GoalCategory
- Organizes family goals into groups
- Fields: name, color (hex), icon (FontAwesome)
- Relationships: goals, family, created_by

## Goal
- Represents family achievements to work toward
- Fields: title, description, points_required, is_completed
- Relationships: category, family, created_by

## FamilyJoinRequest
- Manages family membership requests
- Fields: status, created_at, resolved_at
- Relationships: user, family