set shell := ["bash", "-cu"]

MODEL := "model"
PRINTER := "up3d"
HEIGHT := "122.3"

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

# Transcode G-code to umc
transcode:
    ssh {{PRINTER}} "up3dtranscode mini /tmp/{{MODEL}}.gcode /tmp/{{MODEL}}.umc {{HEIGHT}}"

# Trigger remote print
print:
    ssh {{PRINTER}} "up3dload /tmp/{{MODEL}}.umc"

# Full pipeline
all: stl gcode upload transcode print

# Open CQ-editor
edit:
    uv run cq-editor {{MODEL}}.py

# Remove generated artifacts
clean:
    rm -f *.stl *.step *.gcode
