import click
from sqlalchemy.orm import Session

from database import get_session
from schemas import UserCreate


@click.command()
@click.option('--username', prompt='Username', help='The username of the superuser')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password of the superuser')
@click.option('--email', prompt='Email', help='The email of the superuser')
@click.option('--perms', prompt='Permissions (-, r, rw)', type=click.Choice(['-', 'r', 'rw']), default='rw', help='Permissions for the new user')
def createsuperuser(username: str, password: str, email: str, perms: str):
    db: Session = next(get_session())
    user_in = UserCreate(username=username, email=email, password=password, is_superuser=True)
    user = crud.user.create(db, obj_in=user_in)
    crud.object.assign_perm(db, user.id, '_user', perms)  # Assigns the chosen perms for _user object to the new user
    click.echo(f"Superuser {user.username} has been created with {perms} perms for _user object.")

