from client.local import core
from client.event import Event
from client.local.font import base
from client.local.font import MainFont

from ..model.model import MainSectionModel

from direct.gui.DirectGui import DirectWaitBar, DirectLabel
from direct.showbase.DirectObject import DirectObject


class FloatingBars(DirectObject):
    def __init__(self, model: MainSectionModel):
        DirectObject.__init__(self)
        self.model = model
        self.floating_bars = {}
        self.accept(Event.NEW_UNIT_CREATED, self.handle_local_new_unit)
        self.accept(Event.UNIT_HP_UPDATED, self.handle_unit_hp_updated)
        self.accept(Event.UNIT_MANA_UPDATED, self.handle_unit_mana_updated)
        self.accept(Event.UNIT_NAME_UPDATED, self.handle_unit_name_updated)
        self.accept(Event.UNIT_DISCONNECTED, self.handle_unit_disconnected)
        self.accept(Event.UNIT_MODEL_UPDATED, self.handle_unit_model_updated)

    def handle_local_new_unit(self, *args):
        unit = args[0]
        if unit is not None:
            self.create_bar(unit)

    def handle_unit_hp_updated(self, *args):
        unit = args[0]
        self.update_health_bar(unit)

    def handle_unit_mana_updated(self, *args):
        unit = args[0]
        self.update_mana_bar(unit)

    def handle_unit_name_updated(self, *args):
        unit = args[0]
        self.update_name_label(unit)

    def handle_unit_disconnected(self, *args):
        unit_id = args[0]
        self.delete_bar(unit_id)

    def handle_unit_model_updated(self, *args):
        unit = args[0]
        self.update_vertical_position(unit)

    def delete_bar(self, unit_id):
        bar = self.floating_bars.get(unit_id, None)
        if bar is not None:
            bar.destroy()
            del self.floating_bars[unit_id]

    def update_health_bar(self, unit):
        bar = self.floating_bars.get(unit.id, None)
        if bar is not None:
            bar.health_bar["value"] = unit.health

    def update_mana_bar(self, unit):
        bar = self.floating_bars.get(unit.id, None)
        if bar is not None:
            bar.mana_bar["value"] = unit.mana

    def update_name_label(self, unit):
        bar = self.floating_bars.get(unit.id, None)
        if bar is not None:
            bar.name_label["text"] = unit.name

    def update_vertical_position(self, unit):
        bar = self.floating_bars.get(unit.id)
        if bar is not None:
            bar.update_vertical_position()

    def create_bar(self, unit):
        new_bar = FloatingBar(unit)
        self.floating_bars[unit.id] = new_bar


class FloatingBar:
    def __init__(self, unit):
        self.unit = unit
        self.node = unit.base_node.attach_new_node("floating bar node")
        self.node.set_pos(0, 0, unit.actor.HEIGHT)

        self.health_bar = DirectWaitBar(
            value=unit.health,
            parent=self.node,
            frameColor=(1, 0, 0, 0.3),
            barColor=(0, 1, 0, 1),
        )
        self.health_bar.reparent_to(self.node)
        self.health_bar.set_scale(0.13)
        self.health_bar.set_compass(core.instance.camera)

        self.mana_bar = DirectWaitBar(
            value=unit.mana,
            pos=(0, 0, -0.03),
            parent=self.node,
            frameColor=(0, 0, 0, 0.3),
            barColor=(0, 0, 1, 1),
            frameSize=(-1, 1, 0.05, 0.15)
        )
        self.mana_bar.reparent_to(self.node)
        self.mana_bar.set_scale(0.13)
        self.mana_bar.set_compass(core.instance.camera)

        font = MainFont()
        self.name_label = DirectLabel(
            text=unit.name,
            pos=(0, 0, 0.03),
            scale=0.04,
            parent=self.node,
            text_bg=(0, 0, 0, 0),
            text_fg=(1, 1, 1, 1),
            frameColor=(0, 0, 0, 0),
            text_font=font,
        )
        self.name_label.set_compass(core.instance.camera)

    def update_vertical_position(self):
        self.node.set_pos(0, 0, self.unit.actor.HEIGHT)

    def destroy(self):
        self.mana_bar.destroy()
        self.health_bar.destroy()
        self.name_label.destroy()

