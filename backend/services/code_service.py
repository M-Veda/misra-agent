class CodeService:

    def load(self, path):

        with open(path, "r") as f:

            return f.read()

    def save(self, path, code):

        with open(path, "w") as f:

            f.write(code)