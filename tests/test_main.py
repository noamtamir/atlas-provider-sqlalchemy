from cli.main import run, get_declarative_base, ModelsNotFoundError
from sqlalchemy.orm import DeclarativeBase
import os
import pytest

POSTGRES_DIALECT = 'postgresql+psycopg2'
MYSQL_DIALECT = 'mysql+pymysql'

def test_run_postgres(capsys):
    with open('tests/ddl_postgres.sql', 'r') as f:
        expected_ddl = f.read()
    run(POSTGRES_DIALECT)
    captured = capsys.readouterr()
    assert captured.out == expected_ddl


def test_run_mysql(capsys):
    with open('tests/ddl_mysql.sql', 'r') as f:
        expected_ddl = f.read()
    run(MYSQL_DIALECT)
    captured = capsys.readouterr()
    assert captured.out == expected_ddl


def test_get_declarative_base():
    root_dir = os.getcwd()
    models_dir = os.getcwd()
    Base = get_declarative_base(models_dir, root_dir)
    assert issubclass(Base, DeclarativeBase)


def test_get_declarative_base_explicit_path():
    root_dir = os.getcwd()
    models_dir = os.getcwd() + '/tests/models'
    Base = get_declarative_base(models_dir, root_dir)
    assert issubclass(Base, DeclarativeBase)

def test_get_declarative_base_explicit_path_fail():
    root_dir = os.getcwd()
    models_dir = os.getcwd() + '/nothing/here'
    with pytest.raises(ModelsNotFoundError):
        Base = get_declarative_base(models_dir, root_dir)