class FileService:

    def read(self, path):

        with open(path, "r") as f:

            return f.read()

    def write(self, path, code):

        with open(path, "w") as f:

            f.write(code)