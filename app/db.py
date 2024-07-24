import sqlite3
from os import path
import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    """Получение внутренней базы данных SQLite"""
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


@with_appcontext
def init_db():
    db = get_db()

    with current_app.open_resource(path.join("database", "schema.sql")) as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
def init_db_command():
    """Очистка существующих данных и создание новых таблиц"""
    init_db()
    click.echo("Initialized the database.")


@with_appcontext
def migrate_db():
    db = get_db()

    with current_app.open_resource(path.join("database", "migrate.sql")) as f:
        db.executescript(f.read().decode("utf8"))


@click.command("migrate-db")
def init_db_command():
    """Миграция изменений БД"""
    migrate_db()
    click.echo("Migrated complete.")


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
