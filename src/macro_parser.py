import os
from textwrap import dedent
import clang.cindex as cl
import re

# types
# https://github.com/jiazhihao/clang/blob/master/bindings/python/clang/cindex.py ; 550

class Macro:
    pass

class FunctionMacro(Macro):
    pass

class ClassMacro(Macro):
    pass

class ReplacementMacro(Macro):
    pass


class MacroParser:
    def print_tree(self):
        self.print_next(self.tu.cursor)

    def print_next(self, node: cl.Cursor, level=0):
        """Find all references to the type named 'typename'"""

        if level > 0:
            tokens = node.get_tokens()
            arguments = node.get_arguments()

            print(
                dedent(f"""
                {'-'*level} [line={node.location.line}, col={node.location.column}] 
                {' '*level} Node: {node.spelling} Kind: {node.kind} Type: {node.type.spelling}
                {' '*level} Arguments: {[x for x in arguments]}
                {' '*level} Tokens: {[x.spelling for x in tokens]}
                """).strip()
            )

        for c in node.get_children():
            self.print_next(c, level=level + 1)

    def __init__(self, path="temp.mpp", in_args=[], in_str="", options=0):
        print(f"{in_args=}")

        args = "-x c++ --std=c++20".split()
        print(f"{args=}")

        # syspath = ccsyspath.system_include_paths("clang++")
        # incargs = [b"-I" + inc for inc in syspath]
        # print(f"{incargs=}")

        args = args + in_args  # + incargs

        self.macros = []

        # If we are parsing from a string instead
        unsaved_files = None
        if in_str:
            unsaved_files = [(path, in_str)]

        self.index = cl.Index.create()
        self.tu = self.index.parse(
            path, args=args, options=options, unsaved_files=unsaved_files
        )

    def register_macro(self, m):
        if type(m) in [list, set, tuple]:
            self.macros += m
        else:
            self.macros.append(m)

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

    def find_serializable_types(self, match_str="//\+serde\(([A-Za-z\s,_]*)\)"):
        match_types = [cl.CursorKind.STRUCT_DECL, cl.CursorKind.CLASS_DECL]

        cursor: cl.Cursor = self.tu.cursor
        tokens = cursor.get_tokens()

        found = False
        serializables = []

        for token in tokens:
            match = re.match(match_str, token.spelling)
            if found:
                cursor = cl.Cursor().from_location(self.tu, token.location)
                if cursor.kind in match_types:
                    full_name = "::".join(
                        self.get_current_scope(cursor) + [cursor.spelling]
                    )

                    t: cl.Type = cursor.type
                    fields = [
                        (
                            field.spelling,
                            field.type.spelling,
                            field.access_specifier.name,
                        )
                        for field in t.get_fields()
                    ]

                    serializables.append((full_name, fields))

                    # Start searching for more comments.
                    found = False
                    print(f"{serializables[-1]=}")

            elif (token.kind == cl.TokenKind.COMMENT) and match:
                found = True
                print(f"{match=}")

        return serializables
