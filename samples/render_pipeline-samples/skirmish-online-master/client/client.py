from .net.net_client import NetClient
from .local import core
from client.local.section.section_manager import SectionManager
from client.local.section.main.section import MainSection
from panda3d.core import WindowProperties
from direct.showbase.DirectObject import DirectObject


class Client(DirectObject):
    """
    Main class of the client app.
    """
    STARTUP_SECTION = MainSection

    def __init__(self, server_ip):
        super().__init__()
        self.net_client = NetClient(server_ip)
        self.section_manager = SectionManager()

    def run(self):
        if self.net_client.connect():
            self.basic_configuration()

            section = self.section_manager.switch_to_section(Client.STARTUP_SECTION)
            section.load_model(
                self.net_client.section_state_fetcher.get_main_section_state()
            )
            section.post_model_setup()

            self.net_client.send_ready_for_updates()
            self.net_client.begin_sync_with_server()

            try:
                core.instance.run()
            except:
                print("Disconnecting.")

    def basic_configuration(self):
        core.instance.disable_mouse()
        wind_sound = core.instance.loader.load_sfx("client/local/assets/sounds/wind.ogg")
        wind_sound.set_loop(True)
        wind_sound.play()
        self.accept("aspectRatioChanged", self.handle_aspect_ratio_changed)
        # TODO: set icon, window name etc.

    def handle_aspect_ratio_changed(self):
        # make sure that aspect ratio is maintained when the window resizes
        ww, wh = self.get_window_size()
        props = WindowProperties()
        new_width = int(16 / 9 * wh)
        props.setSize(new_width, wh)
        core.instance.win.requestProperties(props)

    def get_window_size(self):
        return core.instance.win.get_x_size(), core.instance.win.get_y_size()
