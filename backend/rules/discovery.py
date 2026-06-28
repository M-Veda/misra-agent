import importlib
import inspect
import pkgutil

from rules.base_rule import BaseRule


def discover_rule_classes(packages):
    discovered = []
    seen = set()

    for package_name in packages or ():
        package = importlib.import_module(package_name)
        if not hasattr(package, "__path__"):
            for rule_class in _discover_from_module(package):
                if rule_class not in seen:
                    discovered.append(rule_class)
                    seen.add(rule_class)
            continue

        for module_info in pkgutil.walk_packages(package.__path__, prefix=f"{package.__name__}."):
            module_name = module_info.name
            if module_name.rsplit(".", 1)[-1].startswith("_"):
                continue
            module = importlib.import_module(module_name)
            for rule_class in _discover_from_module(module):
                if rule_class not in seen:
                    discovered.append(rule_class)
                    seen.add(rule_class)

    return discovered


def _discover_from_module(module):
    discovered = []
    for _, rule_class in inspect.getmembers(module, inspect.isclass):
        if rule_class is BaseRule:
            continue
        if not issubclass(rule_class, BaseRule):
            continue
        if rule_class.__module__ != module.__name__:
            continue
        if inspect.isabstract(rule_class):
            continue
        discovered.append(rule_class)
    return discovered
