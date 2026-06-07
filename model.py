import cadquery as cq

from components import make_pcb_edge_post

# Parameters
output_filename = "model.stl"

# Components
components = [
    make_pcb_edge_post(),
]

# Geometry
result = cq.Compound.makeCompound(components)

# Export
cq.exporters.export(result, output_filename)

# CQ-editor compatibility
try:
    show_object(result)
except NameError:
    pass
