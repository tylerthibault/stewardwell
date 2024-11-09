from app import db, bcrypt
from app.models.user import (
    User, Family, ChoreCategory, Chore, 
    RewardCategory, Reward
)
from datetime import datetime, timedelta

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

        # Create Tyler (parent)
        tyler = User(
            username="Tyler",
            email="tt@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=tylers_family.id,
            is_superuser=True
        )
        db.session.add(tyler)
        db.session.flush()

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
        db.session.flush()

        # Create Joe's Family
        joes_family = Family(
            name="Joe's Family",
            family_code="JOEJR1"
        )
        db.session.add(joes_family)
        db.session.flush()

        # Create Joe (parent)
        joe = User(
            username="Joe",
            email="jt@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=joes_family.id
        )
        db.session.add(joe)
        db.session.flush()

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
        db.session.flush()

        # Create Curtis's Family
        curtis_family = Family(
            name="Curtis's Family",
            family_code="CURT1S"
        )
        db.session.add(curtis_family)
        db.session.flush()

        # Create Curtis (parent)
        curtis = User(
            username="Curtis",
            email="ct@email.com",
            password_hash=bcrypt.generate_password_hash("Pass123!!").decode('utf-8'),
            is_parent=True,
            family_id=curtis_family.id
        )
        db.session.add(curtis)
        db.session.flush()

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
        db.session.flush()

        # Create Chore Categories for Tyler's family
        chore_categories = [
            {
                "name": "Bedroom",
                "color": "#FF9999",
                "icon": "fa-bed"
            },
            {
                "name": "Kitchen",
                "color": "#99FF99",
                "icon": "fa-utensils"
            },
            {
                "name": "Bathroom",
                "color": "#9999FF",
                "icon": "fa-bath"
            },
            {
                "name": "Outdoor",
                "color": "#FFFF99",
                "icon": "fa-tree"
            },
            {
                "name": "School",
                "color": "#FF99FF",
                "icon": "fa-book"
            }
        ]

        created_categories = {}
        for cat_data in chore_categories:
            category = ChoreCategory(
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                family_id=tylers_family.id,
                created_by_id=tyler.id
            )
            db.session.add(category)
            db.session.flush()
            created_categories[cat_data["name"]] = category

        # Create some chores
        chores = [
            {
                "title": "Make Bed",
                "description": "Make your bed neatly in the morning",
                "category": "Bedroom",
                "coins": 5,
                "points": 10,
                "frequency": "daily"
            },
            {
                "title": "Clean Room",
                "description": "Pick up toys and vacuum floor",
                "category": "Bedroom",
                "coins": 10,
                "points": 20,
                "frequency": "weekly"
            },
            {
                "title": "Do Dishes",
                "description": "Load/unload dishwasher",
                "category": "Kitchen",
                "coins": 8,
                "points": 15,
                "frequency": "daily"
            },
            {
                "title": "Homework",
                "description": "Complete all homework assignments",
                "category": "School",
                "coins": 15,
                "points": 25,
                "frequency": "daily"
            },
            {
                "title": "Mow Lawn",
                "description": "Mow the front and back yard",
                "category": "Outdoor",
                "coins": 30,
                "points": 50,
                "frequency": "weekly"
            }
        ]

        for chore_data in chores:
            chore = Chore(
                title=chore_data["title"],
                description=chore_data["description"],
                category_id=created_categories[chore_data["category"]].id,
                coins=chore_data["coins"],
                points=chore_data["points"],
                frequency=chore_data["frequency"],
                family_id=tylers_family.id,
                created_by_id=tyler.id,
                assigned_to_id=child.id  # Assign to last child created
            )
            db.session.add(chore)

        # Create Reward Categories
        reward_categories = [
            {
                "name": "Screen Time",
                "color": "#FFB366",
                "icon": "fa-tv"
            },
            {
                "name": "Activities",
                "color": "#66B3FF",
                "icon": "fa-gamepad"
            },
            {
                "name": "Treats",
                "color": "#FF66B3",
                "icon": "fa-ice-cream"
            },
            {
                "name": "Money",
                "color": "#66FFB3",
                "icon": "fa-dollar-sign"
            },
            {
                "name": "Special Privileges",
                "color": "#B366FF",
                "icon": "fa-star"
            }
        ]

        created_reward_categories = {}
        for cat_data in reward_categories:
            category = RewardCategory(
                name=cat_data["name"],
                color=cat_data["color"],
                icon=cat_data["icon"],
                family_id=tylers_family.id,
                created_by_id=tyler.id
            )
            db.session.add(category)
            db.session.flush()
            created_reward_categories[cat_data["name"]] = category

        # Create some rewards
        rewards = [
            {
                "title": "30 Minutes Extra Screen Time",
                "description": "Get 30 minutes of extra screen time",
                "category": "Screen Time",
                "cost": 20
            },
            {
                "title": "Choose Movie Night Film",
                "description": "Pick the movie for family movie night",
                "category": "Special Privileges",
                "cost": 50
            },
            {
                "title": "Ice Cream Trip",
                "description": "Trip to get ice cream",
                "category": "Treats",
                "cost": 30
            },
            {
                "title": "Video Game Time",
                "description": "1 hour of video game time",
                "category": "Activities",
                "cost": 25
            },
            {
                "title": "$5 Cash",
                "description": "Convert coins to real money",
                "category": "Money",
                "cost": 100
            }
        ]

        for reward_data in rewards:
            reward = Reward(
                title=reward_data["title"],
                description=reward_data["description"],
                category_id=created_reward_categories[reward_data["category"]].id,
                cost=reward_data["cost"],
                family_id=tylers_family.id,
                created_by_id=tyler.id
            )
            db.session.add(reward)

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
        print("Child 1 (Theo) PIN: 1234")
        print("Child 2 (Z) PIN: 5678")
        
        print("\nJoe's Family:")
        print("Email: jt@email.com")
        print("Password: Pass123!!")
        print("Family Code: JOEJR1")
        print("Child 1 (Calvin) PIN: 4321")
        print("Child 2 (Rosie) PIN: 8765")
        
        print("\nCurtis's Family:")
        print("Email: ct@email.com")
        print("Password: Pass123!!")
        print("Family Code: CURT1S")
        print("Child 1 (Cade) PIN: 9876")
        print("Child 2 (Kam) PIN: 5432")

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        raise e