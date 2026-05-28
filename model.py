import cadquery as cq

# Parameters
square_size = 2.0
height = 1.0

# Geometry
result = (
    cq.Workplane("XY")
    .rect(square_size, square_size)
    .extrude(height)
)

# Export
cq.exporters.export(result, "model.stl")

# CQ-editor compatibility
try:
    show_object(result)
except NameError:
    pass
