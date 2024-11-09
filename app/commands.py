import click
from flask.cli import with_appcontext
from app import db, bcrypt
from app.models.user import User

def init_commands(app):
    app.cli.add_command(make_superuser)

@click.command('make-superuser')
@click.argument('email')
@with_appcontext
def make_superuser(email):
    """Make an existing user a superuser"""
    try:
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f'Error: No user found with email {email}')
            return
        
        user.is_superuser = True
        db.session.commit()
        click.echo(f'User {user.username} is now a superuser!')

    except Exception as e:
        click.echo(f'Error updating user: {str(e)}')
        db.session.rollback() 