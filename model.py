import cadquery as cq

from components import make_pcb_edge_camera_mount

# Parameters
output_filename = "model.stl"

# Geometry
result = make_pcb_edge_camera_mount()

# Export
cq.exporters.export(result, output_filename)

# CQ-editor compatibility
try:
    show_object(result)
except NameError:
    pass
