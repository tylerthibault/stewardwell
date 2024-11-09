# Flask MVC Application Context

## Project Overview
A home economy management tool designed to help parents create a reward-based system for their children. The application allows families to track chores, manage rewards, and work towards family goals.

## Design System
### Colors
- Primary: #4169E1 (Royal Blue)
- Secondary: #4CAF50 (Green)
- Background: #f8f9fa (Light Gray)
- Text: #333333 (Dark Gray)
- Border: #e0e0e0 (Light Gray)

### Typography
- Primary Font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif
- Base Font Size: 16px
- Line Height: 1.6

### Components
1. **Buttons**
   - Padding: 0.75rem 1.5rem
   - Border Radius: 6px
   - Font Size: 0.95rem
   - Transition: transform 0.2s ease
   - Hover Effect: translateY(-1px) + opacity 0.95

2. **Cards**
   - Background: white
   - Border Radius: 8px-12px
   - Box Shadow: 0 2px 4px rgba(0,0,0,0.05)
   - Padding: 1.5rem-2rem

3. **Forms**
   - Max Width: 400px
   - Input Padding: 0.75rem
   - Border Radius: 6px
   - Focus State: Primary color outline

4. **Navigation**
   - Background: white
   - Box Shadow: 0 2px 4px rgba(0,0,0,0.05)
   - Font Weight: 600 (brand)
   - Link Color: #666666

5. **Dashboard Layout**
   - Container Max Width: 1200px
   - Three-column Statistics Grid
   - Two-section Layout (Stats + Activity)
   - Responsive Grid System

6. **Dashboard Cards**
   - Background: white
   - Border Radius: 12px
   - Box Shadow: var(--shadow)
   - Padding: 1.5rem
   - Stat Size: 2.5rem
   - Stat Color: var(--primary-color)

7. **Member Cards**
   - Display: flex
   - Avatar Size: 40px
   - Avatar Background: var(--primary-color)
   - Border Radius: 12px
   - Padding: 1rem
   - Info Layout: vertical stack

8. **Activity Feed**
   - Vertical List Layout
   - Item Padding: 15px
   - Time Display: right-aligned
   - Avatar Size: 30px
   - Background: white

9. **No-Family Message**
   - Centered Layout
   - Max Width: 500px
   - Padding: 2rem
   - Background: white
   - Border Radius: 12px

### Layout
- Container Max Width: 1200px
- Grid System: CSS Grid with auto-fit
- Spacing Scale: 0.75rem, 1rem, 1.5rem, 2rem, 4rem

## Project Structure
project_root/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── forms/
│   │   └── auth.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   ���   └── main.py
│   ├── templates/
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── parent_login.html
│   │   │   ├── child_login.html
│   │   │   └── register.html
│   │   ├── main/
│   │   │   └── index.html
│   │   └── base.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
├── config.py
├── requirements.txt
└── server.py

## Technical Stack
- **Framework**: Flask 2.3.3
- **Database**: SQLite with SQLAlchemy 2.0.21
- **ORM**: Flask-SQLAlchemy 3.1.1
- **Authentication**: Flask-Login 0.6.3
- **Forms**: Flask-WTF 1.2.1
- **Password Hashing**: Flask-Bcrypt 1.0.1
- **Email Validation**: email-validator 2.1.0.post1

## Core Features
1. User Authentication System
   - Registration for parents and children
   - Login/Logout functionality
   - Password hashing for security

2. User Types
   - Superuser (admin)
   - Parents
   - Children

3. Family System
   - Family groups
   - Parent-child relationships
   - Family points system

4. Economy System
   - Individual coin wallet for children
   - Family points for group goals
   - Reward system (pending implementation)
   - Chore management (pending implementation)

## Database Models
1. User Model
   - Basic authentication fields
   - User type flags
   - Family relationships
   - Virtual wallet (coins and family points)

2. Family Model
   - Family grouping
   - Relationship with members
   - Family goals tracking

## Planned Features
- Chore management system
- Reward store
- Family goals system
- Achievement tracking
- Point/coin transaction history

## Security Considerations
- Password hashing implemented
- User session management
- Protected routes with login_required

## Design Principles
1. **Minimalist and Clean**
   - Use white space effectively
   - Keep UI elements subtle
   - Focus on content hierarchy

2. **Consistent Spacing**
   - Maintain consistent padding and margins
   - Use defined spacing scale
   - Keep components aligned

3. **Responsive Design**
   - Mobile-first approach
   - Flexible grid system
   - Breakpoint at 768px for major layout changes

4. **Visual Feedback**
   - Subtle hover effects
   - Clear active states
   - Visible focus indicators

5. **Accessibility**
   - High contrast text
   - Adequate text size
   - Clear visual hierarchy

## Command Line Interface
1. **Superuser Creation**
   - Command: `flask create-superuser`
   - Creates an admin user with superuser privileges
   - Automatically creates associated family
   - Required fields:
     * Username
     * Email
     * Password

## User Hierarchy and Access Control
1. **Superuser (Admin)**
   - Full system access
   - User management capabilities
   - Database management access
   - Family management across system
   - Access to admin-specific sidebar menu
   - Special admin controls:
     * Reset Database
     * Manage All Users
     * Manage All Families

2. **Parent**
   - Family management
   - Chore creation and assignment
   - Reward management
   - Family goal setting
   - Child account management
   - Access to parent-specific sidebar menu

3. **Child**
   - Limited feature access
   - Chore completion
   - Reward redemption
   - Point/coin balance viewing
   - Access to child-specific sidebar menu

## Navigation Structure
1. **Sidebar Navigation**
   - Conditional rendering based on user type
   - Distinct sections for different user roles
   - Visual hierarchy through dividers
   - Special styling for admin functions
   
2. **Admin Menu Items**
   - User Management (gold icon)
   - Family Management (gold icon)
   - Database Reset (red warning icon)
   - Separated by dividers

3. **Parent Menu Items**
   - Family Members
   - Manage Chores
   - Rewards
   - Family Goals

4. **Child Menu Items**
   - My Chores
   - My Rewards
   - Family Goals

5. **Common Menu Items**
   - Dashboard
   - Settings
   - Logout

## Visual Hierarchy
1. **Menu Styling**
   - Background: #2C3E7B (Dark Blue)
   - Text: White with opacity variations
   - Icons: 20px width, consistent spacing
   - Hover effects: Light overlay
   - Active state: Left border indicator

2. **Admin Indicators**
   - Gold icons for admin functions
   - Red warning icons for dangerous actions
   - Section labels in uppercase
   - Dividers for visual separation

3. **Layout Structure**
   - Fixed sidebar width: 250px
   - Full height sidebar
   - Main content margin-left: 250px
   - Responsive adjustments

## Security Implementation
1. **Access Control**
   - Route protection with @login_required
   - Role-based menu visibility
   - Superuser flag checking
   - Parent/Child status verification

2. **Database Security**
   - Password hashing with bcrypt
   - Session management
   - Safe database operations
   - Error handling and logging

## Additional Style Considerations
1. **Admin-Specific Styles**
   ```css
   .menu-label {
       color: rgba(255, 255, 255, 0.5);
       text-transform: uppercase;
       letter-spacing: 1px;
   }
   
   .menu-item i.fas.fa-users-cog {
       color: #ffd700;
   }
   
   .menu-item i.fas.fa-database {
       color: #ff6b6b;
   }
   ```

2. **Navigation Structure**
   ```css
   .sidebar {
       width: 250px;
       background-color: #2C3E7B;
       position: fixed;
       height: 100vh;
   }
   
   .main-content {
       margin-left: 250px;
   }
   ```

## Page Layouts

### Dashboard Page
1. **Header Section**
   - Family Name
   - Page Description
   - Navigation Breadcrumbs

2. **Statistics Section**
   - Members Count
   - Active Chores
   - Family Points
   - Card-based Layout

3. **Family Members Section**
   - Member Cards Grid
   - Avatar Display
   - Role Indication
   - Points/Coins Display

4. **Activity Section**
   - Recent Activities List
   - Timestamp Display
   - Activity Description
   - Points/Coins Earned

5. **Empty States**
   - No Family Message
   - No Activities Message
   - Create Family CTA

## Responsive Breakpoints
1. **Desktop** (> 1200px)
   - Three-column statistics
   - Four-column member grid
   - Full width activity feed

2. **Tablet** (768px - 1199px)
   - Two-column statistics
   - Three-column member grid
   - Full width activity feed

3. **Mobile** (< 767px)
   - Single-column statistics
   - Single-column member grid
   - Simplified activity feed

## User Interface Patterns
1. **Information Hierarchy**
   - Statistics at top
   - Members in middle
   - Activities at bottom
   - Clear section headings

2. **Visual Feedback**
   - Card hover effects
   - Button state changes
   - Loading states (to be implemented)
   - Error states

3. **Navigation Patterns**
   - Clear breadcrumbs
   - Section headers
   - Responsive menu
   - Back to top (to be implemented)

## Template Structure
1. **Base Layout**
   - Single HTML skeleton in base.html
   - All common head tags and scripts
   - Main content area for blocks

2. **Partial Templates**
   - Location: app/templates/partials/
   - Naming Convention: _filename.html (underscore prefix)
   - No DOCTYPE or HTML structure tags
   - Pure content fragments

3. **Component Organization**
   - Navigation: _sidebar.html, _navbar.html
   - Common UI: _flash_messages.html
   - Reusable sections: _stats_card.html, _member_card.html

4. **Include Pattern**
   ```jinja
   {% include 'partials/_filename.html' %}
   ```

5. **Template Inheritance**
   - All pages extend base.html
   - Blocks for content sections
   - Conditional includes based on auth state