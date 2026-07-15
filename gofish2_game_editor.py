import os, sys
import tkinter, tkinter.filedialog, tkinter.messagebox

import gofish2 as gofish

BLACK, WHITE, EMPTY = "b", "w", ""

WIDTH, HEIGHT = 621, 621
GAP = 31

NORMAL, AB, AW, AE = 0, 1, 2, 3     # Click modes

MOTD = """
  NAVIGATE:
  -- Arrows, Home, End, PageUp, PageDown

  SWITCH TO SIBLING:
  -- Tab

  RETURN TO MAIN LINE:
  -- Backspace

  DESTROY NODE:
  -- Delete
"""

CORE_PROPERTIES = {
    "AB", "AW", "AE", "B", "W", "FF", "GM", "CA", "SZ", "KM", "HA",
    "RE", "EV", "GN", "PC", "DT", "RU", "TM", "PB", "PW", "BR", "WR",
}


# Compatibility helpers for the smaller, string-coordinate gofish2 API.

def new_tree(size):
    root = gofish.Node()
    root.set("FF", 4)
    root.set("GM", 1)
    root.set("CA", "UTF-8")
    root.set("SZ", size)
    return root


def set_value(node, key, value):
    value = str(value)
    if value == "" and key not in ["B", "W"]:
        node.delete_key(key)
    else:
        node.set(key, value)


def get_concat(node, key):
    return "".join(node.all_values(key))


def point_to_string(x, y):
    return gofish.xy_to_s(x - 1, y - 1)


def point_from_string(s, node):
    s = node.validated_move_string(s)
    if not s:
        return None
    x, y = gofish.s_to_xy(s)
    return x + 1, y + 1


def points_from_points_string(s, node):
    parts = s.strip().split(":", 1)
    if not parts or len(parts[0]) != 2:
        return set()

    try:
        left, top = gofish.s_to_xy(parts[0])
        right, bottom = gofish.s_to_xy(parts[-1])
    except (TypeError, ValueError):
        return set()

    left, right = sorted((left, right))
    top, bottom = sorted((top, bottom))
    return {
        (x + 1, y + 1)
        for x in range(left, right + 1)
        for y in range(top, bottom + 1)
        if x < node.width and y < node.height
    }


def normalize_setup_ranges(root):
    """Expand compressed setup ranges, which Board.apply expects as single points."""
    todo = [root]
    while todo:
        node = todo.pop()
        todo.extend(node.children)
        for key in ["AB", "AW", "AE"]:
            values = node.all_values(key)
            if not values:
                continue
            points = set()
            for value in values:
                points.update(points_from_points_string(value, node))
            node.delete_key(key)
            for x, y in sorted(points):
                node.add_value(key, point_to_string(x, y))


def move_point(node):
    for key in ["B", "W"]:
        if node.has_key(key):
            return point_from_string(node.get(key), node)
    return None


def move_was_pass(node):
    return any(node.has_key(key) for key in ["B", "W"]) and move_point(node) is None


def moves_made(node):
    return sum(1 for item in node.history() if item.has_key("B") or item.has_key("W"))


def last_colour_played(node):
    while node:
        if node.has_key("PL"):
            if node.get("PL").upper() == "B":
                return WHITE
            if node.get("PL").upper() == "W":
                return BLACK
        if node.has_key("B"):
            return BLACK
        if node.has_key("W"):
            return WHITE
        if node.has_key("AB") and not node.has_key("AW"):
            return BLACK
        if node.has_key("AW") and not node.has_key("AB"):
            return WHITE
        node = node.parent
    return None


def is_main_line(node):
    while node.parent:
        if not node.parent.children or node.parent.children[0] is not node:
            return False
        node = node.parent
    return True


def sibling_moves(node):
    if not node.parent:
        return set()
    return {move_point(item) for item in node.parent.children if item is not node} - {None}


def children_moves(node):
    return {move_point(item) for item in node.children} - {None}


def english_string_from_point(x, y, boardsize):
    columns = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    return "{}{}".format(columns[x - 1], boardsize - y + 1)


def add_setup_stone(node, colour, x, y):
    if node.children or node.has_key("B") or node.has_key("W"):
        node = gofish.Node(node)

    point_sets = {}
    for key in ["AB", "AW", "AE"]:
        points = set()
        for value in node.all_values(key):
            points.update(points_from_points_string(value, node))
        points.discard((x, y))
        point_sets[key] = points

    target_key = {BLACK: "AB", WHITE: "AW", EMPTY: "AE"}[colour]
    point_sets[target_key].add((x, y))

    for key, points in point_sets.items():
        node.delete_key(key)
        for point_x, point_y in sorted(points):
            node.add_value(key, point_to_string(point_x, point_y))
    return node


def clear_markup(node):
    for key in list(node.props):
        if key not in CORE_PROPERTIES:
            node.delete_key(key)


def clear_markup_recursive(root):
    todo = [root]
    while todo:
        node = todo.pop()
        todo.extend(node.children)
        clear_markup(node)


def dump_node(node, include_comments=True):
    for key in sorted(node.props):
        if include_comments or key != "C":
            print("  {}{}".format(key, "".join("[{}]".format(value) for value in node.props[key])))


def debug_node(node):
    node.make_board().dump()
    print()
    dump_node(node)
    print("\n  -- self:         {}".format(node))
    print("  -- parent:       {}".format(node.parent))
    print("  -- siblings:     {}".format(0 if node.parent is None else len(node.parent.children) - 1))
    print("  -- children:     {}".format(len(node.children)))
    print("  -- is main line: {}".format(is_main_line(node)))
    print("  -- moves made:   {}\n".format(moves_made(node)))

# --------------------------------------------------------------------------------------
# Various utility functions...

def load_graphics():
    directory = os.path.dirname(os.path.realpath(__file__))
    graphics_directory = os.path.join(directory, "gfx")
    if not os.path.isdir(graphics_directory):
        # Keep the copied editor usable in this checkout without copying another file.
        graphics_directory = os.path.join(directory, "..", "gofish", "gfx")

    # PhotoImages have a tendency to get garbage-collected even when they're needed.
    # Avoid this by making them globals, so there's always a reference to them.

    global spriteTexture
    try:
        spriteTexture = tkinter.PhotoImage(file = os.path.join(graphics_directory, "texture_override.gif"))
    except:
        spriteTexture = tkinter.PhotoImage(file = os.path.join(graphics_directory, "texture.gif"))

    global textbackSprite
    try:
        textbackSprite = tkinter.PhotoImage(file = os.path.join(graphics_directory, "textback_override.gif"))
    except:
        textbackSprite = tkinter.PhotoImage(file = os.path.join(graphics_directory, "textback.gif"))

    global spriteBlack; spriteBlack = tkinter.PhotoImage(file = os.path.join(graphics_directory, "black.gif"))
    global spriteWhite; spriteWhite = tkinter.PhotoImage(file = os.path.join(graphics_directory, "white.gif"))
    global spriteHoshi; spriteHoshi = tkinter.PhotoImage(file = os.path.join(graphics_directory, "hoshi.gif"))
    global spriteMove; spriteMove = tkinter.PhotoImage(file = os.path.join(graphics_directory, "move.gif"))
    global spriteVarBlack; spriteVarBlack = tkinter.PhotoImage(file = os.path.join(graphics_directory, "var.gif"))
    global spriteVarWhite; spriteVarWhite = tkinter.PhotoImage(file = os.path.join(graphics_directory, "varwhite.gif"))
    global spriteTriangle; spriteTriangle = tkinter.PhotoImage(file = os.path.join(graphics_directory, "triangle.gif"))
    global spriteCircle; spriteCircle = tkinter.PhotoImage(file = os.path.join(graphics_directory, "circle.gif"))
    global spriteSquare; spriteSquare = tkinter.PhotoImage(file = os.path.join(graphics_directory, "square.gif"))
    global spriteMark; spriteMark = tkinter.PhotoImage(file = os.path.join(graphics_directory, "mark.gif"))

    global markup_dict; markup_dict = {"TR": spriteTriangle, "CR": spriteCircle, "SQ": spriteSquare, "MA": spriteMark}

# --------------------------------------------------------------------------------------
# Currently everything that returns a value is outside the class...

def screen_pos_from_board_pos(x, y, boardsize):
    gridsize = GAP * (boardsize - 1) + 1
    margin = (WIDTH - gridsize) // 2
    ret_x = (x - 1) * GAP + margin
    ret_y = (y - 1) * GAP + margin
    return ret_x, ret_y

def board_pos_from_screen_pos(x, y, boardsize):        # Inverse of the above
    gridsize = GAP * (boardsize - 1) + 1
    margin = (WIDTH - gridsize) // 2
    ret_x = round((x - margin) / GAP + 1)
    ret_y = round((y - margin) / GAP + 1)
    return ret_x, ret_y

def title_bar_string(node):
    wwtm = move_point(node)
    mwp = move_was_pass(node)

    if wwtm is None and not mwp:
        if node.parent:
            title = "Empty node"
        else:
            title = "Root node"
    else:
        title = "Move {}".format(moves_made(node))
    if node.parent:
        if len(node.parent.children) > 1:
            index = node.parent.children.index(node)
            title += " [{} of {} variations]".format(index + 1, len(node.parent.children))
    if mwp:
        title += " (pass)"
    elif wwtm:
        x, y = wwtm
        title += " ({})".format(english_string_from_point(x, y, node.width))
    return title

# --------------------------------------------------------------------------------------

class SGF_Board(tkinter.Canvas):
    def __init__(self, owner, filename, *args, **kwargs):
        tkinter.Canvas.__init__(self, owner, *args, **kwargs)

        self.owner = owner

        self.node = new_tree(19)     # Do this now in case the load fails

        self.directory = os.path.dirname(os.path.realpath(sys.argv[0]))

        self.show_siblings = tkinter.IntVar(value = 0)
        self.show_children = tkinter.IntVar(value = 0)
        self.click_mode = tkinter.IntVar(value = NORMAL)

        if filename is not None:
            self.open_file(filename)        # Can fail, leaving us with the tree we created above

        self.node_changed()

    # The show siblings / show children variables can both be off, or one of them can be on, but not both.
    # Tkinter is allowed to toggle them on/off when selected, but the other one must be off in either case...

    def show_siblings_was_toggled(self):
        self.show_children.set(0)
        self.draw_node()

    def show_children_was_toggled(self):
        self.show_siblings.set(0)
        self.draw_node()

    def set_pl(self, colour):
        self.click_mode.set(NORMAL)     # As a GUI intuition, a person setting PL probably wants to go back to normal stone placing
        if colour == BLACK:
            set_value(self.node, "PL", "B")
        elif colour == WHITE:
            set_value(self.node, "PL", "W")
        self.node_changed()

    def open_file(self, infilename):        # expects that there is already a valid self.node
        try:
            roots = gofish.load(infilename)
            loaded_node = roots[0]
            if loaded_node.width != loaded_node.height or not 1 <= loaded_node.width <= 19:
                raise ValueError("the editor supports square boards from 1x1 to 19x19")
            normalize_setup_ranges(loaded_node)
            loaded_node.make_board()
            self.node = loaded_node
            try:
                print("<--- Loaded: {}".format(infilename))
            except:
                print("<--- Loaded: --- Exception when trying to print filename ---")
            print("     Dyer: {}\n".format(self.node.dyer()))
            dump_node(self.node, include_comments = False)
            print()
            self.directory = os.path.dirname(os.path.realpath(infilename))
        except FileNotFoundError:
            print("error while loading: file not found")
        except gofish.ParserFail:
            print("error while loading: parser failed (invalid SGF?)")
        except (IndexError, ValueError) as error:
            print("error while loading: {}".format(error))

    def draw_node(self):
        self.delete(tkinter.ALL)              # DESTROY all!

        board = self.node.make_board()
        boardsize = self.node.width

        all_marks = set()

        # Draw the texture...

        self.create_image(0, 0, anchor = tkinter.NW, image = spriteTexture)

        # Draw the hoshi points...

        if boardsize > 13:
            hoshi_points = gofish.handicap_stones(9, boardsize, boardsize)
        else:
            hoshi_points = gofish.handicap_stones(5, boardsize, boardsize)

        for point_string in hoshi_points:
            point = point_from_string(point_string, self.node)
            screen_x, screen_y = screen_pos_from_board_pos(point[0], point[1], boardsize)
            self.create_image(screen_x, screen_y, image = spriteHoshi)

        # Draw the lines...

        for n in range(1, boardsize + 1):
            start_a, start_b = screen_pos_from_board_pos(n, 1, boardsize)
            end_a, end_b = screen_pos_from_board_pos(n, boardsize, boardsize)

            end_b += 1

            self.create_line(start_a, start_b, end_a, end_b)
            self.create_line(start_b, start_a, end_b, end_a)

        # Draw the stones...

        for x in range(1, boardsize + 1):
            for y in range(1, boardsize + 1):
                screen_x, screen_y = screen_pos_from_board_pos(x, y, boardsize)
                if board.state[x - 1][y - 1] == BLACK:
                    self.create_image(screen_x, screen_y, image = spriteBlack)
                elif board.state[x - 1][y - 1] == WHITE:
                    self.create_image(screen_x, screen_y, image = spriteWhite)

        # Draw a mark at variations, if there are any...

        if self.show_siblings.get():
            sprite = spriteVarWhite if last_colour_played(self.node) == WHITE else spriteVarBlack
            for sib_move in sibling_moves(self.node):
                screen_x, screen_y = screen_pos_from_board_pos(sib_move[0], sib_move[1], boardsize)
                self.create_image(screen_x, screen_y, image = sprite)

        if self.show_children.get():
            sprite = spriteVarBlack if last_colour_played(self.node) in [WHITE, None] else spriteVarWhite
            for child_move in children_moves(self.node):
                screen_x, screen_y = screen_pos_from_board_pos(child_move[0], child_move[1], boardsize)
                self.create_image(screen_x, screen_y, image = sprite)

        # Draw the commonly used marks...

        for mark in markup_dict:
            if mark in self.node.props:
                points = set()
                for value in self.node.props[mark]:
                    points |= points_from_points_string(value, self.node)
                    all_marks |= points
                for point in points:
                    screen_x, screen_y = screen_pos_from_board_pos(point[0], point[1], boardsize)
                    self.create_image(screen_x, screen_y, image = markup_dict[mark])

        # Draw text labels (at most 3 characters of them).

        if "LB" in self.node.props:
            for value in self.node.all_values("LB"):
                if len(value) >= 4:
                    text = value[3:6]           # causes no problems if len is lower
                    if value[2] == ":":
                        points = points_from_points_string(value[0:2], self.node)
                        all_marks |= points
                        for point in points:    # expecting 1 or 0 points
                            screen_x, screen_y = screen_pos_from_board_pos(point[0], point[1], boardsize)
                            if board.state[point[0] - 1][point[1] - 1] == EMPTY:
                                self.create_image(screen_x, screen_y, image = textbackSprite)
                            if board.state[point[0] - 1][point[1] - 1] in [EMPTY, WHITE]:
                                textcolour = "black"
                            else:
                                textcolour = "white"
                            self.create_text(screen_x, screen_y, text = text, fill = textcolour)

        # Draw a mark at the current move, if there is one...

        move = move_point(self.node)
        if move is not None:
            if move not in all_marks:
                screen_x, screen_y = screen_pos_from_board_pos(move[0], move[1], boardsize)
                self.create_image(screen_x, screen_y, image = spriteMove)

    def node_changed(self):
        self.draw_node()
        commentwindow.node_changed(self.node)
        infowindow.node_changed(self.node)
        self.owner.wm_title(title_bar_string(self.node))

    # --------------------------------------------------------------------------------------
    # All the key handlers are in the same form:
    #
    # def handle_key_NAME(self):
    #     <do stuff>
    #
    # where NAME is an uppercase version of the event.keysym, see:
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/key-names.html
    #
    # One can make a new key handler just by creating it, no other work is needed anywhere

    def call_keypress_handler(self, event):
        try:
            function_call = "self.handle_key_{}()".format(event.keysym.upper())
            eval(function_call)
        except AttributeError:
            pass

    # ----- (the above makes the following work) -----

    def handle_key_DOWN(self):
        try:
            self.node = self.node.children[0]
            self.node_changed()
        except IndexError:
            pass

    def handle_key_RIGHT(self):
        self.handle_key_DOWN()

    def handle_key_UP(self):
        if self.node.parent:
            self.node = self.node.parent
            self.node_changed()

    def handle_key_LEFT(self):
        self.handle_key_UP()

    def handle_key_NEXT(self):          # PageDown
        for n in range(10):
            try:
                self.node = self.node.children[0]
            except IndexError:
                break
        self.node_changed()

    def handle_key_PRIOR(self):         # PageUp
        for n in range(10):
            if self.node.parent:
                self.node = self.node.parent
            else:
                break
        self.node_changed()

    def handle_key_TAB(self):
        if self.node.parent:
            if len(self.node.parent.children) > 1:
                index = self.node.parent.children.index(self.node)
                if index < len(self.node.parent.children) - 1:
                    index += 1
                else:
                    index = 0
                self.node = self.node.parent.children[index]
                self.node_changed()

    def handle_key_BACKSPACE(self):         # Return to the main line
        while 1:
            if is_main_line(self.node):
                break
            if self.node.parent is None:
                break
            self.node = self.node.parent
        self.node_changed()

    def handle_key_HOME(self):
        self.node = self.node.get_root()
        self.node_changed()

    def handle_key_END(self):
        self.node = self.node.get_end()
        self.node_changed()

    def handle_key_DELETE(self):
        if len(self.node.children) > 0:
            ok = tkinter.messagebox.askokcancel("Delete?", "Delete this node and all of its children?")
        else:
            ok = True
        if ok:
            unlink_target = self.node

            if self.node.parent:
                parent = self.node.parent
                parent.children.remove(self.node)
                self.node = parent
            else:
                self.node = new_tree(self.node.width)

            self.node_changed()
            unlink_target.parent = None

    def handle_key_P(self):
        self.node = self.node.make_pass()
        self.node_changed()

    def handle_key_D(self):
        debug_node(self.node)

    # Other handlers...

    def opener(self, event = None):
        infilename = tkinter.filedialog.askopenfilename(initialdir = self.directory)
        if infilename:
            self.open_file(infilename)      # this also sets self.directory to match the location
            self.node_changed()

    def saver(self, event = None):
        outfilename = tkinter.filedialog.asksaveasfilename(defaultextension = ".sgf", initialdir = self.directory)
        if outfilename:
            commentwindow.commit_text()             # tell the comment window that it must commit the comment
            infowindow.commit_info()                # likewise for the info window
            gofish.save(outfilename, self.node)
            try:
                print("---> Saved: {}\n".format(outfilename))
            except:
                print("---> Saved: --- Exception when trying to print filename ---")
            self.directory = os.path.dirname(os.path.realpath(outfilename))

    def mousewheel_handler(self, event):
        if event.delta < 0:
            self.handle_key_DOWN()
        else:
            self.handle_key_UP()

    def mouseclick_handler(self, event):
        x, y = board_pos_from_screen_pos(event.x, event.y, self.node.width)

        if self.click_mode.get() != NORMAL:
            self.ab_aw_ae(x, y)
            return

        try:
            self.node = self.node.make_move(point_to_string(x, y))
        except gofish.IllegalMove:
            return
        except ValueError:
            return

        self.node_changed()

    def ab_aw_ae(self, x, y):
        if x < 1 or y < 1 or x > self.node.width or y > self.node.height:
            return

        if self.click_mode.get() == AB:
            colour = BLACK
        elif self.click_mode.get() == AW:
            colour = WHITE
        else:
            colour = EMPTY

        self.node = add_setup_stone(self.node, colour, x, y)

        self.node_changed()

    def new_board(self, size):      # assumes there already is a board; will crash if this is not so
        self.node = new_tree(size)
        self.node_changed()

    def set_handicap(self, h):
        if self.node.parent is None and len(self.node.children) == 0:
            ok = True
        else:
            ok = tkinter.messagebox.askokcancel("New board?", "This requires a fresh board. Destroy the current one?")

        if ok:
            self.new_board(self.node.width)

            points = gofish.handicap_stones(h, self.node.width, self.node.height)
            set_value(self.node, "HA", h)
            for point_string in points:
                x, y = point_from_string(point_string, self.node)
                self.node = add_setup_stone(self.node, BLACK, x, y)

            self.node_changed()

    def clear_markup(self):
        clear_markup(self.node)
        commentwindow.text_widget.delete(1.0, tkinter.END)  # Clear the comment window so it doesn't rewrite its text
        self.node_changed()

    def clear_markup_all(self):
        commentwindow.text_widget.delete(1.0, tkinter.END)  # Clear the comment window so it doesn't rewrite its text
        root = self.node.get_root()
        clear_markup_recursive(root)
        self.node_changed()

# ---------------------------------------------------------------------------------------

class CommentWindow(tkinter.Toplevel):

    def __init__(self, *args, **kwargs):

        tkinter.Toplevel.__init__(self, *args, **kwargs)
        self.title("Comments")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        self.text_widget = tkinter.Text(self, width = 60, height = 20, bg = "#F0F0F0", wrap = tkinter.WORD)
        self.scrollbar = tkinter.Scrollbar(self)

        self.text_widget.pack(side = tkinter.LEFT, fill = tkinter.Y)
        self.scrollbar.pack(side = tkinter.RIGHT, fill = tkinter.Y)

        self.resizable(width = False, height = False)

        self.text_widget.config(yscrollcommand = self.scrollbar.set)
        self.scrollbar.config(command = self.text_widget.yview)

        self.node = gofish.Node()  # This is just a dummy node until we get a real one.

    def node_changed(self, newnode):

        if newnode is self.node:
            return

        self.commit_text()
        self.node = newnode

        s = get_concat(self.node, "C")

        self.text_widget.delete(1.0, tkinter.END)
        self.text_widget.insert(tkinter.END, s)

    def commit_text(self):
        s = self.text_widget.get(1.0, tkinter.END).strip()
        set_value(self.node, "C", s)


class InfoWindow(tkinter.Toplevel):
    def __init__(self, *args, **kwargs):

        tkinter.Toplevel.__init__(self, *args, **kwargs)
        self.title("Game Info")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.resizable(width = False, height = False)

        self.root = gofish.Node()  # This is just a dummy node until we get a real one.

        self.widgets = dict()   # key (e.g. "KM") ---> Entry widget

        # Top section: player names and ranks...

        tkinter.Label(self, text = " Player Black ").grid(column = 0, row = 0)
        tkinter.Label(self, text = " Player White ").grid(column = 0, row = 1)
        tkinter.Label(self, text = " Rank ").grid(column = 2, row = 0)
        tkinter.Label(self, text = " Rank ").grid(column = 2, row = 1)

        self.widgets["PB"] = tkinter.Entry(self, width = 30)
        self.widgets["PW"] = tkinter.Entry(self, width = 30)
        self.widgets["BR"] = tkinter.Entry(self, width = 10)
        self.widgets["WR"] = tkinter.Entry(self, width = 10)

        self.widgets["PB"].grid(column = 1, row = 0)
        self.widgets["PW"].grid(column = 1, row = 1)
        self.widgets["BR"].grid(column = 3, row = 0)
        self.widgets["WR"].grid(column = 3, row = 1)

        tkinter.Label(self, text="").grid(column = 0, columnspan = 4, row = 2)

        # Mid section: various metadata...

        tkinter.Label(self, text = "Event").grid(column = 0, row = 3)
        tkinter.Label(self, text = "Game").grid(column = 0, row = 4)
        tkinter.Label(self, text = "Place").grid(column = 0, row = 5)
        tkinter.Label(self, text = "Date").grid(column = 0, row = 6)

        self.widgets["EV"] = tkinter.Entry(self, width = 30)
        self.widgets["GN"] = tkinter.Entry(self, width = 30)
        self.widgets["PC"] = tkinter.Entry(self, width = 30)
        self.widgets["DT"] = tkinter.Entry(self, width = 30)

        self.widgets["EV"].grid(column = 1, row = 3)
        self.widgets["GN"].grid(column = 1, row = 4)
        self.widgets["PC"].grid(column = 1, row = 5)
        self.widgets["DT"].grid(column = 1, row = 6)

        tkinter.Label(self, text="").grid(column = 0, columnspan = 4, row = 7)

        # Bottom section: result...

        tkinter.Label(self, text = "Komi").grid(column = 0, row = 8)
        tkinter.Label(self, text = "Result").grid(column = 0, row = 9)

        self.widgets["KM"] = tkinter.Entry(self, width = 30)
        self.widgets["RE"] = tkinter.Entry(self, width = 30)

        self.widgets["KM"].grid(column = 1, row = 8)
        self.widgets["RE"].grid(column = 1, row = 9)


    def node_changed(self, node):

        # For simplicity, this widget gets notified every time the viewer's node changes,
        # regardless of whether the root is still the same. So we need to check for that.

        newroot = node.get_root()
        if newroot is self.root:
            return

        # If the identity of the root has changed, save the info into the old root...
        # This is actually pointless. When the game is saved, .commit_info() is called
        # by the saver.

        self.commit_info()

        self.root = newroot

        for key in self.widgets:                            # e.g. key is "RE" or "KM" etc...
            text = get_concat(self.root, key)      # pull the value from the root node
            self.widgets[key].delete(0, tkinter.END)
            self.widgets[key].insert(tkinter.END, text)     # and set the widget to it

    def commit_info(self):

        for key in self.widgets:                            # e.g. key is "RE" or "KM" etc...
            text = self.widgets[key].get().strip()          # pull the value from the widget
            set_value(self.root, key, text)                  # and set the root node accordingly


class HelpWindow(tkinter.Toplevel):
    def __init__(self, *args, **kwargs):

        tkinter.Toplevel.__init__(self, *args, **kwargs)

        self.resizable(width = False, height = False)

        self.title("Help")
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        tkinter.Label(self, text = MOTD, justify = tkinter.LEFT).grid(row = 0, column = 0)
        tkinter.Label(self, text = "  ").grid(row = 0, column = 1)


class Root(tkinter.Tk):
    def __init__(self, *args, **kwargs):

        tkinter.Tk.__init__(self, *args, **kwargs)
        self.resizable(width = False, height = False)

        load_graphics()

        if len(sys.argv) > 1:
            filename = sys.argv[1]
        else:
            filename = None

        self.protocol("WM_DELETE_WINDOW", self.quit)

        global commentwindow
        commentwindow = CommentWindow()
        commentwindow.withdraw()    # comment window starts hidden

        global infowindow
        infowindow = InfoWindow()
        infowindow.withdraw()       # info window starts hidden

        global helpwindow
        helpwindow = HelpWindow()
        helpwindow.withdraw()       # help window starts hidden

        global board
        board = SGF_Board(self, filename, width = WIDTH, height = HEIGHT, bd = 0, highlightthickness = 0)

        menubar = tkinter.Menu(self)

        file_menu = tkinter.Menu(menubar, tearoff = 0)
        file_menu.add_command(label = "Open", command = board.opener)
        file_menu.add_command(label = "Save As", command = board.saver)

        new_board_menu = tkinter.Menu(menubar, tearoff = 0)
        new_board_menu.add_command(label = "19x19", command = lambda : board.new_board(19))
        new_board_menu.add_command(label = "17x17", command = lambda : board.new_board(17))
        new_board_menu.add_command(label = "15x15", command = lambda : board.new_board(15))
        new_board_menu.add_command(label = "13x13", command = lambda : board.new_board(13))
        new_board_menu.add_command(label = "11x11", command = lambda : board.new_board(11))
        new_board_menu.add_command(label = "9x9", command = lambda : board.new_board(9))
        new_board_menu.add_command(label = "7x7", command = lambda : board.new_board(7))

        handicap_menu = tkinter.Menu(menubar, tearoff = 0)
        handicap_menu.add_command(label = "9", command = lambda : board.set_handicap(9))
        handicap_menu.add_command(label = "8", command = lambda : board.set_handicap(8))
        handicap_menu.add_command(label = "7", command = lambda : board.set_handicap(7))
        handicap_menu.add_command(label = "6", command = lambda : board.set_handicap(6))
        handicap_menu.add_command(label = "5", command = lambda : board.set_handicap(5))
        handicap_menu.add_command(label = "4", command = lambda : board.set_handicap(4))
        handicap_menu.add_command(label = "3", command = lambda : board.set_handicap(3))
        handicap_menu.add_command(label = "2", command = lambda : board.set_handicap(2))

        options_menu = tkinter.Menu(menubar, tearoff = 0)
        options_menu.add_checkbutton(label = "Show siblings", variable = board.show_siblings, command = board.show_siblings_was_toggled)
        options_menu.add_checkbutton(label = "Show children", variable = board.show_children, command = board.show_children_was_toggled)
        options_menu.add_separator()
        options_menu.add_command(label="Clear markup (this node)", command = board.clear_markup)
        options_menu.add_command(label="Clear markup (all)", command = board.clear_markup_all)
        options_menu.add_separator()
        options_menu.add_command(label="Set next player: Black", command = lambda : board.set_pl(BLACK))
        options_menu.add_command(label="Set next player: White", command = lambda : board.set_pl(WHITE))
        options_menu.add_separator()
        options_menu.add_radiobutton(label = "Alternate", variable = board.click_mode, value = NORMAL)
        options_menu.add_radiobutton(label = "Add Black", variable = board.click_mode, value = AB)
        options_menu.add_radiobutton(label = "Add White", variable = board.click_mode, value = AW)
        options_menu.add_radiobutton(label = "Add Empty", variable = board.click_mode, value = AE)
        options_menu.add_separator()
        options_menu.add_command(label="Pass", command = lambda : board.handle_key_P())

        menubar.add_cascade(label = "File", menu = file_menu)
        menubar.add_cascade(label = "New", menu = new_board_menu)
        menubar.add_cascade(label = "Handicap", menu = handicap_menu)
        menubar.add_cascade(label = "Options", menu = options_menu)
        menubar.add_command(label = "Comments", command = commentwindow.deiconify)
        menubar.add_command(label = "Info", command = infowindow.deiconify)
        menubar.add_command(label = "Help", command = helpwindow.deiconify)

        self.config(menu = menubar)

        board.pack()

        self.focus_set()
        self.bind("<Key>", board.call_keypress_handler)
        self.bind("<Button-1>", board.mouseclick_handler)
        self.bind("<MouseWheel>", board.mousewheel_handler)
        self.bind("<Control-o>", board.opener)
        self.bind("<Control-s>", board.saver)


if __name__ == "__main__":
    app = Root()
    app.mainloop()
