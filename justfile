set shell := ["bash", "-cu"]

MODEL := "model"
PRINTER := "up3d"

default:
    @just --list

# Generate STL via CadQuery
stl:
    uv run python {{MODEL}}.py

# Slice STL into G-code
gcode:
    prusa-slicer --load profiles/{{PRINTER}}.ini --export-gcode {{MODEL}}.stl --output {{MODEL}}.gcode

# Upload G-code to printer host
upload:
    scp {{MODEL}}.gcode {{PRINTER}}:/tmp/

# Trigger remote print
print:
    ssh {{PRINTER}} "./print.sh"

# Full pipeline
all: stl gcode upload print

# Open CQ-editor
edit:
    uv run cq-editor {{MODEL}}.py

# Remove generated artifacts
clean:
    rm -f *.stl *.step *.gcode
