import sqlite3

import click
from flask import current_app, g, render_template


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


# def get_restaurants(query=""):
#     db = get_db()

#     if query:
#         restaurants = db.execute("SELECT r.name, r.rating, r.min_order_amount, p.photo_path FROM restaurants r LEFT JOIN restaurant_photos p ON r.id=p.restaurant_id WHERE name LIKE ?;", (f'%{query}%',))
#     else:    
#         restaurants = db.execute("SELECT r.name, r.rating, r.min_order_amount, p.photo_path FROM restaurants r LEFT JOIN restaurant_photos p ON r.id=p.restaurant_id;")
    
#     return restaurants.fetchall()