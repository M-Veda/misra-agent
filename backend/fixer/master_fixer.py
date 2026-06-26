from fixer.declaration_fixer import fix_declarations
from fixer.expression_fixer import fix_expressions
from fixer.pointer_fixer import fix_pointers
from fixer.array_fixer import fix_arrays
from fixer.memory_fixer import fix_memory
from fixer.loop_fixer import fix_loops
from fixer.formatting import format_code


class MasterFixer:

    def fix(self, code):

        code = fix_declarations(code)

        code = fix_expressions(code)

        code = fix_pointers(code)

        code = fix_arrays(code)

        code = fix_memory(code)

        code = fix_loops(code)

        code = format_code(code)

        return code