import cadquery as cq

from .pcb_edge_post import (
    make_pcb_edge_post,
    overall_width as default_overall_width,
    pcb_clearance as default_pcb_clearance,
    pcb_thickness as default_pcb_thickness,
    post_length as default_post_length,
    post_thickness as default_post_thickness,
    post_width as default_post_width,
    slot_angle_degrees as default_slot_angle_degrees,
    slot_depth as default_slot_depth,
    height_above_pcb_top as default_height_above_pcb_top,
)
from .pi_camera_v3_plate import (
    board_thickness as default_camera_board_thickness,
    board_width as default_camera_board_width,
)
from .pi_camera_v3_slide_mount import (
    board_thickness_clearance as default_camera_board_thickness_clearance,
    make_pi_camera_v3_slide_mount,
    side_clearance as default_camera_side_clearance,
)

# Parameters
camera_mount_overlap = 0.2
camera_entry_extra_clearance = 0.8
camera_attachment_pad_length = 0.0
camera_attachment_pad_width = 4.0


def _orient_camera_mount_for_frame(camera_mount: cq.Shape) -> cq.Shape:
    """Keep the camera face up and put the slide entry at the frame top bridge."""
    return camera_mount.rotate((0, 0, 0), (0, 0, 1), -90)


def _put_top_side_on_bed(shape: cq.Shape, height: float) -> cq.Shape:
    result = shape.rotate((0, 0, 0), (1, 0, 0), 180)
    return result.translate((0, 0, height))


def _make_camera_attachment_pads(
    *,
    frame_x_max: float,
    overall_width: float,
    entry_slot_width: float,
    pad_length: float,
    pad_width: float,
    height: float,
) -> cq.Workplane | None:
    if pad_length == 0:
        return None

    if pad_length < 0:
        raise ValueError("camera_attachment_pad_length must not be negative")
    if pad_width <= 0:
        raise ValueError("camera_attachment_pad_width must be positive")
    if height <= 0:
        raise ValueError("camera attachment pad height must be positive")
    if entry_slot_width >= overall_width:
        raise ValueError("camera entry slot leaves no room for attachment pads")

    pad_inner_y = entry_slot_width / 2
    pad_outer_y = overall_width / 2
    if pad_inner_y + pad_width > pad_outer_y:
        raise ValueError("camera_attachment_pad_width is wider than the frame side area")

    pad_center_x = frame_x_max - pad_length / 2

    pads: cq.Workplane | None = None
    for side in (-1, 1):
        pad = (
            cq.Workplane("XY")
            .center(pad_center_x, side * (pad_inner_y + pad_width / 2))
            .rect(pad_length, pad_width)
            .extrude(height)
        )
        if pads is None:
            pads = pad
        else:
            pads = pads.union(pad)

    return pads


def make_pcb_edge_camera_mount(
    *,
    post_width: float = default_post_width,
    post_thickness: float = default_post_thickness,
    post_length: float = default_post_length,
    overall_width: float = default_overall_width,
    height_above_pcb_top: float = default_height_above_pcb_top,
    pcb_thickness: float = default_pcb_thickness,
    pcb_clearance: float = default_pcb_clearance,
    slot_depth: float = default_slot_depth,
    slot_angle_degrees: float = default_slot_angle_degrees,
    camera_board_width: float = default_camera_board_width,
    camera_board_thickness: float = default_camera_board_thickness,
    camera_board_thickness_clearance: float = default_camera_board_thickness_clearance,
    camera_side_clearance: float = default_camera_side_clearance,
    camera_mount_height: float | None = None,
    camera_y_center: float = 0.0,
    top_side_on_bed: bool = True,
    camera_mount_overlap: float = camera_mount_overlap,
    camera_entry_extra_clearance: float = camera_entry_extra_clearance,
    camera_attachment_pad_length: float = camera_attachment_pad_length,
    camera_attachment_pad_width: float = camera_attachment_pad_width,
) -> cq.Shape:
    """Create the PCB edge frame with the validated top-loading camera rails."""
    if camera_board_width <= 0:
        raise ValueError("camera_board_width must be positive")
    if camera_board_thickness <= 0:
        raise ValueError("camera_board_thickness must be positive")
    if camera_board_thickness_clearance < 0:
        raise ValueError("camera_board_thickness_clearance must not be negative")
    if camera_side_clearance < 0:
        raise ValueError("camera_side_clearance must not be negative")
    if camera_mount_overlap < 0:
        raise ValueError("camera_mount_overlap must not be negative")
    if camera_entry_extra_clearance < 0:
        raise ValueError("camera_entry_extra_clearance must not be negative")
    if camera_attachment_pad_length < 0:
        raise ValueError("camera_attachment_pad_length must not be negative")
    if camera_attachment_pad_width <= 0:
        raise ValueError("camera_attachment_pad_width must be positive")
    if camera_mount_height is None:
        camera_mount_height = post_thickness
    if camera_mount_height <= 0:
        raise ValueError("camera_mount_height must be positive")

    camera_channel_height = camera_board_thickness + camera_board_thickness_clearance
    if camera_channel_height >= camera_mount_height:
        raise ValueError("camera_mount_height must be larger than the camera board channel")
    camera_base_thickness = (camera_mount_height - camera_channel_height) / 2

    frame = make_pcb_edge_post(
        post_width=post_width,
        post_thickness=post_thickness,
        post_length=post_length,
        overall_width=overall_width,
        height_above_pcb_top=height_above_pcb_top,
        pcb_thickness=pcb_thickness,
        pcb_clearance=pcb_clearance,
        slot_depth=slot_depth,
        slot_angle_degrees=slot_angle_degrees,
    )

    camera_mount = make_pi_camera_v3_slide_mount(
        board_thickness=camera_board_thickness,
        board_thickness_clearance=camera_board_thickness_clearance,
        base_thickness=camera_base_thickness,
        rail_height=camera_mount_height,
        include_frame_interface=False,
        include_bottom_plate=True,
    )
    camera_mount = _orient_camera_mount_for_frame(camera_mount)

    frame_x_max = post_length / 2
    target_camera_x_max = frame_x_max

    camera_bb = camera_mount.BoundingBox()
    camera_center_y = (camera_bb.ymin + camera_bb.ymax) / 2
    camera_mount = camera_mount.translate(
        (
            target_camera_x_max - camera_bb.xmax,
            camera_y_center - camera_center_y,
            0,
        )
    )

    cut_overlap = 0.2
    entry_slot_width = (
        camera_board_width
        + 2 * camera_side_clearance
        + camera_entry_extra_clearance
    )
    entry_slot = (
        cq.Workplane("XY")
        .center(frame_x_max - post_width / 2, camera_y_center)
        .rect(post_width + 2 * camera_mount_overlap, entry_slot_width)
        .extrude(post_thickness + 2 * cut_overlap)
        .translate((0, 0, -cut_overlap))
    )

    frame = cq.Workplane("XY").add(frame).cut(entry_slot).val()
    attachment_pads = _make_camera_attachment_pads(
        frame_x_max=frame_x_max,
        overall_width=overall_width,
        entry_slot_width=entry_slot_width,
        pad_length=camera_attachment_pad_length,
        pad_width=camera_attachment_pad_width,
        height=min(post_thickness, camera_mount_height),
    )

    if top_side_on_bed:
        frame = _put_top_side_on_bed(frame, post_thickness)
        camera_mount = _put_top_side_on_bed(camera_mount, camera_mount_height)
        if attachment_pads is not None:
            attachment_pads = cq.Workplane("XY").add(
                _put_top_side_on_bed(attachment_pads.val(), min(post_thickness, camera_mount_height))
            )

    result = cq.Workplane("XY").add(frame).union(cq.Workplane("XY").add(camera_mount))
    if attachment_pads is not None:
        result = result.union(attachment_pads)

    return result.val()
