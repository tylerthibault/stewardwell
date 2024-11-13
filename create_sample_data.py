from app import create_app, db
from app.models.user import User, Family
from app.modules.homeconomy.models import Chore, Reward, Goal
from datetime import datetime

def create_sample_data():
    app = create_app()
    with app.app_context():
        # Create a parent user and family
        parent = User.query.filter_by(username='parent').first()
        if not parent:
            parent = User(
                username='parent',
                email='parent@example.com',
                user_type='parent'
            )
            parent.set_password('parent123')
            db.session.add(parent)
            db.session.flush()  # Flush to get the parent ID

            # Create family
            family = Family(
                name='Sample Family',
                owner_id=parent.id
            )
            db.session.add(family)
            db.session.flush()  # Flush to get the family ID

            # Associate parent with family
            parent.family_id = family.id

        # Create a child user
        child = User.query.filter_by(username='child').first()
        if not child:
            child = User(
                username='child',
                user_type='child',
                family_id=parent.family_id,
                coins=50  # Start with some coins
            )
            child.set_password('child123')
            db.session.add(child)

        # Create sample chores
        chores = [
            {
                'name': 'Clean Your Room',
                'description': 'Make your bed, pick up toys, and vacuum the floor',
                'coins_reward': 20,
                'points_reward': 10,
                'family_id': parent.family_id,
                'is_active': True
            },
            {
                'name': 'Do Your Homework',
                'description': 'Complete all homework assignments for today',
                'coins_reward': 15,
                'points_reward': 8,
                'family_id': parent.family_id,
                'is_active': True
            },
            {
                'name': 'Help with Dishes',
                'description': 'Help load or unload the dishwasher',
                'coins_reward': 10,
                'points_reward': 5,
                'family_id': parent.family_id,
                'is_active': True
            }
        ]

        for chore_data in chores:
            if not Chore.query.filter_by(name=chore_data['name'], family_id=parent.family_id).first():
                chore = Chore(**chore_data)
                db.session.add(chore)

        # Create sample rewards
        rewards = [
            {
                'name': 'Extra Screen Time',
                'description': '30 minutes of extra screen time',
                'coin_cost': 30,
                'family_id': parent.family_id,
                'quantity': -1,  # Unlimited
                'is_active': True
            },
            {
                'name': 'Choose Dinner',
                'description': 'Pick what\'s for dinner!',
                'coin_cost': 50,
                'family_id': parent.family_id,
                'quantity': 3,
                'is_active': True
            },
            {
                'name': 'Stay Up Late',
                'description': 'Stay up 30 minutes past bedtime',
                'coin_cost': 40,
                'family_id': parent.family_id,
                'quantity': -1,  # Unlimited
                'is_active': True
            }
        ]

        for reward_data in rewards:
            if not Reward.query.filter_by(name=reward_data['name'], family_id=parent.family_id).first():
                reward = Reward(**reward_data)
                db.session.add(reward)

        # Create sample goals
        goals = [
            {
                'name': 'Family Movie Night',
                'description': 'Earn a special family movie night with popcorn!',
                'points_required': 100,
                'family_id': parent.family_id,
                'is_active': True
            },
            {
                'name': 'Pizza Party',
                'description': 'Family pizza party when we reach the goal!',
                'points_required': 200,
                'family_id': parent.family_id,
                'is_active': True
            }
        ]

        for goal_data in goals:
            if not Goal.query.filter_by(name=goal_data['name'], family_id=parent.family_id).first():
                goal = Goal(**goal_data)
                db.session.add(goal)

        db.session.commit()

        print("Sample data created successfully!")
        print("\nLogin credentials:")
        print("Parent - Username: parent, Password: parent123")
        print("Child  - Username: child,  Password: child123")

if __name__ == '__main__':
    create_sample_data()
