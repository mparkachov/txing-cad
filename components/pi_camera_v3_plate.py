import cadquery as cq

# Raspberry Pi Camera Module 3 board dimensions from the official mechanical
# drawing. Camera Module 3 uses the Camera Module 2 board and mounting pattern.
board_width = 25.0
board_depth = 23.862
board_thickness = 1.12
plate_thickness = 2.0

# Small ABS shrinkage allowance for XY footprint and locator spacing.
abs_xy_scale = 1.006

camera_mount_hole_diameter = 2.2
connector_standoff_height = 2.75
pin_diameter = 2.15
pin_protrusion_above_board = 0.35
pin_height = connector_standoff_height + board_thickness + pin_protrusion_above_board
pin_tip_diameter = 1.65
pin_tip_height = 0.4
corner_radius = 2.0

support_bump_width = 5.0
support_bump_depth = 3.2
support_bump_height = connector_standoff_height - 1.0
support_bump_top_margin = 1.5

pin_centers_from_lower_left = (
    (2.0, 2.0),
    (23.0, 2.0),
    (2.0, 14.5),
    (23.0, 14.5),
)


def _make_pin(
    x: float,
    y: float,
    diameter: float,
    height: float,
    tip_diameter: float,
    tip_height: float,
) -> cq.Workplane:
    body_height = height - tip_height
    pin = cq.Workplane("XY").center(x, y).circle(diameter / 2).extrude(body_height)
    tip = (
        cq.Workplane("XY")
        .center(x, y)
        .circle(diameter / 2)
        .workplane(offset=tip_height)
        .circle(tip_diameter / 2)
        .loft()
        .translate((0, 0, body_height))
    )

    return pin.union(tip)


def _make_rounded_plate(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    if radius <= 0:
        return cq.Workplane("XY").rect(width, depth).extrude(height)

    max_radius = min(width, depth) / 2
    if radius > max_radius:
        raise ValueError("corner_radius is too large for the plate size")

    center_bar = cq.Workplane("XY").rect(width - 2 * radius, depth).extrude(height)
    cross_bar = cq.Workplane("XY").rect(width, depth - 2 * radius).extrude(height)
    plate = center_bar.union(cross_bar)

    corner_centers = (
        (-width / 2 + radius, -depth / 2 + radius),
        (width / 2 - radius, -depth / 2 + radius),
        (-width / 2 + radius, depth / 2 - radius),
        (width / 2 - radius, depth / 2 - radius),
    )

    for x, y in corner_centers:
        corner = cq.Workplane("XY").center(x, y).circle(radius).extrude(height)
        plate = plate.union(corner)

    return plate


def _center_from_lower_left(x: float, y: float, width: float, depth: float, scale: float) -> tuple[float, float]:
    return ((x - width / 2) * scale, (y - depth / 2) * scale)


def make_pi_camera_v3_plate(
    *,
    board_width: float = board_width,
    board_depth: float = board_depth,
    board_thickness: float = board_thickness,
    plate_thickness: float = plate_thickness,
    abs_xy_scale: float = abs_xy_scale,
    connector_standoff_height: float = connector_standoff_height,
    pin_diameter: float = pin_diameter,
    pin_height: float | None = None,
    pin_protrusion_above_board: float = pin_protrusion_above_board,
    pin_tip_diameter: float = pin_tip_diameter,
    pin_tip_height: float = pin_tip_height,
    corner_radius: float = corner_radius,
    support_bump_width: float = support_bump_width,
    support_bump_depth: float = support_bump_depth,
    support_bump_height: float = support_bump_height,
    support_bump_top_margin: float = support_bump_top_margin,
) -> cq.Shape:
    """Create a snug locator plate for the Raspberry Pi Camera Module 3."""
    if plate_thickness <= 0:
        raise ValueError("plate_thickness must be positive")
    if board_thickness <= 0:
        raise ValueError("board_thickness must be positive")
    if connector_standoff_height <= 0:
        raise ValueError("connector_standoff_height must be positive")
    if pin_diameter <= 0:
        raise ValueError("pin_diameter must be positive")
    if pin_diameter >= camera_mount_hole_diameter:
        raise ValueError("pin_diameter must be smaller than camera_mount_hole_diameter")
    if pin_tip_diameter <= 0:
        raise ValueError("pin_tip_diameter must be positive")
    if pin_tip_diameter > pin_diameter:
        raise ValueError("pin_tip_diameter must not be larger than pin_diameter")
    if pin_tip_height < 0:
        raise ValueError("pin_tip_height must not be negative")
    if pin_height is None:
        pin_height = connector_standoff_height + board_thickness + pin_protrusion_above_board
    if pin_height <= 0:
        raise ValueError("pin_height must be positive")
    if pin_tip_height >= pin_height:
        raise ValueError("pin_tip_height must be smaller than pin_height")
    if abs_xy_scale <= 0:
        raise ValueError("abs_xy_scale must be positive")
    if support_bump_width <= 0:
        raise ValueError("support_bump_width must be positive")
    if support_bump_depth <= 0:
        raise ValueError("support_bump_depth must be positive")
    if support_bump_height <= 0:
        raise ValueError("support_bump_height must be positive")

    plate_width = board_width * abs_xy_scale
    plate_depth = board_depth * abs_xy_scale
    scaled_corner_radius = corner_radius * abs_xy_scale

    result = _make_rounded_plate(
        width=plate_width,
        depth=plate_depth,
        height=plate_thickness,
        radius=scaled_corner_radius,
    )

    pin_overlap = 0.05
    support_bump_center_from_lower_left = (
        board_width / 2,
        support_bump_top_margin + support_bump_depth / 2,
    )

    bump_x, bump_y = _center_from_lower_left(
        x=support_bump_center_from_lower_left[0],
        y=support_bump_center_from_lower_left[1],
        width=board_width,
        depth=board_depth,
        scale=abs_xy_scale,
    )
    bump = (
        cq.Workplane("XY")
        .center(bump_x, bump_y)
        .rect(support_bump_width * abs_xy_scale, support_bump_depth * abs_xy_scale)
        .extrude(support_bump_height + pin_overlap)
        .translate((0, 0, plate_thickness - pin_overlap))
    )
    result = result.union(bump)

    for x, y in pin_centers_from_lower_left:
        pin_x, pin_y = _center_from_lower_left(
            x=x,
            y=y,
            width=board_width,
            depth=board_depth,
            scale=abs_xy_scale,
        )
        pin = _make_pin(
            x=pin_x,
            y=pin_y,
            diameter=pin_diameter,
            height=pin_height + pin_overlap,
            tip_diameter=pin_tip_diameter,
            tip_height=pin_tip_height,
        ).translate((0, 0, plate_thickness - pin_overlap))
        result = result.union(pin)

    return result.val()
