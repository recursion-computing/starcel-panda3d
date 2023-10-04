from panda3d.core import *
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import DirectObject

from tkinter import Tk
r = Tk()
r.withdraw()


class InputField:

    def __init__(self, app, pos, scale, width, geoms, on_commit=None):

        self._screen = app.aspect2d
        self._mouse_watcher = app.mouseWatcherNode
        self._task_mgr = app.taskMgr
        win_props = app.win.get_properties()
        self._aspect_ratio = 1. * win_props.get_x_size() / win_props.get_y_size()

        self._scale = scale

        # Initialize the main variables

        self._listener = DirectObject.DirectObject()
        self._selecting_input = False
        self._select_with_mouse_started = False
        self._start_select_from_current_pos = False
        self._ignore_set_text = False
        self._text_was_erased = False
        self._cursor_was_moved = False
        self._text_was_entered = False
        self._text_prev = ""
        self._edited_text = ""
        self._edit = ""
        self._edit_start = 0
        self._char_positions = []
        self._cursor_prev = (0, 0.)
        self._select_start = (0, 0.)
        self._selection = ""

        # Create the text selection background

        cm = CardMaker("text_selection_bg")
        cm.set_frame(0., 1., -.5, 1.)
        cm.set_color(.5, .5, 1., 1.)
        cm.set_has_uvs(False)
        cm.set_has_normals(False)
        self._sel_bg = NodePath(cm.generate())

        # Create the DirectEntry, to which the text selection background will be
        # assigned as a geom when needed
        fontPath = "SourceCodePro-Regular.ttf"
        font2 = loader.loadFont(fontPath, color = (1,1,1,1))
        self._d_entry = DirectEntry(
                                    width=1000000,
                                    rolloverSound=None,
                                    clickSound=None,
                                    text_align=TextNode.ALeft,
                                    relief=None,
                                    entryFont=font2
                                   )

        # Retrieve the geoms to be displayed for the different states of the input
        # field

        self._geom_hilited = geoms.find("**/*_hilited") # for when field has focus
        self._geom_normal = geoms.find("**/*_normal") # for when field has no focus

        # Create a DirectEntryScroll, to which the actual geometry of the input
        # field will be assigned

        self._scroll_frame = DirectEntryScroll(
                                                self._d_entry,
                                                pos=pos,
                                                scale=self._scale,
                                                geom=self._geom_normal,
                                                clipSize=(0., width, -.5, 1.)
                                              )

        cursor_move = self._d_entry.guiItem.get_cursormove_event()
        type_text = self._d_entry.guiItem.get_type_event()
        self._listener.accept(cursor_move, self.__edit_entry)
        self._listener.accept(type_text, self.__notify_edit)

        self._listener.accept("escape", self.__cancel_input)
        self._listener.accept("control-c", self.__copy_selection)
        self._listener.accept("delete", self.__notify_erase, extraArgs=["delete"])
        self._listener.accept("backspace", self.__notify_erase, extraArgs=["backspace"])
        self._listener.accept("shift-delete", self.__notify_erase, extraArgs=["delete"])
        self._listener.accept("shift-backspace", self.__notify_erase, extraArgs=["backspace"])
        self._listener.accept("shift-arrow_left", self.__notify_select)
        self._listener.accept("shift-arrow_right", self.__notify_select)
        self._listener.accept("shift-arrow_left-repeat", self.__notify_select)
        self._listener.accept("shift-arrow_right-repeat", self.__notify_select)
        self._listener.accept("shift-home", self.__notify_select)
        self._listener.accept("shift-end", self.__notify_select)
        self._listener.accept("control-a", self.__select_all)
        self._listener.accept("control-x", self.__cut_selection)

        self._d_entry.bind(DGG.B1PRESS, self.__enable_select_with_mouse)
        self._d_entry.bind(DGG.B1RELEASE, self.__disable_select_with_mouse)

        if on_commit:

            on_commit_command, on_commit_args = on_commit

            # As it is possible that some text is selected when committing the input,
            # the formatting code for the white text color would be passed along to
            # the command that is called then.
            # To prevent this, the given command is wrapped inside a function that
            # ensures only the plain text is passed, as is normally expected.

            def command(text):

                on_commit_command(self._d_entry.get(True), *on_commit_args)

            self._d_entry["command"] = command

        self._d_entry["focusInCommand"] = self.__on_focus_in
        self._d_entry["focusOutCommand"] = self.__on_focus_out

    def __clear_selection(self):

        self._selecting_input = False
        self._d_entry["geom"] = None
        self._selection = ""
        self._d_entry.set(self._d_entry.get(True)) # reset the entry text to black
        self._ignore_set_text = True

    def __notify_edit(self, edit_data):

        self._text_was_entered = True

        text_prev = self._edited_text
        text = self._d_entry.get(True)

        if text != text_prev:
          self._edited_text = text
          cursor_pos = self._d_entry.guiItem.get_cursor_position()
          cursor_pos_prev = self._cursor_prev[0]
          self._edit = text[cursor_pos_prev:cursor_pos]
          self._edit_start = cursor_pos_prev

    def __notify_select(self):

        if self._d_entry.guiItem.get_focus():
          self._cursor_was_moved = True

    def __notify_erase(self, key):

        if self._d_entry.guiItem.get_focus():

            self._text_was_erased = True
            cursor_pos = self._d_entry.guiItem.get_cursor_position()

            # force entry edit when trying to erase past text start or end, so
            # the selection - if any - still gets erased
            if ((key == "delete" and cursor_pos == len(self._d_entry.get(True)))
                    or (key == "backspace" and cursor_pos == 0)):
                cursor_x = self._d_entry.guiItem.getCursorX()
                self.__edit_entry(cursor_x, 0.)

    def __edit_entry(self, cursor_x, cursor_y):

        entry = self._d_entry

        if not entry.guiItem.get_focus():
            return

        cursor_pos = entry.guiItem.get_cursor_position()

        # whenever entry.set() is called, the cursor position changes, so this
        # function gets called; if the previous call to this function indicated
        # that the change in text should be ignored, only the new position of the
        # cursor should be checked this time
        if self._ignore_set_text and not self._cursor_was_moved:
            self._cursor_prev = (cursor_pos, cursor_x)
            self._ignore_set_text = False
            return

        manually_set_cursor = False

        # Determine if text was added to the entry.

        if self._selection and self._text_was_entered and not self._cursor_was_moved:
            # since the cursor was not moved using the arrow keys or by dragging the
            # mouse, a printable character must have been entered
            edit = self._edit
            edit_pos = self._edit_start
        else:
            edit = ""
            edit_pos = -1

        self._edit = ""

        # Handle selection deletion/overwriting.

        if self._selection and (edit or self._text_was_erased):

            entry_txt_prev = self._edited_text

            start_pos, start_x = self._select_start
            end_pos, end_x = self._cursor_prev
            start, end = sorted([start_pos, end_pos])

            edit_len = len(edit)

            if edit_pos == start:
                entry_txt = entry_txt_prev[:start+edit_len] + entry_txt_prev[end+edit_len:]
            else:
                entry_txt = entry_txt_prev[:start] + entry_txt_prev[end:]

            entry.set(entry_txt)
            self._edited_text = entry_txt
            entry.setCursorPosition(start + edit_len)
            manually_set_cursor = True

        # Start, change or cancel selection.

        if self._cursor_was_moved:

            if not self._selecting_input:

                # Start selection

                self._selecting_input = True

                entry["geom"] = self._sel_bg

                if self._start_select_from_current_pos:
                    self._select_start = (cursor_pos, cursor_x)
                    self._start_select_from_current_pos = False
                else:
                    self._select_start = self._cursor_prev

            start_pos, start_x = self._select_start

            if start_pos != cursor_pos:

                # Adjust the selection background

                entry["geom"] = self._sel_bg
                entry["geom_pos"] = (start_x, 0., 0.)
                entry["geom_scale"] = (cursor_x - start_x, 1., 1.)

                # Determine the new selection

                start, end = sorted([start_pos, cursor_pos])
                self._selection = entry.get(True)[start:end]

                # Set the selection color to white

                entry_txt = entry.get(True)
                entry_txt = entry_txt[:start] + "\1white\1" + self._selection \
                            + "\2" + entry_txt[end:]
                entry.set(entry_txt)
                self._ignore_set_text = True

            else:

                self.__clear_selection()

        elif self._selecting_input:

            # Cancel selection

            self.__clear_selection()

        if not self._text_was_entered:
            # the delete or backspace keys must have been pressed, which is not
            # registered through entry.guiItem.getTypeEvent(), so the edited text
            # has to be updated here since it didn't happen in notifyEdit()
            self._edited_text = entry.get(True)

        self._text_was_erased = False
        self._text_was_entered = False
        self._cursor_was_moved = False

        if not manually_set_cursor:
            self._cursor_prev = (cursor_pos, cursor_x)

    def __select_all(self):

        entry = self._d_entry

        if entry.guiItem.get_focus():

            selection = entry.get(True)

            if selection:

                self._select_start = (0, 0.)
                entry["geom_pos"] = (0., 0., 0.)
                self._cursor_was_moved = True
                self._selecting_input = True

                cursor_pos = entry.guiItem.get_cursor_position()

                # force entry edit if cursor is already at end of text
                if cursor_pos == len(selection):
                    cursor_x = entry.guiItem.getCursorX()
                    self.__edit_entry(cursor_x, 0.)
                else:
                    entry.setCursorPosition(len(selection))

    def __copy_selection(self):

        if self._d_entry.guiItem.get_focus() and self._selection:
            r.clipboard_clear()
            r.clipboard_append(self._selection)

    def __cut_selection(self):

        if self._d_entry.guiItem.get_focus() and self._selection:
            r.clipboard_clear()
            r.clipboard_append(self._selection)
            self._text_was_erased = True
            cursor_x = self._d_entry.guiItem.getCursorX()
            self.__edit_entry(cursor_x, 0.)

    def __cancel_input(self):

        if self._d_entry.guiItem.get_focus():
            self._d_entry.guiItem.set_focus(False)

    def __get_char_positions(self):

        tn = self._d_entry.guiItem.get_text_def(0)
        text = ""
        char_pos = [0.]

        for char in self._d_entry.get(True):
            text += char
            char_pos.append(tn.calc_width(text))

        return char_pos

    def __set_cursor_to_mouse_pos(self, task):

        entry = self._d_entry

        entry_txt = entry.get(True)

        if entry_txt != self._text_prev:
            self._char_positions = self.__get_char_positions()
            self._text_prev = entry_txt

        if entry_txt:

            char_positions = self._char_positions[:]
            right_edge = char_positions[-1]
            m_x = (self._mouse_watcher.get_mouse_x() * self._aspect_ratio \
                - entry.get_x(self._screen)) / self._scale

            if m_x <= 0.:
                cursor_pos = 0
            elif m_x >= right_edge:
                cursor_pos = len(char_positions) - 1
            else:
                char_positions.append(m_x)
                char_positions.sort()
                index = char_positions.index(m_x)
                pos_left = char_positions[index-1]
                pos_right = char_positions[index+1]
                if m_x < (pos_left + pos_right) / 2.:
                    cursor_pos = index - 1
                else:
                    cursor_pos = index

        else:

            cursor_pos = 0

        if (cursor_pos != entry.guiItem.get_cursor_position()
                or self._select_with_mouse_started):
            self._select_with_mouse_started = False
            entry.setCursorPosition(cursor_pos)
            self._cursor_was_moved = True

        return task.cont

    def __enable_select_with_mouse(self, event_data):

        self._task_mgr.add(self.__set_cursor_to_mouse_pos, "set_cursor_to_mouse_pos")

        if not self._mouse_watcher.is_button_down("shift"):
            self._start_select_from_current_pos = True
            self._select_with_mouse_started = True
            self.__clear_selection()

    def __disable_select_with_mouse(self, event_data):

        self._task_mgr.remove("set_cursor_to_mouse_pos")
        self._cursor_was_moved = False

    def __on_focus_in(self):

        self._scroll_frame["geom"] = self._geom_hilited

    def __on_focus_out(self):

        self.__clear_selection()
        self._cursor_prev = (0, 0.)
        self._scroll_frame["geom"] = self._geom_normal
        self._d_entry.setCursorPosition(0)