# StewardWell - Family Management System

## Project Overview
StewardWell is a family management application designed to help parents create a reward-based system for their children. The system uses a dual-currency approach:
- Individual coins for children
- Family points for collective goals

## Core Features

### 1. User Management
- Three user types: Superuser, Parent, Child
- Family-based organization
- PIN-based login for children
- Email/password login for parents

### 2. Chore System
- Create and assign chores
- Category organization
- Due date tracking
- Dual rewards (coins + points)
- Completion verification

### 3. Reward System
- Individual rewards for children
- Category-based organization
- Availability toggle
- Redemption approval process
- Cost management in coins

### 4. Family Goals
- Shared family objectives
- Points-based progress tracking
- Collective achievement system
- Completion celebration

## Technical Stack
- Framework: Flask 2.3.3
- Database: SQLite with SQLAlchemy 2.0.21
- Authentication: Flask-Login 0.6.3
- Forms: Flask-WTF 1.2.1
- Password Security: Flask-Bcrypt 1.0.1

## Design Philosophy
- Clean, minimalist interface
- Mobile-responsive design
- Role-based access control
- Family-centric organization
- Gamification elements

## Project Structure
```
app/
├── models/
│   └── user.py (All models)
├── controllers/
│   ├── admin.py
│   ├── auth.py
│   ├── chores.py
│   ├── family.py
│   ├── goals.py
│   ├── main.py
│   ├── rewards.py
│   └── settings.py
├── templates/
│   ├── admin/
│   ├── auth/
│   ├── chores/
│   ├── family/
│   ├── goals/
│   ├── main/
│   ├── rewards/
│   └── settings/
└── static/
    ├── css/
    └── js/
```

## Key Concepts

### Family Structure
- Each family has a unique code
- Multiple parents possible
- Children use PIN authentication
- Shared family points
- Individual coin wallets

### Reward System
- Chores award both coins and points
- Coins are individual currency
- Points contribute to family goals
- Rewards cost coins to redeem
- Parents approve redemptions

### Categories
Both chores and rewards use categories for organization:
- Custom colors and icons
- Family-specific categories
- Dynamic category creation
- Category management

## Future Enhancements
1. Real-time notifications
2. Achievement system
3. Statistics and reporting
4. Mobile application
5. Multiple family support 