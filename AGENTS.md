# AGENTS.md

## Purpose

This repository is used to generate 3D-printable parts from natural-language descriptions using CadQuery, then export STL files for slicing and printing.

The user should be able to describe what they want in plain language. The agent should turn that into clean, robust, parametric CadQuery code without requiring the user to specify low-level CadQuery details.

## Default modeling assumptions

Unless the user says otherwise:

- Units are millimeters.
- The model is intended for FDM 3D printing.
- The printer uses a 0.4 mm nozzle.
- Prefer robust, simple geometry over clever or fragile constructions.
- The bottom of printable parts should sit on `Z = 0`.
- Center parts on the XY origin unless placement relative to another feature is explicitly requested.
- Export an STL file.
- Code must run both:
  - inside CQ-editor, where `show_object()` exists
  - headlessly with `uv run python model.py`, where `show_object()` does not exist

Use this compatibility pattern:

```python
try:
    show_object(result)
except NameError:
    pass
```

## CadQuery coding style

Prefer:

- named parameters at the top of the file
- readable construction steps
- sketches, rectangles, circles, extrusions, fillets, and simple cuts
- explicit variable names such as `outer_width`, `wall_thickness`, `hole_diameter`
- `cq.Workplane("XY").rect(...).extrude(...)` for printable flat-base objects
- bottom face on `Z = 0`

Avoid unless necessary:

- unnecessary boolean complexity
- fragile chained selectors
- hardcoded magic numbers buried in the code
- models centered around `Z = 0` when they are meant to be printed
- topology-sensitive selector chains that will break after small parameter changes

## Standard file structure for generated scripts

A generated CadQuery script should usually follow this shape:

```python
import cadquery as cq

# Parameters
width = 20.0
depth = 20.0
height = 1.0

# Geometry
result = (
    cq.Workplane("XY")
    .rect(width, depth)
    .extrude(height)
)

# Export
cq.exporters.export(result, "part.stl")

# CQ-editor compatibility
try:
    show_object(result)
except NameError:
    pass
```

## Interpreting natural-language model requests

When the user gives a simple request, infer reasonable manufacturing details.

Example user request:

> make a 20x20 square frame, 1 mm high

Generate a parametric CadQuery model with:

- outer size 20 x 20 mm
- height 1 mm
- default wall thickness if not specified, usually 2 mm
- centered on XY origin
- bottom on Z = 0
- STL export

Do not force the user to specify CadQuery implementation details.

## Ask clarification only when required

Ask a follow-up question only if the missing information makes the part ambiguous or unsafe to generate.

Do not ask for clarification for details that can be reasonably inferred.

Reasonable defaults:

- wall thickness: 2.0 mm
- corner radius: 0 unless the user asks for rounded corners
- clearance for fitted parts: 0.2 mm for FDM unless otherwise specified
- hole clearance: nominal diameter plus 0.2 mm for printed holes, when practical
- export filename: `model.stl`

Ask if:

- critical dimensions are missing
- the part interfaces with an existing object and fit matters
- the user asks for snap fits, threads, bearings, press fits, or load-bearing structures without enough constraints

## 3D-printing design guidance

Prefer designs that are easy to print on FDM:

- avoid unsupported overhangs greater than about 45 degrees
- avoid very thin walls below nozzle-compatible sizes
- use wall thicknesses that are multiples of 0.4 mm when possible
- avoid tiny features below about 0.4 mm
- place the largest flat face on the bed when practical
- avoid sharp internal corners if stress matters
- use fillets where they improve strength or usability, but do not overuse them

For the current printer workflow, small ABS parts are expected. Designs should be robust against ABS shrinkage and minor first-layer variation.

## Printer and workflow context

The project targets an UP Mini style workflow:

```text
CadQuery
→ STL
→ PrusaSlicer CLI
→ G-code
→ up3dtranscode
→ up3dload
```

The physical printer can print approximately 120 x 120 x 120 mm, but normal useful parts should usually stay within a centered 100 x 100 x 100 mm region unless the user explicitly asks otherwise.

When generating model dimensions, avoid using the full physical print area unless requested.

## Slicing and printing are out of scope for model code

Generated CadQuery files should not contain slicer logic, printer G-code, or upload logic.

They should only:

- define geometry
- export STL
- optionally display in CQ-editor

The printing pipeline should handle slicing and upload separately.

## Preferred response behavior for Codex

When asked to create or modify a model:

1. Inspect existing project files if available.
2. Generate or update the CadQuery script.
3. Keep the script parametric.
4. Ensure it runs headlessly.
5. Ensure it exports STL.
6. Avoid introducing GUI-only requirements.
7. If changing dimensions, update filenames when appropriate.
8. Do not silently change printer or slicer settings.

## Validation checklist

Before considering CadQuery code complete, verify:

- the script imports `cadquery as cq`
- all important dimensions are parameters
- the model bottom is on `Z = 0`
- the model is centered on XY unless otherwise specified
- the model exports an STL
- `show_object()` is guarded with `try/except NameError`
- generated geometry matches the requested dimensions
- no unnecessary supports should be needed for simple parts
- the model fits within the intended print volume

## Example: square frame

```python
import cadquery as cq

# Parameters
outer_size = 20.0
height = 1.0
wall_thickness = 2.0

inner_size = outer_size - 2 * wall_thickness
if inner_size <= 0:
    raise ValueError("wall_thickness is too large for outer_size")

# Create a flat-base square frame from Z=0 to Z=height
outer = (
    cq.Workplane("XY")
    .rect(outer_size, outer_size)
    .extrude(height)
)

inner_cut = (
    cq.Workplane("XY")
    .rect(inner_size, inner_size)
    .extrude(height + 0.2)
)

result = outer.cut(inner_cut)

cq.exporters.export(result, "square_20x20x1.stl")

try:
    show_object(result)
except NameError:
    pass
```

## Example: natural-language interpretation

User says:

> make me a small spacer, 30 mm long, with two screw holes

Agent should infer a rectangular spacer and ask only for the screw hole diameter if it is not obvious. If reasonable, use common defaults and make the script parametric:

- length = 30 mm
- width = 10 mm unless specified
- height = 3 mm unless specified
- two holes along the centerline
- hole diameter parameter
- bottom on Z = 0
- export STL

## Do not

- generate non-parametric one-off geometry unless explicitly requested
- require the user to know CadQuery selectors
- put printer-specific G-code into CadQuery scripts
- assume visual inspection is available
- rely on `show_object()` without guarding it
- create parts larger than the intended print volume without warning
