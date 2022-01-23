import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class App(Gtk.Window):
    def __init__(self):
        super().__init__(title='Whatever')
        self.multi_box = Gtk.Box(spacing=6,
                                 orientation=Gtk.Orientation.VERTICAL)
        self.multi_flavor = Gtk.Label.new('Multi Name')
        self.multi_name = Gtk.Entry()
        self.rank_flavor = Gtk.CheckButton.new_with_mnemonic(
            'Subscriber _Rank Range')
        self.rank_flavor.connect('toggled', self.on_rank_checked)
        self.multi_box.pack_start(self.multi_flavor, False, False, 0)
        self.multi_box.pack_start(self.multi_name, False, False, 0)
        self.multi_box.pack_start(self.rank_flavor, False, False, 0)
        self.add(self.multi_box)
    
    def on_rank_checked(self):
        print('rank enabled')


if __name__ == '__main__':
    window = App()
    window.connect('destroy', Gtk.main_quit)
    window.show_all()
    Gtk.main()
