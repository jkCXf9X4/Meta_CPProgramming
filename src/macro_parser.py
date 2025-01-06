import os
from textwrap import dedent
import clang.cindex as cl
import re

# types
# https://github.com/jiazhihao/clang/blob/master/bindings/python/clang/cindex.py ; 550


class Macro:
    pass


class MacroDef:
    def __init__(self, ast_node=None, token=None):
        self.ast_node = ast_node
        self.token = token


class FunctionMacroDef(MacroDef):
    def __init__(self, ast_node=None, token=None):
        super().__init__(ast_node=ast_node, token=token)

        self.arguments = {}


class ClassMacroDef(MacroDef):
    def __init__(self, ast_node=None, token=None):
        super().__init__(ast_node=ast_node, token=token)

        self.functions = []
        self.variables = []


class ReplacementMacroDef(MacroDef):
    def __init__(self, ast_node=None, token=None):
        super().__init__(ast_node=ast_node, token=token)

        self.replacement_text = None
        self.new_text = None


class CursorExt:
    def __init__(self, node: cl.Cursor):
        self.node: cl.Cursor = node
        self.tokens = self.node.get_tokens()
        self.arguments = self.node.get_arguments()

        self.str_tokens = [x.spelling for x in self.tokens]
        self.str_arguments = [x for x in self.arguments]

    def is_macro(self):
        return (
            self.node.kind == cl.CursorKind.TEMPLATE_NON_TYPE_PARAMETER
            and self.str_tokens
            and self.str_tokens[0] == "macro"
        )
    
    @property
    def lexical_parent(self):
        return CursorExt(self.node.lexical_parent)

    def __str__(self):
        return dedent(f"""
        [line={self.node.location.line}, col={self.node.location.column}] 
        Node: {self.node.spelling} Kind: {self.node.kind} Type: {self.node.type.spelling}
        Arguments: {self.str_arguments}
        Tokens: {self.str_tokens}
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

        self.macros = []

        # If we are parsing from a string instead
        unsaved_files = None
        if in_str:
            unsaved_files = [(path, in_str)]

        self.index = cl.Index.create()
        self.tu = self.index.parse(
            path, args=args, options=options, unsaved_files=unsaved_files
        )

    def find_macros(self):
        self.macros = self.find_next_macro(self.tu.cursor)

    @classmethod
    def find_next_macro(cls, node: cl.Cursor, level=0):
        """Find all references to the type named 'typename'"""
        
        n = CursorExt(node)
        # if level > 0:
        #     print(n.str_level(level))            
        
        if n.is_macro():
            print(f"Found {n.str_level(level)}")
            print(f"Parent {n.lexical_parent}")
           
        for c in node.get_children():
            cls.find_next_macro(c, level=level + 1)

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
