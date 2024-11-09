# Database Structure

## Core Tables
- users
- families
- family_join_requests

## Chores System
- chore_categories
- chores

## Rewards System
- reward_categories
- rewards
- reward_redemptions

## Goals System
- goal_categories
- goals

## Key Relationships
1. Family-based organization:
   - All categories (chores, rewards, goals) belong to a family
   - All items (chores, rewards, goals) belong to a family
   - Users belong to one family

2. Category relationships:
   - Chores can belong to a chore category
   - Rewards can belong to a reward category
   - Goals can belong to a goal category
   - Categories track who created them

3. User relationships:
   - Parents can create categories and items
   - Children can complete chores and redeem rewards
   - Family points contribute to goals