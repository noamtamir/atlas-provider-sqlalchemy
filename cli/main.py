import os
import importlib.util
import inspect
from pathlib import Path
from sqlalchemy import create_mock_engine
from sqlalchemy.orm import DeclarativeBase
import typer
import sys


COMMON_VENV_NAMES = [
    '.env',
    '.venv',
    'env',
    'venv',
    'ENV',
    'env.bak',
    'venv.bak',
]


class ModelsNotFoundError(Exception):
    message = 'Found no sqlalchemy models in the directory tree.'


def run(dialect: str, modles_dir: str = '', root_dir: str = '', debug: bool = False) -> type[DeclarativeBase]:
    models_dir = Path(modles_dir) or Path(os.getcwd())
    root_path = Path(root_dir) or Path(os.getcwd())
    Base = get_declarative_base(models_dir, root_path, debug)
    return dump_ddl(dialect, Base)


def get_declarative_base(models_dir: Path, root_dir: Path, debug: bool = False) -> type[DeclarativeBase]:
    '''
    Walk the directory tree starting at the root, import all models, and return 1 of them, as they all keep a refernce to the Metadata object.
    The way sqlalchemy works, you must import all classes in order for them to be registered in Metadata.
    '''
    root_abs_path = os.path.abspath(str(root_dir))
    if root_abs_path not in sys.path:
        sys.path.append(root_abs_path)

    models: set[type[DeclarativeBase]] = set()
    for root, _, _ in os.walk(models_dir):
        python_file_paths = Path(root).glob('*.py')
        for file_path in python_file_paths:
            if should_exclude(file_path):
                continue
            try:
                module_spec = importlib.util.spec_from_file_location(
                    file_path.stem, file_path)
                if module_spec and module_spec.loader:
                    module = importlib.util.module_from_spec(module_spec)
                    module_spec.loader.exec_module(module)
            except Exception as e:
                if debug:
                    print(f'{e.__class__.__name__}: {str(e)}')
                # TODO: handle nicer
                continue
            classes = {c[1]
                       for c in inspect.getmembers(module, inspect.isclass)
                       if issubclass(c[1], DeclarativeBase) and c[1] is not DeclarativeBase}
            models.update(classes)
    try:
        model = models.pop()
    except KeyError as e:
        raise ModelsNotFoundError()
    return model


def dump_ddl(dialect_driver: str, Base: type[DeclarativeBase]) -> type[DeclarativeBase]:
    '''
    Creates a mock engine and dumps its DDL to stdout
    '''
    def dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))

    engine = create_mock_engine(f'{dialect_driver}://', dump)
    Base.metadata.create_all(engine, checkfirst=False)
    return Base


def should_exclude(path: Path) -> bool:
    '''
    Exclude files inside virtual environments to exclude external packages.
    '''
    # TODO: improve. perhaps use .gitigonre
    return any([(x in str(path)) for x in COMMON_VENV_NAMES])


def get_import_path_from_path(path: Path, root_dir: Path) -> str:
    import_path = '.'.join(path.relative_to(
        root_dir).parts).replace(path.suffix, '')
    return import_path


app = typer.Typer(no_args_is_help=True)


@app.command()
def load(dialect: str = typer.Option(default=...), path: str = '', root_dir: str = '', debug: bool = False):
    run(dialect, path, root_dir, debug)


if __name__ == "__main__":
    app(prog_name='atlas-provider-sqlalchemy')
