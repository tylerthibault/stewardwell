from app import create_app, db
from app.models.user import User
from datetime import datetime

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin is None:
            admin = User(
                username='admin',
                email='admin@stewardwell.com',
                is_admin=True,
                user_type='parent',  # Set user_type as parent
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')  # Change this password in production!
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")

if __name__ == '__main__':
    create_admin_user()
