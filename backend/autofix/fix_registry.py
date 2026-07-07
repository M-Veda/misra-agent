from pathlib import Path
import importlib
import pkgutil


class FixRegistry:

    def __init__(self):

        self.fixers = {}

        self.discover()

    def discover(self):

        package = "autofix"

        root = Path(__file__).parent

        for _, module_name, _ in pkgutil.iter_modules([str(root)]):

            if module_name.startswith("base"):
                continue

            if module_name.startswith("fix_"):

                module = importlib.import_module(
                    f"{package}.{module_name}"
                )

                for obj in module.__dict__.values():

                    if (
                        isinstance(obj, type)
                        and obj.__name__.endswith("Fixer")
                        and obj.__name__ != "BaseFixer"
                        and getattr(obj, "RULE_ID", "")
                    ):
                        self.fixers[obj.RULE_ID] = obj()

    def get(
        self,
        rule_id,
    ):
        return self.fixers.get(rule_id)