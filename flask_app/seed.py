from flask_app import db, bcrypt
from flask_app.models.user import User, Family, ModuleSettings
from datetime import datetime

def seed_database():
    try:
        # Create Tyler's family
        tylers_family = Family(
            name="Tyler's Family",
            family_code="TYL123"
        )
        db.session.add(tylers_family)
        db.session.flush()  # Flush to get the family ID

        # Create Tyler (Parent)
        tyler = User(
            username="Tyler",
            email="tt@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=True,
            is_superuser=True,
            family_id=tylers_family.id
        )
        db.session.add(tyler)
        db.session.flush()

        # Create Tyler's children
        tyler_child1 = User(
            username="Theo",
            email="theo@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=tylers_family.id,
            parent_id=tyler.id,
            pin="1234"
        )
        tyler_child2 = User(
            username="Z",
            email="z@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=tylers_family.id,
            parent_id=tyler.id,
            pin="1234"
        )
        db.session.add_all([tyler_child1, tyler_child2])

        # Create Joe's family
        joes_family = Family(
            name="Joe's Family",
            family_code="JOE123"
        )
        db.session.add(joes_family)
        db.session.flush()

        # Create Joe (Parent)
        joe = User(
            username="Joe",
            email="joe@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=True,
            family_id=joes_family.id
        )
        db.session.add(joe)
        db.session.flush()

        # Create Joe's children
        joe_child1 = User(
            username="Calvin",
            email="calvin@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=joes_family.id,
            parent_id=joe.id,
            pin="1234"
        )
        joe_child2 = User(
            username="Rosie",
            email="rosie@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=joes_family.id,
            parent_id=joe.id,
            pin="1234"
        )
        db.session.add_all([joe_child1, joe_child2])

        # Create Curtis's family
        curtis_family = Family(
            name="Curtis's Family",
            family_code="CUR123"
        )
        db.session.add(curtis_family)
        db.session.flush()

        # Create Curtis (Parent)
        curtis = User(
            username="Curtis",
            email="curtis@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=True,
            family_id=curtis_family.id
        )
        db.session.add(curtis)
        db.session.flush()

        # Create Curtis's children
        curtis_child1 = User(
            username="Cade",
            email="cade@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=curtis_family.id,
            parent_id=curtis.id,
            pin="1234"
        )
        curtis_child2 = User(
            username="Kam",
            email="kam@email.com",
            password_hash=bcrypt.generate_password_hash("password").decode('utf-8'),
            is_parent=False,
            family_id=curtis_family.id,
            parent_id=curtis.id,
            pin="1234"
        )
        db.session.add_all([curtis_child1, curtis_child2])

        # Add default module settings for each family
        default_modules = ['economy']
        for family in [tylers_family, joes_family, curtis_family]:
            for module_name in default_modules:
                module_setting = ModuleSettings(
                    module_name=module_name,
                    is_enabled=True,
                    family_id=family.id
                )
                db.session.add(module_setting)

        # Commit all changes
        db.session.commit()
        print("Database seeded successfully!")

    except Exception as e:
        db.session.rollback()
        print("Error seeding database:", str(e))
        raise e