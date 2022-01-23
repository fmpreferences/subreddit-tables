import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class App(Gtk.Window):
    def __init__(self):
        super().__init__(title='Whatever')
        self.left_box = Gtk.Box(spacing=10,
                                orientation=Gtk.Orientation.VERTICAL)
        self.right_box = Gtk.Box(spacing=10,
                                 orientation=Gtk.Orientation.VERTICAL)

        self.source_text = Gtk.Label.new('Source Subreddit')
        self.source_name = Gtk.Entry()

        self.source_box = Gtk.Box(spacing=10,
                                  orientation=Gtk.Orientation.VERTICAL)

        self.source_box.pack_start(self.source_text, False, False, 0)
        self.source_box.pack_start(self.source_name, False, False, 0)

        self.wikipage_text = Gtk.Label.new('Wiki Page')
        self.wikipage_name = Gtk.Entry()

        self.wikipage_box = Gtk.Box(spacing=10,
                                    orientation=Gtk.Orientation.VERTICAL)

        self.wikipage_box.pack_start(self.wikipage_text, False, False, 0)
        self.wikipage_box.pack_start(self.wikipage_name, False, False, 0)

        self.subwiki_box = Gtk.Box(spacing=10)

        self.subwiki_box.pack_start(self.source_box, False, False, 0)
        self.subwiki_box.pack_start(self.wikipage_box, False, False, 0)

        self.headers_text = Gtk.Label.new('Headers to match')
        self.headers_name = Gtk.Entry()

        self.multi_text = Gtk.Label.new('Multi Name')
        self.multi_name = Gtk.Entry()

        self.rank_text = Gtk.CheckButton.new_with_mnemonic(
            'Subscriber _Rank Range')

        self.rank_highest = OneHundredSpinButton(True)
        self.rank_lowest = OneHundredSpinButton(True)

        self.rank_text.connect('toggled', self.on_checked_set_editable,
                               self.rank_highest)
        self.rank_text.connect('toggled', self.on_checked_set_editable,
                               self.rank_lowest)

        self.rank_box = Gtk.Box(spacing=10)
        self.rank_box.pack_start(self.rank_highest, False, False, 0)
        self.rank_box.pack_start(self.rank_lowest, False, False, 0)

        self.count_text = Gtk.CheckButton.new_with_mnemonic('_Count')
        self.count_field = OneHundredSpinButton()

        self.count_text.connect('toggled', self.on_checked_set_editable,
                                self.count_field)

        self.calendar_text = Gtk.CheckButton.new_with_mnemonic(
            '_Activity Filter')
        self.calendar = Gtk.Calendar()
        self.calendar_text.connect('toggled', self.on_checked_set_visible,
                                   self.calendar)

        self.submit_btn = Gtk.Button.new_with_label('Submit')
        self.submit_btn.connect('clicked', self.pre_send_checks)

        self.error_text = Gtk.Label.new('')

        self.left_box.pack_start(self.subwiki_box, False, False, 0)
        self.left_box.pack_start(self.headers_text, False, False, 0)
        self.left_box.pack_start(self.headers_name, False, False, 0)
        self.left_box.pack_start(self.multi_text, False, False, 0)
        self.left_box.pack_start(self.multi_name, False, False, 0)
        self.left_box.pack_start(self.rank_text, False, False, 0)
        self.left_box.pack_start(self.rank_box, False, False, 0)
        self.left_box.pack_start(self.count_text, False, False, 0)
        self.left_box.pack_start(self.count_field, False, False, 0)

        self.right_box.pack_start(self.calendar_text, False, False, 0)
        self.right_box.pack_start(self.calendar, False, False, 0)
        self.right_box.pack_start(self.submit_btn, False, False, 0)
        self.right_box.pack_start(self.error_text, False, False, 0)

        self.all_box = Gtk.Box(spacing=10)
        self.all_box.pack_start(self.left_box, False, False, 0)
        self.all_box.pack_start(self.right_box, False, False, 0)

        self.add(self.all_box)

        self.required_entries = [
            self.source_name, self.wikipage_name, self.headers_name,
            self.multi_name
        ]

    def on_checked_set_editable(self, source, target):
        target.set_editable(not target.get_editable())

    def on_checked_set_visible(self, source, target):
        target.set_visible(not target.get_visible())

    def pre_send_checks(self, source):
        for entry in self.required_entries:
            if not entry.get_text():
                self.error_text.set_text('One or more fields is blank!')
                return
        highest = int(self.rank_highest.get_text())
        lowest = int(self.rank_lowest.get_text())

class OneHundredSpinButton(Gtk.SpinButton):
    def __init__(self, negative=False):
        super().__init__()
        upper = 100
        lower = -100 if negative else 0
        adjustment = Gtk.Adjustment(upper=upper,
                                    lower=lower,
                                    step_increment=1,
                                    page_increment=10)
        self.set_numeric(True)
        self.set_editable(False)
        self.set_adjustment(adjustment)


if __name__ == '__main__':
    window = App()
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    window.calendar.set_visible(False)
    Gtk.main()
