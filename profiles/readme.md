# UP3D profile notes

This directory contains slicer profiles for the UP Mini style workflow:

```text
CadQuery -> STL -> PrusaSlicer CLI -> G-code -> up3dtranscode -> up3dload
```

These notes record physical print findings from the PCB edge post tests on
2026-06-06 and 2026-06-07. They are practical settings for this workflow, not
generic Prusa recommendations.

## Important constraints

The printer and UP3D transcoder handle simple G-code much more reliably than
modern, highly optimized PrusaSlicer output.

Keep the profile conservative in the type of generated paths:

- Use `perimeter_generator = classic`.
- Keep arcs disabled.
- Use absolute extrusion with `M82`; avoid relative extrusion mode `M83`.
- Avoid firmware-specific commands that UP3D does not understand.
- Avoid E-only extrusion moves in printable G-code.
- Avoid retracts for now.
- Avoid gap-fill for now.
- Avoid dense internal solid/infill paths until they are tested separately.

The print failures seen before these changes looked like the printer was still
running or blinking, but motion/extrusion stopped mid-print. The same pipeline
printed a simple model successfully, so the issue was isolated to the generated
path style/complexity rather than upload or model generation in general.

## Proven successful sequence

The following physical tests completed successfully:

1. One perimeter shell only:
   - `perimeters = 1`
   - `fill_density = 0%`
   - `top_solid_layers = 0`
   - `bottom_solid_layers = 0`
   - `gap_fill_enabled = 0`
   - `retract_length = 0`
   - slow perimeter/travel speeds

2. Two perimeter shell:
   - `perimeters = 2`
   - still no infill, no top/bottom solid fill, no gap-fill, no retract

3. Faster two perimeter shell:
   - perimeter speeds increased to 15 mm/s
   - travel increased to 30 mm/s

4. Fast two perimeter shell:
   - `perimeter_speed = 30`
   - `external_perimeter_speed = 25`
   - `small_perimeter_speed = 25`
   - `travel_speed = 50`

5. Earlier fast speed profile:
   - `first_layer_speed = 20`
   - `perimeter_speed = 30`
   - `external_perimeter_speed = 30`
   - `small_perimeter_speed = 30`
   - `infill_speed = 35`
   - `solid_infill_speed = 35`
   - `top_solid_infill_speed = 35`
   - `travel_speed = 100`

Step 5 also completed successfully. This suggests speed itself is not the main
problem for this part and workflow.

6. Three perimeter shell:
   - `perimeters = 3`
   - same fixed speed profile as step 5
   - still no infill, no top/bottom solid fill, no gap-fill, no retract

Step 6 completed successfully and was the first good physical baseline. The
part already looked acceptable at this point, so heavier strength settings are
not required unless a later use case needs them.

7. Three perimeters with light rectilinear infill:
   - `perimeters = 3`
   - `fill_density = 5%`
   - `fill_pattern = rectilinear`
   - still no top/bottom solid fill, no gap-fill, no retract

Step 7 completed successfully, but the part was visibly too light. Treat it as
a proof that simple rectilinear infill works, not as a good final density.

8. Three perimeters with 20% rectilinear infill:
   - `perimeters = 3`
   - `fill_density = 20%`
   - `fill_pattern = rectilinear`
   - still no top/bottom solid fill, no gap-fill, no retract

Step 8 completed successfully. This is the first acceptable filled profile.

9. Three perimeters with 20% gyroid infill at fine G-code resolution:
   - `perimeters = 3`
   - `fill_density = 20%`
   - `fill_pattern = gyroid`
   - `gcode_resolution = 0.0125`
   - still no top/bottom solid fill, no gap-fill, no retract

Step 9 failed twice, consistently hanging around 1 mm of printed height. The
first layer also looked shifted or disturbed. Because 20% rectilinear worked at
the same speed and density, the failure is likely related to Gyroid path shape
or microsegment complexity rather than speed alone.

10. Three perimeters with 20% gyroid infill at coarse G-code resolution:
   - `perimeters = 3`
   - `fill_density = 20%`
   - `fill_pattern = gyroid`
   - `gcode_resolution = 0.2`
   - still no top/bottom solid fill, no gap-fill, no retract

Step 10 completed successfully. This strongly suggests the failed fine-Gyroid
test was caused by microsegment complexity, not by Gyroid density or speed
alone.

11. Three perimeters with 15% gyroid infill at coarse G-code resolution:
   - `perimeters = 3`
   - `fill_density = 15%`
   - `fill_pattern = gyroid`
   - `gcode_resolution = 0.2`
   - `layer_height = 0.3`
   - still no top/bottom solid fill, no gap-fill, no retract

Step 11 printed but was mechanically broken. The bottom was uneven, upper
layers shifted relative to lower layers, and previous samples broke cleanly
between layers. This points to weak inter-layer bonding rather than planner
failure.

Reviewing the early perimeter-only prints showed no visible warping. That
suggests the bending is not basic bed adhesion failure. The more likely cause is
ABS shrinkage from infill pulling against the long, thin perimeter rails.

12. Stress-relief attempt with hotter extrusion and softer infill connection:
   - `fill_density = 15%`
   - `fill_pattern = gyroid`
   - `layer_height = 0.25`
   - `temperature = 260`
   - `first_layer_temperature = 260`
   - `extrusion_multiplier = 1.05`
   - `infill_overlap = 10%`
   - `infill_anchor = 1.5`
   - `infill_anchor_max = 8`

Step 12 became much worse. Extra heat/flow and softer infill anchoring did not
fix layer bonding; it increased deformation. Do not continue in that direction.

13. Two perimeters with 15% Gyroid at coarse G-code resolution:
   - `perimeters = 2`
   - `fill_density = 15%`
   - `fill_pattern = gyroid`
   - `gcode_resolution = 0.2`
   - `first_layer_height = 0.3`
   - `layer_height = 0.3`
   - `temperature = 260`
   - `first_layer_temperature = 260`
   - `extrusion_multiplier = 1`
   - `infill_overlap = 25%`
   - `infill_anchor = 600%`
   - `infill_anchor_max = 50`
   - `top_solid_layers = 0`
   - `bottom_solid_layers = 0`
   - `gap_fill_enabled = 0`
   - `retract_length = 0`
   - direct PrusaSlicer G-code, no legacy post-processor

Step 13 completed successfully. This is the current confirmed baseline. The
main difference from the mechanically failed 15% Gyroid tests is reduced shell
load: `perimeters` went from `3` to `2`. That reduced path count and likely
reduced ABS shrink stress in the long rails. The successful result also shows
that speed alone was not the failure trigger.

## Current confirmed baseline

The current `profiles/up3d.ini` successful print uses:

```ini
perimeter_generator = classic
arc_fitting = disabled
use_relative_e_distances = 0
retract_length = 0
gap_fill_enabled = 0
thin_walls = 1

perimeters = 2
fill_density = 15%
fill_pattern = gyroid
gcode_resolution = 0.2

first_layer_height = 0.3
layer_height = 0.3

temperature = 260
first_layer_temperature = 260
bed_temperature = 100
first_layer_bed_temperature = 100
extrusion_multiplier = 1

infill_overlap = 25%
infill_anchor = 600%
infill_anchor_max = 50

top_solid_layers = 0
bottom_solid_layers = 0

cooling = 0
max_fan_speed = 0
```

The current speed settings are intentionally no longer capped at `30 mm/s`:

```ini
first_layer_speed = 20
perimeter_speed = 30
external_perimeter_speed = 30
small_perimeter_speed = 30
infill_speed = 35
solid_infill_speed = 30
top_solid_infill_speed = 30
travel_speed = 80
max_print_speed = 80
bridge_speed = 25
gap_fill_speed = 20
```

Generated G-code from this profile contains these feedrates:

```text
F90, F480, F600, F1200, F1500, F1800, F2100, F3000, F4800
```

The successful print confirms that `F3000` positioning moves are acceptable on
this printer for this part. The current profile also emits `F4800` travel moves
from `travel_speed = 80`; those did not cause the observed historical stall in
this successful test. Continue treating path complexity and internal shrink
stress as higher-risk than travel speed alone.

## Start G-code note

The start prime was changed to avoid an E-only prime command:

```gcode
G1 X85 E9.0 F480
G92 E0
G1 X86 E0.45 F90
G4 P250
G92 E0
```

This keeps extrusion paired with XY motion. The temporary legacy G-code
post-processor was removed after testing showed it did not address the printer
stall; the current pipeline uses PrusaSlicer output directly.

## Metrics from successful generated files

Approximate transcode metrics observed during tuning:

| Profile stage | Estimated time | G-code size | UMC size | MoveL blocks | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 perimeter, slow | 23m39s | 11 KB | 16 KB | 580 | success |
| 2 perimeters, slow | 37m16s | 23 KB | 28 KB | 1184 | success |
| 2 perimeters, 15 mm/s | 27m45s | 23 KB | 29 KB | 1268 | success |
| 2 perimeters, fast | 19m20s | 24 KB | 50 KB | 2337 | success |
| earlier fast speed profile | 17m24s | 24 KB | 52 KB | 2403 | success |
| 3 perimeters, fixed speed | 21m58s | 35 KB | 74 KB | 3553 | success |
| 3 perimeters + 5% rectilinear infill | 24m25s | 63 KB | 113 KB | 5569 | success, too light |
| 3 perimeters + 20% rectilinear infill | 25m56s | 135 KB | 209 KB | 10442 | success |
| 3 perimeters + 20% gyroid infill, `gcode_resolution = 0.0125` | 25m22s | 287 KB | 318 KB | 16050 | failed near 1 mm |
| 3 perimeters + 20% gyroid infill, `gcode_resolution = 0.2` | 25m16s | 116 KB | 205 KB | 10260 | success |
| 3 perimeters + 15% gyroid infill, `gcode_resolution = 0.2`, `layer_height = 0.3` | 25m36s | 92 KB | 160 KB | 7956 | mechanical failure |
| 3 perimeters + 15% gyroid infill, `gcode_resolution = 0.2`, `layer_height = 0.25` | 28m41s | 118 KB | 195 KB | 9738 | warped / layer lines visible |
| 15% gyroid, layer 0.25, 260 C, 1.05 flow, softer infill connection | 28m35s | 117 KB | 192 KB | 9559 | worse deformation |
| 2 perimeters + 15% gyroid infill, faster travel, direct Prusa G-code | 14m59s | 120 KB | not measured | not measured | success |
| 3 perimeters + 15% rectilinear infill | not transcoded | 111 KB | not measured | not measured | pending |

All successful tuned profiles had:

- `E-only G1 = 0`
- no extrusion drops/retract-like E decreases in generated print moves
- no top/bottom solid fill or gap-fill through the current two-perimeter 15%
  Gyroid baseline

## Subtle-path risk settings

The printer appears sensitive to small features and very fine motion
segmentation. Settings that can reintroduce that risk should be changed one at
a time:

- `layer_height`: lowering from `0.3` to `0.25` did not fix the mechanical
  problem on Gyroid and added more layers. Keep `0.3` as the baseline.
- `temperature`, `first_layer_temperature`, and `extrusion_multiplier`: `260 C`
  with `1.05` flow made deformation worse, but `260 C` with `1.0` flow worked in
  the two-perimeter baseline. Do not combine hotter extrusion with extra flow
  unless there is a specific reason to retest bonding.
- `infill_overlap`, `infill_anchor`, and `infill_anchor_max`: reducing these
  did not help in the hotter Gyroid test. Keep the known successful values:
  `25%`, `600%`, and `50`.
- `gcode_resolution`: keep at `0.2` for Gyroid or other curved patterns. Fine
  values such as `0.0125` can generate too many small segments for this
  workflow.
- `perimeter_generator`: keep `classic`; avoid `arachne` while tuning because
  variable-width paths can create subtle thin features.
- `gap_fill_enabled`: keep disabled until late testing; gap fill tends to create
  many short moves.
- `ensure_vertical_shell_thickness` and `extra_perimeters`: keep disabled unless
  a specific wall problem appears; both can add unexpected local paths.
- `thin_walls`: already successful as-is, but treat it as a risk setting if
  narrow geometry starts causing unstable paths.
- `top_solid_layers` and `bottom_solid_layers`: test separately because solid
  fill adds dense rectilinear passes on narrow rails.

## Top and bottom strategy

Earlier dry-run metrics for the three-perimeter 15% coarse Gyroid test at
`layer_height = 0.3` showed these candidates:

| Top/bottom setting | Estimated time | G-code size | UMC size | MoveL blocks |
| --- | ---: | ---: | ---: | ---: |
| `bottom_solid_layers = 0`, `top_solid_layers = 0` | 25m36s | 92 KB | 160 KB | 7956 |
| `bottom_solid_layers = 1`, `top_solid_layers = 0` | 26m03s | 110 KB | 184 KB | 9202 |
| `bottom_solid_layers = 0`, `top_solid_layers = 1` | 25m54s | 112 KB | 184 KB | 9212 |
| `bottom_solid_layers = 1`, `top_solid_layers = 1` | 26m20s | 129 KB | 209 KB | 10458 |
| `bottom_solid_layers = 1`, `top_solid_layers = 2` | 26m43s | 131 KB | 211 KB | 10573 |

Recommended order:

1. Keep the current two-perimeter 15% Gyroid profile as the baseline.
2. Then test `bottom_solid_layers = 1`, `top_solid_layers = 0` only if the
   baseline stays flat. This improves bed contact and bottom continuity without
   testing top bridging yet.
3. If that succeeds and a closed top is needed, test
   `bottom_solid_layers = 1`, `top_solid_layers = 1`.
4. Use `top_solid_layers = 2` only if one top layer looks too open. With the
   current `layer_height = 0.3`, two top layers give about 0.6 mm of solid cap.
5. Keep `gap_fill_enabled = 0` throughout these tests.

## Suggested next tuning order

Do not re-enable every quality/strength setting at once. Restore one source of
path complexity at a time and check the generated/transcoded file before
printing.

Recommended next experiments:

1. Keep the current two-perimeter 15% Gyroid profile as the known-good baseline.
2. If it remains flat, proceed to `bottom_solid_layers = 1`.
3. If a later change bends the part again, treat that change as adding internal
   shrink stress or path complexity; revert to this baseline before testing the
   next variable.
4. If it bonds well and shape is acceptable, test `top_solid_layers = 1` only if
   a closed top is needed.
5. Test `gap_fill_enabled = 1` last, because gap-fill tends to create many
   short segments.

For each generated file, check at least:

```text
G1 count
UMC MoveL count
E-only G1 count
extrusion drops/retract-like moves
transcoded UMC size
up3dtranscode estimated time
```
