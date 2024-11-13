# StewardWell - Family Management Platform

StewardWell is a modular family management platform built with Flask, following the MVC pattern. The platform allows families to manage various aspects of their household through different modules.

## Current Modules

### Homeconomy
A comprehensive chore and reward management system that helps parents incentivize and track children's contributions to household tasks. See [Homeconomy Module Documentation](app/modules/homeconomy/README.md) for details.

Features:
- Chore management with coin and point rewards
- Individual reward store for children
- Family-wide goals and achievements
- Parent verification system
- Progress tracking and statistics

## Technical Stack

- Python 3.8+
- Flask Web Framework
- SQLAlchemy ORM
- Flask-Login for authentication
- Flask-Migrate for database migrations
- TailwindCSS for styling
- SQLite database (configurable for other databases)

## Project Structure

```
stewardwell/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   └── user.py
│   ├── modules/
│   │   └── homeconomy/
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── forms.py
│   │       ├── routes.py
│   │       ├── README.md
│   │       └── templates/
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   ├── main/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── templates/
│       ├── base.html
│       ├── auth/
│       └── main/
├── config.py
├── requirements.txt
└── run.py
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/stewardwell.git
cd stewardwell
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` as needed

5. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. Create an admin user:
```bash
python create_admin.py
```

7. Run the application:
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## User Types and Features

### Parent Users
- Create and manage family
- Add and manage children
- Create and assign chores
- Verify completed chores
- Create rewards and goals
- Monitor progress and achievements

### Child Users
- View assigned and available chores
- Complete chores to earn coins and points
- Spend coins in the reward store
- Track individual progress
- Contribute to family goals

## Module System

StewardWell uses a modular architecture where each module:
- Has its own models, views, and controllers
- Maintains its own documentation
- Can be enabled/disabled per family
- Follows consistent design patterns

### Creating New Modules
1. Create a new directory in `app/modules/`
2. Include required components:
   - `__init__.py` with Blueprint
   - `models.py` for database models
   - `routes.py` for endpoints
   - `forms.py` for forms
   - `README.md` for documentation
   - Templates directory

## Security

- All passwords are hashed using Werkzeug's security features
- Session management handled by Flask-Login
- CSRF protection enabled by default
- Role-based access control
- Secure form handling

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Future Enhancements

- Additional modules for different family management aspects
- Mobile application support
- Advanced reporting and analytics
- Integration with external services
- Notification system
- API for third-party integrations

## License

This project is licensed under the MIT License - see the LICENSE file for details.
