from nml.expression import *
from nml.actions import action2, actionD
from action6 import *

class Action3(object):
    def __init__(self, feature, id):
        self.feature = feature
        self.id = id
        self.cid_mappings = []

    def prepare_output(self):
        self.cid_mappings = [(cargo, action2.remove_ref(cid)) for cargo, cid in self.cid_mappings]
        if self.def_cid != 0: self.def_cid = action2.remove_ref(self.def_cid)

    def write(self, file):
        size = 7 + 3 * len(self.cid_mappings)
        if self.feature <= 3: size += 2
        file.print_sprite_size(size)
        file.print_bytex(3)
        file.print_bytex(self.feature)
        file.print_bytex(1 if not self.is_livery_override else 0x81) # a single id
        file.print_varx(self.id, 3 if self.feature <= 3 else 1)
        file.print_byte(len(self.cid_mappings))
        file.newline()
        for cargo, cid in self.cid_mappings:
            cargo.write(file, 1)
            file.print_wordx(cid)
            file.newline()
        file.print_wordx(self.def_cid)
        file.newline()
        file.newline()

    def skip_action7(self):
        return True

    def skip_action9(self):
        return False

    def skip_needed(self):
        return True

def parse_graphics_block(graphics_list, default_graphics, feature, id, is_livery_override = False):
    action_list = []
    act6 = Action6()
    if isinstance(id, ConstantNumeric):
        act3 = Action3(feature, id.value)
    else:
        tmp_param, tmp_param_actions = actionD.get_tmp_parameter(id)
        size = 3 if feature <= 3 else 1
        offset = 4 if feature <= 3 else 3
        act6.modify_bytes(tmp_param, size, offset)
        action_list.extend(tmp_param_actions)
        act3 = Action3(feature, 0)

    act3.is_livery_override = is_livery_override

    if default_graphics is None:
        act3.def_cid = 0
    else:
        action2.add_ref(default_graphics.value)
        act3.def_cid = default_graphics.value

    for graphics in graphics_list:
        action2.add_ref(graphics.action2_id.value)
        cargo_id = reduce_constant(graphics.cargo_id, [cargo_numbers])
        act3.cid_mappings.append( (cargo_id, graphics.action2_id.value) )

    if len(act6.modifications) > 0: action_list.append(act6)
    action_list.append(act3)

    return action_list
