import cadquery as cq

from components import make_pi_camera_v3_slide_mount

# Parameters
output_filename = "model.stl"

# Geometry
raw_result = make_pi_camera_v3_slide_mount(
    include_frame_interface=False,
    include_bottom_plate=True,
)

result = raw_result.rotate((0, 0, 0), (1, 0, 0), 180)
result = result.translate((0, 0, -result.BoundingBox().zmin))

# Export
cq.exporters.export(result, output_filename)

# CQ-editor compatibility
try:
    show_object(result)
except NameError:
    pass
