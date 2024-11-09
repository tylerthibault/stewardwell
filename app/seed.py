from app import db, bcrypt
from app.models.user import (
    User, Family, ChoreCategory, RewardCategory, 
    Reward, GoalCategory, Goal, ModuleSettings
)
from app.models.chore import Chore
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
                family_id=tylers_family.id,
                created_by_id=tyler.id
            )
            db.session.add(goal_category)
            db.session.flush()

            # Add some goals for each category
            goal = Goal(
                title=f"Complete {goal_cat_data['name']} Challenge",
                description=f"Achieve something great in {goal_cat_data['name']}!",
                points_required=100,
                family_id=tylers_family.id,
                created_by_id=tyler.id,
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
            family_id=tylers_family.id,
            is_parent=False
        ).first()

        for chore_data in chores:
            chore = Chore(
                title=chore_data["title"],
                description=chore_data["description"],
                points=chore_data["points"],
                status=chore_data["status"],
                due_date=chore_data["due_date"],
                family_id=tylers_family.id,
                created_by_id=tyler.id,
                assigned_to_id=first_child.id if first_child else None,
                category_id=created_categories[chore_data["category"]].id
            )
            db.session.add(chore)

        # Enable modules for Tyler's family
        modules = ['economy', 'goals']
        for module in modules:
            module_setting = ModuleSettings(
                module_name=module,
                is_enabled=True,
                family_id=tylers_family.id
            )
            db.session.add(module_setting)

        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")
        
        # Print login credentials
        print("\nDemo Account Created:")
        print("----------------------")
        print("Parent Account:")
        print("Email: tt@email.com")
        print("Password: Pass123!!")
        print("\nChildren Accounts:")
        print("Theo (PIN: 1234)")
        print("Z (PIN: 5678)")
        print("\nFamily Code: TYLER1")

    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
        raise e