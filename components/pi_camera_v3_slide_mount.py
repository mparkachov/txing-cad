import cadquery as cq

from .pi_camera_v3_plate import (
    board_depth as pi_camera_v3_board_depth,
    board_thickness as pi_camera_v3_board_thickness,
    board_width as pi_camera_v3_board_width,
)

# Parameters
side_clearance = 0.35
slide_clearance = 0.35
board_thickness_clearance = 0.45

base_thickness = 1.2
rail_wall_thickness = 2.4
rail_lip_width = 1.2
rail_lip_thickness = 0.8
lead_in_length = 4.0

stop_depth = 2.4
stop_inset_width = 5.2
bottom_plate_depth = 7.0
bottom_plate_thickness = 2.0
bottom_plate_min_z = 2.0
bottom_plate_end_extension = 2.4

detent_protrusion = 0.0
detent_length = 2.4
detent_margin_from_top = 1.2

interface_strip_depth = 4.0


def _make_box(
    *,
    center_x: float,
    center_y: float,
    width: float,
    depth: float,
    height: float,
    z_min: float = 0.0,
) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center(center_x, center_y)
        .rect(width, depth)
        .extrude(height)
        .translate((0, 0, z_min))
    )


def _make_side_rail(
    *,
    side: int,
    channel_half_width: float,
    rail_center_y: float,
    rail_length: float,
    base_thickness: float,
    top_plate_z_min: float,
    rail_height: float,
    rail_wall_thickness: float,
    rail_lip_width: float,
    cut_overlap: float,
) -> cq.Workplane:
    rail_width = rail_wall_thickness + rail_lip_width
    rail_center_x = side * (channel_half_width + (rail_wall_thickness - rail_lip_width) / 2)
    channel_cut_center_x = side * (channel_half_width - rail_lip_width / 2)

    rail = _make_box(
        center_x=rail_center_x,
        center_y=rail_center_y,
        width=rail_width,
        depth=rail_length,
        height=rail_height,
    )

    channel_cut = _make_box(
        center_x=channel_cut_center_x,
        center_y=rail_center_y,
        width=rail_lip_width + 2 * cut_overlap,
        depth=rail_length + 2 * cut_overlap,
        height=top_plate_z_min - base_thickness + cut_overlap,
        z_min=base_thickness - cut_overlap,
    )
    rail = rail.cut(channel_cut)

    return rail


def make_pi_camera_v3_slide_mount(
    *,
    board_width: float = pi_camera_v3_board_width,
    board_depth: float = pi_camera_v3_board_depth,
    board_thickness: float = pi_camera_v3_board_thickness,
    side_clearance: float = side_clearance,
    slide_clearance: float = slide_clearance,
    board_thickness_clearance: float = board_thickness_clearance,
    base_thickness: float = base_thickness,
    rail_wall_thickness: float = rail_wall_thickness,
    rail_lip_width: float = rail_lip_width,
    rail_lip_thickness: float = rail_lip_thickness,
    rail_height: float | None = None,
    lead_in_length: float = lead_in_length,
    stop_depth: float = stop_depth,
    stop_inset_width: float = stop_inset_width,
    include_bottom_plate: bool = False,
    bottom_plate_depth: float = bottom_plate_depth,
    bottom_plate_thickness: float = bottom_plate_thickness,
    bottom_plate_min_z: float = bottom_plate_min_z,
    bottom_plate_end_extension: float = bottom_plate_end_extension,
    detent_protrusion: float = detent_protrusion,
    detent_length: float = detent_length,
    detent_margin_from_top: float = detent_margin_from_top,
    include_frame_interface: bool = True,
    include_stops: bool = True,
    interface_strip_depth: float = interface_strip_depth,
) -> cq.Shape:
    """Create a top-loading slide cradle for the Raspberry Pi Camera Module 3."""
    if board_width <= 0:
        raise ValueError("board_width must be positive")
    if board_depth <= 0:
        raise ValueError("board_depth must be positive")
    if board_thickness <= 0:
        raise ValueError("board_thickness must be positive")
    if side_clearance < 0:
        raise ValueError("side_clearance must not be negative")
    if slide_clearance < 0:
        raise ValueError("slide_clearance must not be negative")
    if board_thickness_clearance < 0:
        raise ValueError("board_thickness_clearance must not be negative")
    if base_thickness <= 0:
        raise ValueError("base_thickness must be positive")
    if rail_wall_thickness <= 0:
        raise ValueError("rail_wall_thickness must be positive")
    if rail_lip_width <= 0:
        raise ValueError("rail_lip_width must be positive")
    if rail_lip_thickness <= 0:
        raise ValueError("rail_lip_thickness must be positive")
    if lead_in_length < 0:
        raise ValueError("lead_in_length must not be negative")
    if stop_depth <= 0:
        raise ValueError("stop_depth must be positive")
    if stop_inset_width <= 0:
        raise ValueError("stop_inset_width must be positive")
    if bottom_plate_depth <= 0:
        raise ValueError("bottom_plate_depth must be positive")
    if bottom_plate_thickness <= 0:
        raise ValueError("bottom_plate_thickness must be positive")
    if bottom_plate_min_z < 0:
        raise ValueError("bottom_plate_min_z must not be negative")
    if bottom_plate_end_extension < 0:
        raise ValueError("bottom_plate_end_extension must not be negative")
    if detent_protrusion < 0:
        raise ValueError("detent_protrusion must not be negative")
    if detent_length <= 0:
        raise ValueError("detent_length must be positive")
    if detent_margin_from_top < 0:
        raise ValueError("detent_margin_from_top must not be negative")
    if interface_strip_depth <= 0:
        raise ValueError("interface_strip_depth must be positive")

    channel_width = board_width + 2 * side_clearance
    channel_depth = board_depth + 2 * slide_clearance
    channel_half_width = channel_width / 2
    channel_half_depth = channel_depth / 2
    board_channel_height = board_thickness + board_thickness_clearance

    if stop_inset_width * 2 >= channel_width:
        raise ValueError("stop_inset_width leaves no center ribbon opening")
    if detent_protrusion >= side_clearance and detent_protrusion > 0:
        raise ValueError("detent_protrusion must be smaller than side_clearance")

    channel_clearance_top_z = base_thickness + board_channel_height
    top_plate_z_min = channel_clearance_top_z
    top_plate_thickness = rail_lip_thickness
    if include_bottom_plate:
        top_plate_z_min = max(bottom_plate_min_z, channel_clearance_top_z)
        top_plate_thickness = max(top_plate_thickness, bottom_plate_thickness)
    minimum_rail_height = top_plate_z_min + top_plate_thickness
    if rail_height is None:
        rail_height = minimum_rail_height
    if rail_height < minimum_rail_height:
        raise ValueError("rail_height is too small for the board channel and top plate")

    mount_y_min = -channel_half_depth - stop_depth
    mount_y_max = channel_half_depth + lead_in_length
    y_offset = -(mount_y_min + mount_y_max) / 2

    channel_y_min = -channel_half_depth + y_offset
    channel_y_max = channel_half_depth + y_offset
    rail_y_min = channel_y_min
    rail_y_max = channel_y_max + lead_in_length
    rail_length = rail_y_max - rail_y_min
    rail_center_y = (rail_y_min + rail_y_max) / 2
    board_y_min = channel_y_min + slide_clearance

    mount_outer_width = channel_width + 2 * rail_wall_thickness
    cut_overlap = 0.05

    if interface_strip_depth > rail_length:
        raise ValueError("interface_strip_depth must not be longer than the slide rails")

    parts: list[cq.Shape] = []
    result: cq.Workplane | None = None

    if include_frame_interface:
        result = _make_box(
            center_x=0,
            center_y=rail_y_max - interface_strip_depth / 2,
            width=mount_outer_width,
            depth=interface_strip_depth,
            height=base_thickness,
        )

    if include_bottom_plate:
        bottom_plate_height = rail_height - top_plate_z_min
        effective_bottom_plate_depth = bottom_plate_depth + bottom_plate_end_extension
        bottom_plate = _make_box(
            center_x=0,
            center_y=rail_y_min - bottom_plate_end_extension + effective_bottom_plate_depth / 2,
            width=mount_outer_width,
            depth=effective_bottom_plate_depth,
            height=bottom_plate_height,
            z_min=top_plate_z_min,
        )
        if result is None:
            result = bottom_plate
        else:
            result = result.union(bottom_plate)

    for side in (-1, 1):
        rail = _make_side_rail(
            side=side,
            channel_half_width=channel_half_width,
            rail_center_y=rail_center_y,
            rail_length=rail_length,
            base_thickness=base_thickness,
            top_plate_z_min=top_plate_z_min,
            rail_height=rail_height,
            rail_wall_thickness=rail_wall_thickness,
            rail_lip_width=rail_lip_width,
            cut_overlap=cut_overlap,
        )

        if include_stops:
            stop_center_x = side * (channel_half_width + (rail_wall_thickness - stop_inset_width) / 2)
            stop = _make_box(
                center_x=stop_center_x,
                center_y=channel_y_min - stop_depth / 2,
                width=rail_wall_thickness + stop_inset_width,
                depth=stop_depth,
                height=rail_height,
            )
            rail = rail.union(stop)

        if detent_protrusion > 0:
            detent_center_x = side * (
                channel_half_width + (cut_overlap - detent_protrusion) / 2
            )
            detent_center_y = channel_y_max - detent_margin_from_top - detent_length / 2
            detent = _make_box(
                center_x=detent_center_x,
                center_y=detent_center_y,
                width=detent_protrusion + cut_overlap,
                depth=detent_length,
                height=board_channel_height,
                z_min=base_thickness,
            )
            rail = rail.union(detent)

        if result is None:
            parts.append(rail.val())
        else:
            result = result.union(rail)

    if result is not None:
        return result.val()

    if len(parts) == 1:
        return parts[0]

    return cq.Compound.makeCompound(parts)
