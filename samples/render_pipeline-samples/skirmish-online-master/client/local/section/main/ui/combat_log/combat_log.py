from client.local.section.main.ui.text_panels.text_log import TextLog
from client.event import Event


class CombatLog(TextLog):
    def __init__(self, parent_node, units):
        super().__init__(parent_node, width=0.25, height=0.265, n_lines=12, text_y=0.007)
        self.accept(Event.COMBAT_DATA_PARSED, self.handle_combat_data_parsed)
        self.accept(Event.NOT_ENOUGH_MANA, self.handle_not_enough_mana)
        self.units = units

    def handle_combat_data_parsed(self, *args):
        lines = []
        spell_id = args[0]
        damage = args[1]
        source_id = args[2]
        target_ids = args[3]
        for target_id in target_ids:
            lines.append(
                f"{self.units.get(source_id).name}/{self.units.get(target_id).name}/"
                f"{damage}/{spell_id}"
            )
        for line in lines:
            self.add_line(line)
        self.update_view()

    def handle_not_enough_mana(self, *args):
        self.add_line("Not enough mana.")
        self.update_view()

