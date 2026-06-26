import json


class RuleDatabaseService:

    def load(self, path):

        with open(path, "r") as f:

            return json.load(f)

    def save(self, path, rules):

        with open(path, "w") as f:

            json.dump(rules, f, indent=4)