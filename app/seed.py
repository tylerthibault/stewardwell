from app import db, bcrypt
from app.models.user import User, Family

def seed_database():
    """Seed the database with initial data"""
    try:
        # Create Tyler's Family
        tylers_family = Family(
            name="Tyler's Family",
            family_code="TYLER1"
        )
        db.session.add(tylers_family)
        db.session.flush()

        tyler = User(
            username="Tyler",
            email="tt@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=tylers_family.id,
            is_superuser=True  # Make Tyler a superuser
        )
        db.session.add(tyler)

        # Create children for Tyler's family
        tyler_children = [
            {
                "username": "Theo",
                "pin": "1234",
                "coins": 100
            },
            {
                "username": "Z",
                "pin": "5678",
                "coins": 50
            }
        ]

        for child_data in tyler_children:
            child = User(
                username=child_data["username"],
                email=f"{child_data['username']}@child.local",
                password_hash=bcrypt.generate_password_hash("child-account").decode('utf-8'),
                pin=child_data["pin"],
                is_parent=False,
                family_id=tylers_family.id,
                parent_id=tyler.id,
                coins=child_data["coins"]
            )
            db.session.add(child)

        # Create Joe's Family
        joes_family = Family(
            name="Joe's Family",
            family_code="JOEJR1"
        )
        db.session.add(joes_family)
        db.session.flush()

        joe = User(
            username="Joe",
            email="jt@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=joes_family.id
        )
        db.session.add(joe)

        # Create children for Joe's family
        joe_children = [
            {
                "username": "Calvin",
                "pin": "4321",
                "coins": 75
            },
            {
                "username": "Rosie",
                "pin": "8765",
                "coins": 25
            }
        ]

        for child_data in joe_children:
            child = User(
                username=child_data["username"],
                email=f"{child_data['username']}@child.local",
                password_hash=bcrypt.generate_password_hash("child-account").decode('utf-8'),
                pin=child_data["pin"],
                is_parent=False,
                family_id=joes_family.id,
                parent_id=joe.id,
                coins=child_data["coins"]
            )
            db.session.add(child)

        # Create Curtis's Family
        curtis_family = Family(
            name="Curtis's Family",
            family_code="CURT1S"
        )
        db.session.add(curtis_family)
        db.session.flush()

        curtis = User(
            username="Curtis",
            email="ct@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=curtis_family.id
        )
        db.session.add(curtis)

        # Create children for Curtis's family
        curtis_children = [
            {
                "username": "Cade",
                "pin": "9876",
                "coins": 150
            },
            {
                "username": "Kam",
                "pin": "5432",
                "coins": 80
            }
        ]

        for child_data in curtis_children:
            child = User(
                username=child_data["username"],
                email=f"{child_data['username']}@child.local",
                password_hash=bcrypt.generate_password_hash("child-account").decode('utf-8'),
                pin=child_data["pin"],
                is_parent=False,
                family_id=curtis_family.id,
                parent_id=curtis.id,
                coins=child_data["coins"]
            )
            db.session.add(child)

        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")
        
        # Print login credentials
        print("\nDemo Accounts Created:")
        print("----------------------")
        print("\nTyler's Family:")
        print("Email: tt@email.com")
        print("Password: Pass123!!")
        print("Family Code: TYLER1")
        print("Child 1 PIN: 1234")
        print("Child 2 PIN: 5678")
        
        print("\nJoe's Family:")
        print("Email: jt@email.com")
        print("Password: Pass123!!")
        print("Family Code: JOEJR1")
        print("Child 1 PIN: 4321")
        print("Child 2 PIN: 8765")
        
        print("\nCurtis's Family:")
        print("Email: ct@email.com")
        print("Password: Pass123!!")
        print("Family Code: CURT1S")
        print("Child 1 PIN: 9876")
        print("Child 2 PIN: 5432")

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        raise e