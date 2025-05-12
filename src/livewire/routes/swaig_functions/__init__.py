import importlib
import pkgutil


def auto_register_swaig_endpoints():
    # Import all modules in this package (routes.swaig)
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{package}.{module_name}")
