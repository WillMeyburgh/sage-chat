import click
from flask.cli import with_appcontext
from sage_chat.database import db
import json
import os
from sage_chat.model.user import User # Import User model
from sage_chat.model.sage import Sage # Import Sage model

@click.command('create-db')
@with_appcontext
def create_db_command():
    """Creates the database tables."""
    db.create_all()
    click.echo('Database tables created!')

@click.command('load-sages')
@with_appcontext
def load_sages_command():
    """Loads sage data from static/sages.json into the database."""
    sages_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'sages.json')
    
    if not os.path.exists(sages_file_path):
        click.echo(f"Error: {sages_file_path} not found. Cannot load sages.")
        return

    try:
        with open(sages_file_path, 'r') as f:
            sages_data_raw = json.load(f)
    except json.JSONDecodeError:
        click.echo(f"Error: Could not decode JSON from {sages_file_path}. Please check file format.")
        return

    for name, data in sages_data_raw.items():
        existing_sage = Sage.query.filter_by(name=name).first()
        if existing_sage:
            click.echo(f"Sage '{name}' already exists. Skipping.")
            continue

        new_sage = Sage(
            name=name,
            initial_message=data.get('initial_message', "Welcome! I am a sage."),
            system_instruction=data.get('system_instruction', "You are a sage."),
            response_template=data.get('response_template', "I am a sage, but I lack a specific response for this query."),
            portrait_url=data.get('portrait_url', "/static/img/default.jpg")
        )
        db.session.add(new_sage)
        click.echo(f"Added sage: {name}")
    
    db.session.commit()
    click.echo('Sages loaded successfully!')
