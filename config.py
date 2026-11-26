"""Default settings for draw_res_rings_ed.py.

For another dataset or microscope, make a small file with only the values that
differ (e.g. CAMERA_LENGTH_MM = 1000.0) and pick it with
    python draw_res_rings_ed.py --config my_other_settings.py
"""

# ===== Paths =====
INPUT_PATH = r"C:\path\to\your\scaled\image.tiff"
OUTPUT_PATH = r"C:\output\path\example_with_rings.png"

# ===== Geometry =====
PIXEL_SIZE_UM = 55.0          # physical detector pixel size, µm
CAMERA_LENGTH_MM = 757.0      # mm
WAVELENGTH_A = 0.019687       # Å (0.019687 Å = 300 kV)
BEAM_CENTER = (257.0, 257.0)  # (x, y) in px; None = image centre

# ===== What to draw =====
RINGS_D_A = [3, 2, 1.1]       # resolution rings, d-spacing in Å
SCALE_BAR_INV_A = None        # scale bar length in Å⁻¹ (e.g. 0.5); None = no bar

# ===== Appearance =====
COLOR = "white"
RING_LINEWIDTH = 0.8
LABEL_FONTSIZE = 15
CONTRAST_PERCENTILES = None   # e.g. (1, 99.5) to clip hot pixels; None = full range
DPI = 300
