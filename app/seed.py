from app import db, bcrypt
from app.models.user import (
    User, Family, ChoreCategory, RewardCategory, 
    Reward, GoalCategory, Goal, ModuleSettings
)
from app.models.chore import Chore
from datetime import datetime, timedelta
from app.utils.logger import get_logger

logger = get_logger()

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
            is_superuser=True,
            avatar='fa-user-circle'
        )
        db.session.add(tyler)
        db.session.flush()

        # Create children for Tyler's family
        tyler_children = [
            {
                "username": "Theo",
                "pin": "1234",
                "coins": 100,
                "avatar": "fa-user-ninja"
            },
            {
                "username": "Z",
                "pin": "5678",
                "coins": 50,
                "avatar": "fa-user-astronaut"
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
                coins=child_data["coins"],
                avatar=child_data["avatar"]
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
            family_id=joes_family.id,
            avatar='fa-user-astronaut'
        )
        db.session.add(joe)
        db.session.flush()

        # Create children for Joe's family
        joe_children = [
            {
                "username": "Calvin",
                "pin": "4321",
                "coins": 75,
                "avatar": "fa-user-ninja"
            },
            {
                "username": "Rosie",
                "pin": "8765",
                "coins": 25,
                "avatar": "fa-user-secret"
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
                coins=child_data["coins"],
                avatar=child_data["avatar"]
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
            family_id=curtis_family.id,
            avatar='fa-user-tie'
        )
        db.session.add(curtis)
        db.session.flush()

        # Create children for Curtis's family
        curtis_children = [
            {
                "username": "Cade",
                "pin": "9876",
                "coins": 150,
                "avatar": "fa-user-graduate"
            },
            {
                "username": "Kam",
                "pin": "5432",
                "coins": 80,
                "avatar": "fa-user-ninja"
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
                coins=child_data["coins"],
                avatar=child_data["avatar"]
            )
            db.session.add(child)
        db.session.flush()

        # Create categories and chores for each family
        families = [(tylers_family, tyler), (joes_family, joe), (curtis_family, curtis)]
        
        for family, parent in families:
            # Create Chore Categories
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
                    family_id=family.id,
                    created_by_id=parent.id
                )
                db.session.add(category)
                db.session.flush()
                created_categories[cat_data["name"]] = category

            # Create Goal Categories
            goal_categories = [
                {
                    "name": "Education",
                    "color": "#4A90E2",
                    "icon": "fa-graduation-cap"
                },
                {
                    "name": "Health",
                    "color": "#7ED321",
                    "icon": "fa-heartbeat"
                },
                {
                    "name": "Skills",
                    "color": "#F5A623",
                    "icon": "fa-brain"
                }
            ]

            for goal_cat_data in goal_categories:
                goal_category = GoalCategory(
                    name=goal_cat_data["name"],
                    color=goal_cat_data["color"],
                    icon=goal_cat_data["icon"],
                    family_id=family.id,
                    created_by_id=parent.id
                )
                db.session.add(goal_category)
                db.session.flush()

                # Add some goals for each category
                goal = Goal(
                    title=f"Complete {goal_cat_data['name']} Challenge",
                    description=f"Achieve something great in {goal_cat_data['name']}!",
                    points_required=100,
                    family_id=family.id,
                    created_by_id=parent.id,
                    category_id=goal_category.id
                )
                db.session.add(goal)

            # Create some chores
            chores = [
                {
                    "title": "Make Bed",
                    "description": "Make your bed neatly in the morning",
                    "category": "Bedroom",
                    "points": 10,
                    "status": "pending",
                    "due_date": datetime.utcnow() + timedelta(days=1)
                },
                {
                    "title": "Clean Room",
                    "description": "Pick up toys and vacuum floor",
                    "category": "Bedroom",
                    "points": 20,
                    "status": "pending",
                    "due_date": datetime.utcnow() + timedelta(days=2)
                },
                {
                    "title": "Do Dishes",
                    "description": "Load/unload dishwasher",
                    "category": "Kitchen",
                    "points": 15,
                    "status": "pending",
                    "due_date": datetime.utcnow() + timedelta(days=1)
                }
            ]

            # Get the first child for assigning chores
            first_child = User.query.filter_by(
                family_id=family.id,
                is_parent=False
            ).first()

            for chore_data in chores:
                chore = Chore(
                    title=chore_data["title"],
                    description=chore_data["description"],
                    points=chore_data["points"],
                    status=chore_data["status"],
                    due_date=chore_data["due_date"],
                    family_id=family.id,
                    created_by_id=parent.id,
                    assigned_to_id=first_child.id if first_child else None,
                    category_id=created_categories[chore_data["category"]].id
                )
                db.session.add(chore)

            # Enable modules for each family
            modules = ['economy', 'goals']
            for module in modules:
                module_setting = ModuleSettings(
                    module_name=module,
                    is_enabled=True,
                    family_id=family.id
                )
                db.session.add(module_setting)

        # Commit all changes
        db.session.commit()
        logger.info("Database seeded successfully!")
        
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
        logger.error("Error seeding database", exc_info=True)
        raise e