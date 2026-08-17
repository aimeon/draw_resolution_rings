import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# ===== USER INPUT =====
input_path = r"C:\path\to\your\scaled\image.tiff"
output_path = r"C:\output\path\example_with_rings.png"

pixel_size_um = 55.0          # um, physical detector pixel size in micrometers
camera_length_mm = 757.0        # mm
wavelength_A = 0.019687       # Å
beam_center = (257.0, 257.0)        # px

# Resolution rings you want (in Å)
rings_d_A = [3, 2, 1.1]


# scale bar length (in Å^-1)
scale_bar_d_A = 2.0     # Å^-1

# ======================


def d_to_radius_pixels(d_A, L_mm, lam_A, pixel_size_um):
    """
    Convert d-spacing (Å) to radius in pixels using:
        R(mm) = L * λ / d    (small-angle approx)
    """
    pixel_size_mm = pixel_size_um / 1000.0
    R_mm = L_mm * lam_A / d_A
    R_px = R_mm / pixel_size_mm
    return R_px


def draw_res_rings():
    if beam_center is None:
        cx = nx / 2.0
        cy = ny / 2.0
    else:
        cx, cy = beam_center
    # --- Draw resolution rings ---
    for d in rings_d_A:
        R_px = d_to_radius_pixels(d, camera_length_mm, wavelength_A, pixel_size_um)
        circ = Circle((cx, cy), R_px, edgecolor="white", facecolor="none", linewidth=0.8)
        ax.add_patch(circ)

        # Label each ring roughly on the diagonal
        label_x = cx + R_px / np.sqrt(2)
        label_y = cy - R_px / np.sqrt(2)
        ax.text(label_x, label_y, f"{d:.2f} Å", color="white", fontsize=15,
                ha="left", va="bottom")


def draw_scale_bar():
    bar_len_px = d_to_radius_pixels(scale_bar_d_A, camera_length_mm, wavelength_A, pixel_size_um)

    margin_px = 0.05 * ny
    x0 = 0.05 * nx
    y0 = ny - margin_px

    ax.plot([x0, x0 + bar_len_px], [y0, y0], color="white", linewidth=2)

    label_text = f" {1/scale_bar_d_A:.2f} Å⁻¹"
    ax.text(x0 + bar_len_px / 2, y0 - 15, label_text,
            color="white", fontsize=8, ha="center", va="top")


def main():
    img = plt.imread(input_path)
    if img.ndim == 3:
        img = img.mean(axis=2)

    ny, nx = img.shape
    fig, ax = plt.subplots(figsize=(6, 6))

    ax.imshow(img, cmap="gray", origin="upper")

    draw_res_rings()
    # draw_scale_bar()

    ax.set_axis_off()
    ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0)
    plt.show()

    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
    
