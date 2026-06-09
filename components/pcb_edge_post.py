import math

import cadquery as cq

# Parameters
post_width = 4.0
post_thickness = 7.0
post_length = 66.5
overall_width = 50.0

height_above_pcb_top = 62.0
pcb_thickness = 1.4
pcb_clearance = 0.2
slot_depth = 5.0
slot_angle_degrees = 83.0


def _make_slotted_post(
    *,
    post_width: float = post_width,
    post_thickness: float = post_thickness,
    post_length: float = post_length,
    height_above_pcb_top: float = height_above_pcb_top,
    pcb_thickness: float = pcb_thickness,
    pcb_clearance: float = pcb_clearance,
    slot_depth: float = slot_depth,
    slot_angle_degrees: float = slot_angle_degrees,
) -> cq.Workplane:
    """Create one horizontal-print post with a top slot for a PCB edge."""
    if post_width <= 0:
        raise ValueError("post_width must be positive")
    if post_thickness <= 0:
        raise ValueError("post_thickness must be positive")
    if post_length <= 0:
        raise ValueError("post_length must be positive")
    if height_above_pcb_top <= 0:
        raise ValueError("height_above_pcb_top must be positive")
    if height_above_pcb_top >= post_length:
        raise ValueError("height_above_pcb_top must be smaller than post_length")
    if pcb_thickness <= 0:
        raise ValueError("pcb_thickness must be positive")
    if pcb_clearance < 0:
        raise ValueError("pcb_clearance must not be negative")
    if slot_depth <= 0:
        raise ValueError("slot_depth must be positive")
    if slot_depth >= post_thickness:
        raise ValueError("slot_depth must be smaller than post_thickness")
    if slot_angle_degrees <= 0 or slot_angle_degrees > 90:
        raise ValueError("slot_angle_degrees must be greater than 0 and no more than 90")

    slot_gap = pcb_thickness + pcb_clearance
    lower_end_to_pcb_top = post_length - height_above_pcb_top
    angle_radians = math.radians(slot_angle_degrees)
    slot_direction_x = -math.cos(angle_radians)
    slot_direction_z = -math.sin(angle_radians)
    slot_length = slot_depth / abs(slot_direction_z)
    slot_drop = slot_length * -slot_direction_x
    lower_lip_height = lower_end_to_pcb_top - slot_drop - slot_gap

    if lower_lip_height <= 0:
        raise ValueError("PCB slot leaves no material at the lower end")

    cut_overlap = 0.2
    lower_end_x = -post_length / 2
    slot_top_x = lower_end_x + lower_end_to_pcb_top
    slot_top_z = post_thickness
    outer_extension = cut_overlap / abs(slot_direction_z)

    top_outer = (
        slot_top_x - slot_direction_x * outer_extension,
        slot_top_z + cut_overlap,
    )
    top_inner = (
        slot_top_x + slot_direction_x * slot_length,
        slot_top_z + slot_direction_z * slot_length,
    )
    bottom_inner = (
        top_inner[0] - slot_gap,
        top_inner[1],
    )
    bottom_outer = (
        top_outer[0] - slot_gap,
        top_outer[1],
    )

    body = (
        cq.Workplane("XY")
        .rect(post_length, post_width)
        .extrude(post_thickness)
    )

    slot_cut = (
        cq.Workplane("XZ")
        .polyline([top_outer, top_inner, bottom_inner, bottom_outer])
        .close()
        .extrude(post_width + 2 * cut_overlap)
        .translate((0, post_width / 2 + cut_overlap, 0))
    )

    return body.cut(slot_cut)


def _make_slot_cut(
    *,
    rail_center_y: float,
    post_width: float = post_width,
    post_thickness: float = post_thickness,
    post_length: float = post_length,
    height_above_pcb_top: float = height_above_pcb_top,
    pcb_thickness: float = pcb_thickness,
    pcb_clearance: float = pcb_clearance,
    slot_depth: float = slot_depth,
    slot_angle_degrees: float = slot_angle_degrees,
) -> cq.Workplane:
    slot_gap = pcb_thickness + pcb_clearance
    lower_end_to_pcb_top = post_length - height_above_pcb_top
    angle_radians = math.radians(slot_angle_degrees)
    slot_direction_x = -math.cos(angle_radians)
    slot_direction_z = -math.sin(angle_radians)
    slot_length = slot_depth / abs(slot_direction_z)

    cut_overlap = 0.2
    lower_end_x = -post_length / 2
    slot_top_x = lower_end_x + lower_end_to_pcb_top
    slot_top_z = post_thickness
    outer_extension = cut_overlap / abs(slot_direction_z)

    top_outer = (
        slot_top_x - slot_direction_x * outer_extension,
        slot_top_z + cut_overlap,
    )
    top_inner = (
        slot_top_x + slot_direction_x * slot_length,
        slot_top_z + slot_direction_z * slot_length,
    )
    bottom_inner = (
        top_inner[0] - slot_gap,
        top_inner[1],
    )
    bottom_outer = (
        top_outer[0] - slot_gap,
        top_outer[1],
    )

    return (
        cq.Workplane("XZ")
        .polyline([top_outer, top_inner, bottom_inner, bottom_outer])
        .close()
        .extrude(post_width + 2 * cut_overlap)
        .translate((0, rail_center_y + post_width / 2 + cut_overlap, 0))
    )


def make_pcb_edge_post(
    *,
    post_width: float = post_width,
    post_thickness: float = post_thickness,
    post_length: float = post_length,
    overall_width: float = overall_width,
    height_above_pcb_top: float = height_above_pcb_top,
    pcb_thickness: float = pcb_thickness,
    pcb_clearance: float = pcb_clearance,
    slot_depth: float = slot_depth,
    slot_angle_degrees: float = slot_angle_degrees,
) -> cq.Shape:
    """Create two parallel slotted posts joined at the top end."""
    if overall_width <= post_width:
        raise ValueError("overall_width must be larger than post_width")
    if post_length <= post_width:
        raise ValueError("post_length must be larger than post_width")
    if post_thickness <= 0:
        raise ValueError("post_thickness must be positive")

    rail_center_y = (overall_width - post_width) / 2
    bridge_width = post_width

    cut_overlap = 0.2
    outer = (
        cq.Workplane("XY")
        .rect(post_length, overall_width)
        .extrude(post_thickness)
    )

    outer_x_min = -post_length / 2
    bridge_x_min = post_length / 2 - bridge_width
    inner_length = bridge_x_min - outer_x_min + cut_overlap
    inner_center_x = (bridge_x_min + outer_x_min - cut_overlap) / 2
    inner_width = overall_width - 2 * post_width

    inner_cut = (
        cq.Workplane("XY")
        .center(inner_center_x, 0)
        .rect(inner_length, inner_width)
        .extrude(post_thickness + 2 * cut_overlap)
        .translate((0, 0, -cut_overlap))
    )

    result = outer.cut(inner_cut)

    for y in (-rail_center_y, rail_center_y):
        result = result.cut(
            _make_slot_cut(
                rail_center_y=y,
                post_width=post_width,
                post_thickness=post_thickness,
                post_length=post_length,
                height_above_pcb_top=height_above_pcb_top,
                pcb_thickness=pcb_thickness,
                pcb_clearance=pcb_clearance,
                slot_depth=slot_depth,
                slot_angle_degrees=slot_angle_degrees,
            )
        )

    return result.val()
