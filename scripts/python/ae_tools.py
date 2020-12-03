import hou

# ========================
# Utils
# ========================

def get_all_hda_definitions():
    result = []
    for category in hou.nodeTypeCategories().values():
        for node_type in category.nodeTypes().values():
            definition = node_type.definition()
            if definition is None:
                continue
            if definition not in result:
                result.append(definition)
    return result

def filter_aelib_hdadefs(defs):
    return [d for d in defs if "ae::" in d.nodeTypeName()]

def get_aelib_hdadefs():
    alldefs = get_all_hda_definitions()
    return filter_aelib_hdadefs(alldefs)

def set_oncreated(defs):
    for d in defs:
        if "OnCreated" in defs.sections().keys():
            s = defs.sections["OnCreated"]
            oncr = s.contents()
            oncr += "\n"
            oncr += "#TEST"
            s.setContents(oncr)
        else:
            new_oncreated = d.addSection("OnCreated", contents="#TEST")

def camel_to_underscored(s):
    # doesnt convert lower case
    # dont use this.. dangerous
    return ''.join(['_'+c if c.isupper() else c for c in s]).lstrip('_')

def replace_underscored_in_hda_label_with_spaces(defs):
    for d in defs:
        des = d.description()
        # x = camel_to_underscored(des)
        # print(x)
        x = des.replace("_", " ")
        print(x)
        d.setDescription(x)
