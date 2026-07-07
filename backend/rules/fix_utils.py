import re


class FixUtils:

    @staticmethod
    def regex_replace(

        code,

        pattern,

        replacement

    ):

        return re.sub(

            pattern,

            replacement,

            code,

            flags=re.MULTILINE

        )
