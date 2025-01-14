from itertools import groupby
from textwrap import dedent
import clang.cindex as cl


from src.default_macros import default_macros

# types
# https://github.com/jiazhihao/clang/blob/master/bindings/python/clang/cindex.py ; 550


class Macro:
    def __init__(self, function, arguments=[], macro_node=None, macro_def_node=None):
        self.function = function
        self.arguments = arguments

        self.macro_node: CursorExt = macro_node
        self.macro_def_node: CursorExt = macro_def_node

    def __str__(self):
        return f"[Macro] {self.function.__name__} args{self.arguments}, {self.macro_node.node.spelling}"


class TokenExt:
    def __init__(self, tokens: list):
        self.strings = tokens

    def is_macro(self):
        return self.strings != [] and self.strings[0] == "macro"

    def get_macro_atr(self):
        macro_name = self.strings[1]

        arguments = []
        if "(" in self.strings:
            not_args = ["macro", macro_name, "(", ")", ","]
            arguments = [x for x in self.strings if x not in not_args]

        return macro_name, arguments

    def codify(self):
        tokens = self.strings.copy()
        print(tokens)

        if tokens[-1] not in ["}", ":"] and "class" not in tokens:
            tokens.append(";")

        i = 0
        while i < len(tokens):
            if tokens[i] in ["{", ":", ";"]:
                tokens.insert(i + 1, "\n")
            i += 1

        print(tokens)
        return " ".join(tokens)


class CursorExt:
    def __init__(self, node: cl.Cursor):
        self.node: cl.Cursor = node
        self.tokens = TokenExt([x.spelling for x in self.node.get_tokens()])

        self.arguments = [x for x in self.node.get_arguments()]

    def is_macro(self):
        macro_type = cl.CursorKind.TEMPLATE_NON_TYPE_PARAMETER
        return self.node.kind == macro_type and self.tokens.is_macro()

    def get_macro(self):
        macro_name, arguments = self.tokens.get_macro_atr()
        func = default_macros[macro_name]

        return Macro(
            function=func,
            arguments=arguments,
            macro_node=self.lexical_parent,
            macro_def_node=self,
        )

    def to_code(self):
        tokens = self.get_node_tokens()

        out = f"{self.codify(tokens)}{{\n"
        for c in self.get_children():
            out += f"{self.codify(c.tokens.strings)}\n"
        out += "}"
        return out

    def get_children(self):
        return [CursorExt(c) for c in self.node.get_children()]

    @property
    def lexical_parent(self):
        return CursorExt(self.node.lexical_parent)

    def __str__(self):
        return dedent(f"""
        [line={self.node.location.line}, col={self.node.location.column}] 
        Node: {self.node.spelling} Kind: {self.node.kind} Type: {self.node.type.spelling}
        Arguments: {self.arguments}
        Tokens: {self.tokens.strings}
        """).strip()

    def str_level(self, level=0):
        return f"{'-'*level} " + f"\n{' '*level} ".join(str(self).split("\n"))


class MacroParser:
    def __init__(self, path="temp.mpp", in_args=[], in_str="", options=0):
        print(f"{in_args=}")

        args = "-x c++ --std=c++20".split()
        print(f"{args=}")

        # syspath = ccsyspath.system_include_paths("clang++")
        # incargs = [b"-I" + inc for inc in syspath]
        # print(f"{incargs=}")

        args = args + in_args  # + incargs

        self.macros: list[Macro] = []

        # If we are parsing from a string instead
        unsaved_files = None
        if in_str:
            unsaved_files = [(path, in_str)]

        self.index = cl.Index.create()
        self.tu = self.index.parse(
            path, args=args, options=options, unsaved_files=unsaved_files
        )

    def find_macros(self):
        self.find_next_macro(self.tu.cursor)

    def find_next_macro(self, node: cl.Cursor, level=0):
        """Find all references to the type named 'typename'"""

        n = CursorExt(node)
        # if level > 0:
        print(n.str_level(level))

        if n.is_macro():
            self.macros.append(n.get_macro())

        for c in node.get_children():
            self.find_next_macro(c, level=level + 1)

    def get_current_scope(self, cursor: cl.Cursor):
        """
        Get the current scope of the current cursor.

        For example:

        namespace A {
        namespace B {

        class C {
            <CURSOR IS IN HERE>
        };

        }
        }

        will return: ["A", "B", "C"] and can be joined to be "A::B::C"

        Parameters ::
        - cursor: A clang.cindex.Cursor to loop for declaration parents of.

        Returns ::
        - A list of names of the scopes.
        """
        parent: cl.Cursor = cursor.lexical_parent

        if parent.kind.is_declaration():
            return self.get_current_scope(parent) + [parent.spelling]
        else:
            return []


def parse_file(file: str):
    macro_parser = MacroParser(file)
    macro_parser.find_macros()

    print("\nFound:")
    for m in macro_parser.macros:
        print(m)
        print(m.macro_node.get_node_tokens())
        print(m.macro_node.to_code())

    # def find_serializable_types(self, match_str="//\+serde\(([A-Za-z\s,_]*)\)"):
    #     match_types = [cl.CursorKind.STRUCT_DECL, cl.CursorKind.CLASS_DECL]

    #     cursor: cl.Cursor = self.tu.cursor
    #     tokens = cursor.get_tokens()

    #     found = False
    #     serializables = []

    #     for token in tokens:
    #         match = re.match(match_str, token.spelling)
    #         if found:
    #             cursor = cl.Cursor().from_location(self.tu, token.location)
    #             if cursor.kind in match_types:
    #                 full_name = "::".join(
    #                     self.get_current_scope(cursor) + [cursor.spelling]
    #                 )

    #                 t: cl.Type = cursor.type
    #                 fields = [
    #                     (
    #                         field.spelling,
    #                         field.type.spelling,
    #                         field.access_specifier.name,
    #                     )
    #                     for field in t.get_fields()
    #                 ]

    #                 serializables.append((full_name, fields))

    #                 # Start searching for more comments.
    #                 found = False
    #                 print(f"{serializables[-1]=}")

    #         elif (token.kind == cl.TokenKind.COMMENT) and match:
    #             found = True
    #             print(f"{match=}")

    #     return serializables
