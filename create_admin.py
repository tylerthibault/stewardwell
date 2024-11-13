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
                is_active=True,
                user_type='parent',  # Admin must be a parent type
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')  # Change this password in production!
            
            try:
                db.session.add(admin)
                db.session.commit()
                print("Admin user created successfully!")
                print("Username: admin")
                print("Password: admin123")
                print("Please change the password after first login.")
                
            except Exception as e:
                db.session.rollback()
                print(f"Error creating admin user: {str(e)}")
                
        else:
            if not admin.is_admin:
                # Ensure the admin user has admin privileges
                admin.is_admin = True
                admin.is_active = True
                db.session.commit()
                print("Existing user 'admin' updated with admin privileges.")
            else:
                print("Admin user already exists!")
                print("Username: admin")
                print("If you need to reset the password, use the admin interface.")

def verify_admin_exists():
    """Verify that at least one admin user exists in the system"""
    app = create_app()
    with app.app_context():
        admin_exists = User.query.filter_by(is_admin=True).first() is not None
        if not admin_exists:
            print("WARNING: No admin users found in the system!")
            print("Creating default admin user...")
            create_admin_user()
        else:
            print("Admin user verification successful.")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--verify':
        verify_admin_exists()
    else:
        create_admin_user()
