    @classmethod
    def parse_sgf_alt(cls, sgf):
        return cls.parse_sgf_alt_recursive(sgf, 0, None)["root"]

    @classmethod
    def parse_sgf_alt_recursive(cls, sgf, off, parent_of_local_root):

        root = None
        node = None
        tree_started = False
        inside_value = False
        escape_flag = False

        value = []
        key = []
        keycomplete = False

        i = off - 1
        while i + 1 < len(sgf):

            i += 1
            c = sgf[i]

            if not tree_started:
                if c.isspace():
                    continue
                elif c == "(":
                    tree_started = True
                    continue
                else:
                    raise ParseError("SGF load error: Unexpected byte before (")

            if inside_value:

                if escape_flag:
                    value.append(sgf[i])
                    escape_flag = False
                    continue
                elif c == "\\":
                    escape_flag = True
                    continue
                elif c == "]":
                    inside_value = False
                    if not node:
                        raise ParseError("SGF load error: Value ended by ] but node was None")
                    node.set_property("".join(key), "".join(value))
                    continue
                else:
                    value.append(c)
                    continue

            else:

                if c.isspace() or (c >= "a" and c <= "z"):
                    continue
                elif c == "[":
                    if not node:
                        node = cls._NODE_CLASS(parent=parent_of_local_root)
                        root = node
                    value = []
                    inside_value = True
                    keycomplete = True
                    if len(key) == 0:
                        raise ParseError("SGF load error: Value started by [ but key was empty")
                    continue
                elif c == "(":
                    if not node:
                        raise ParseError("SGF load error: New subtree started but node was None")
                    chars_to_skip = cls.parse_sgf_alt_recursive(sgf, i, node)["readcount"]
                    i += chars_to_skip - 1  # Subtract 1: the ( character we have read is also counted by the recurse.
                    continue
                elif c == ")":
                    if not root:
                        raise ParseError("SGF load error: Subtree ended but local root was None")
                    return {"root": root, "readcount": i + 1 - off}
                elif c == ";":
                    if not node:
                        node = cls._NODE_CLASS(parent=parent_of_local_root)
                        root = node
                    else:
                        node = cls._NODE_CLASS(parent=node)
                    key = []
                    keycomplete = False
                    continue
                elif c >= "A" and c <= "Z":
                    if keycomplete:
                        key = []
                        keycomplete = False
                    key.append(c)
                    continue
                else:
                    raise ParseError("SGF load error: Unacceptable byte while expecting key")

        raise ParseError("SGF load error: Reached end of input")