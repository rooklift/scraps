import sys

# A reasonably complete (?) XML parser written for playful / capricious reasons.

class ParserFail(Exception):
    pass

class Element():
    def __init__(self, tag = "tag"):
        self.tag = tag
        self.attributes = dict()
        self.children = []          # Each child should be an Element or a string not containing Elements

    def __str__(self):
        s = "<{}".format(self.tag)

        for a in self.attributes:
            s += ' {}="{}"'.format(a, self.attributes[a])

        if len(self.children) == 0:
            s += " />"
            return s

        s += ">"

        for c in self.children:
            s += str(c)

        s += "</{}>".format(self.tag)

        return s

    def __repr__(self):
        return "<booxml.Element: {}>".format(self.tag)

    def text(self, recursive = True):
        s = ""
        for child in self.children:
            if type(child) is str:
                s += child
            else:
                if recursive:
                    s += child.text(recursive = True)
        return s

# ---------------------------------------------------------------------
# Enum for parse_element() states...

SEARCHING_LT = 10
SEARCHING_TAG = 20
READING_TAG = 30
SEARCHING_ATTR_OR_GT = 40
EXPECTING_GT_FOR_EMPTY_ELEMENT = 45
READING_ATTR_NAME = 50
SEARCHING_EQUALS = 60
SEARCHING_VALUE = 70
READING_VALUE = 80
READING_TEXT = 90
GOT_LT_WHILE_READING_TEXT = 95
READING_TAG_CLOSE = 100

# ---------------------------------------------------------------------

def parse_xml_file(filename):

    f = open(filename, encoding="UTF-8")

    while 1:
        c = f.read(1)
        if c == "":             # EOF
            raise ParserFail

        if c == "<":
            c = f.read(1)       # Some rigmarol to skip past metadata line
            if c == "?":
                while 1:
                    c = f.read(1)
                    if c != "?":
                        continue
                    c = f.read(1)
                    if c != ">":
                        raise ParserFail
                    break
            else:
                f.seek(f.tell() - 2)
                return parse_element(f)

def parse_element(f):

    element = Element()
    state = SEARCHING_LT

    new_state = None            # When changing state, use this instead of directly setting the state.

    while 1:

        # --------------------------------------------------------------------------------------------
        # Various state transitions require some storage to be inited or set to the last char we read.

        if new_state != None:

            state = new_state
            new_state = None

            if state == READING_TAG:
                element.tag = c
            elif state == READING_TEXT:
                text = ""
                comment_flag = False
            elif state == READING_VALUE:
                value = ""
            elif state == READING_TAG_CLOSE:
                tag_close = ""
            elif state == READING_ATTR_NAME:
                attr_name = c

        # --------------------------------------------------------------------------------------------

        c = f.read(1)
        if c == "":             # Unexpected EOF
            raise ParserFail

        # --------------------------------------------------------------------------------------------

        elif state == SEARCHING_LT:
            if c.isspace():
                continue
            if c != "<":
                raise ParserFail
            new_state = SEARCHING_TAG

        elif state == SEARCHING_TAG:
            if c.isspace():             # Not allowed
                raise ParserFail
            new_state = READING_TAG

        elif state == READING_TAG:
            if c.isspace():
                new_state = SEARCHING_ATTR_OR_GT
                continue
            if c == ">":
                new_state = READING_TEXT
                continue
            element.tag += c

        elif state == SEARCHING_ATTR_OR_GT:
            if c.isspace():
                continue
            if c == ">":
                new_state = READING_TEXT
                continue
            if c == "/":
                new_state = EXPECTING_GT_FOR_EMPTY_ELEMENT
                continue
            new_state = READING_ATTR_NAME

        elif state == EXPECTING_GT_FOR_EMPTY_ELEMENT:
            if c.isspace():
                continue
            if c != ">":
                raise ParserFail
            return element

        elif state == READING_ATTR_NAME:
            if c.isspace():
                new_state = SEARCHING_EQUALS
                continue
            if c == "=":
                new_state = SEARCHING_VALUE
                continue
            attr_name += c

        elif state == SEARCHING_EQUALS:
            if c.isspace():
                continue
            if c == "=":
                new_state = SEARCHING_VALUE
                continue
            raise ParserFail

        elif state == SEARCHING_VALUE:
            if c.isspace():
                continue
            if c == '"':
                new_state = READING_VALUE
                continue

        elif state == READING_VALUE:
            if c == '"':
                element.attributes[attr_name] = value
                new_state = SEARCHING_ATTR_OR_GT
                continue
            value += c

        elif state == READING_TEXT:

            if comment_flag:
                text += c
                if text[-3:] == "-->":
                    comment_flag = False
                continue

            if c == "<":
                c = f.read(1)   # Read one more to check for comment
                if c == "":
                    raise ParserFail

                if c == "!":
                    next2 = f.read(2)
                    if next2 != "--":
                        raise ParserFail
                    text += "<!--"
                    comment_flag = True
                    continue
                else:
                    f.seek(f.tell() - 1)    # Undo the read if not a comment
                    if text:
                        element.children.append(text)
                    new_state = GOT_LT_WHILE_READING_TEXT
                    continue

            text += c

        elif state == GOT_LT_WHILE_READING_TEXT:
            # We know this is not a comment, we tested for that above.

            if c.isspace():   # Not allowed; also would mess with our assumption of fseek(-2) later.
                raise ParserFail
            if c == "/":
                new_state = READING_TAG_CLOSE
                continue
            # We got the start of a new element, so recursively deal with it...
            f.seek(f.tell() - 2)
            next_element = parse_element(f)
            element.children.append(next_element)
            new_state = READING_TEXT

        elif state == READING_TAG_CLOSE:
            if c == ">":
                tag_close = tag_close.strip()
                if tag_close != element.tag:
                    raise ParserFail
                return element
            tag_close += c

        else:
            raise ParserFail


def list_to_element(l, tag = "list"):
    root = Element(tag = tag)
    for item in l:
        node = Element()
        node.tag = "li"
        node.children.append(str(item))
        root.children.append(node)
    return root

# ---------------------------------------------------------------------

def main():
    ent = parse_xml_file(sys.argv[1])
    print(str(ent))

if __name__ == "__main__":
    main()
