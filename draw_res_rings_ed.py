"""Draw resolution rings (and an optional scale bar) on an electron diffraction pattern.

Settings live in config.py next to this script. Usage:

    python draw_res_rings_ed.py
    python draw_res_rings_ed.py input.tiff output.png --no-show
    python draw_res_rings_ed.py --config other_config.py
"""

import argparse
import runpy
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

DEFAULT_CONFIG = Path(__file__).with_name("config.py")


def _read_settings(path):
    """Run a settings file and return its UPPER_CASE names as a dict."""
    values = runpy.run_path(str(path))
    return {k: v for k, v in values.items() if k.isupper()}


def load_config(path=None):
    """Load config.py as defaults, then apply the settings in `path` on top.

    An extra settings file only needs the values that differ from config.py.
    Names that config.py does not define are reported and ignored, so typos
    don't silently fall back to the default.
    """
    settings = _read_settings(DEFAULT_CONFIG)
    if path is not None and Path(path).resolve() != DEFAULT_CONFIG.resolve():
        overrides = _read_settings(path)
        unknown = sorted(set(overrides) - set(settings))
        for name in unknown:
            print(f"Warning: {path} sets unknown setting {name!r}; ignored. "
                  f"Known settings: {', '.join(sorted(settings))}")
            del overrides[name]
        settings.update(overrides)
    return SimpleNamespace(**settings)


def d_to_radius_px(d_A, camera_length_mm, wavelength_A, pixel_size_um):
    """Convert a d-spacing (Å) to a ring radius on the detector (px).

    Uses the exact geometry: sin θ = λ / 2d (Bragg) and R = L · tan 2θ.
    For electrons this differs from the small-angle R = L·λ/d by well under 0.1 %,
    but there is no reason not to be exact.
    """
    theta = np.arcsin(wavelength_A / (2.0 * d_A))
    radius_mm = camera_length_mm * np.tan(2.0 * theta)
    return radius_mm / (pixel_size_um / 1000.0)


def load_grayscale(path):
    """Read an image and return it as a 2-D float array."""
    img = np.asarray(plt.imread(path), dtype=float)
    if img.ndim == 3:
        img = img[..., :3].mean(axis=2)  # drop alpha channel before averaging
    return img


def draw_res_rings(ax, img_shape, center, cfg, geometry):
    """Draw one circle per d-spacing, labelled on the upper-right diagonal."""
    ny, nx = img_shape
    cx, cy = center
    for d in sorted(cfg.RINGS_D_A, reverse=True):
        r = d_to_radius_px(d, **geometry)
        ax.add_patch(Circle((cx, cy), r, edgecolor=cfg.COLOR, facecolor="none",
                            linewidth=cfg.RING_LINEWIDTH))

        label_x = cx + r / np.sqrt(2)
        label_y = cy - r / np.sqrt(2)
        if 0 <= label_x < nx and 0 <= label_y < ny:
            ax.text(label_x, label_y, f"{d:g} Å", color=cfg.COLOR,
                    fontsize=cfg.LABEL_FONTSIZE, ha="left", va="bottom")
        else:
            print(f"Warning: label for {d:g} Å ring falls outside the image; skipped.")


def draw_scale_bar(ax, img_shape, cfg, geometry):
    """Draw a reciprocal-space scale bar in the lower-left corner."""
    ny, nx = img_shape
    length_inv_A = cfg.SCALE_BAR_INV_A
    bar_len_px = d_to_radius_px(1.0 / length_inv_A, **geometry)

    x0 = 0.05 * nx
    y0 = 0.95 * ny
    ax.plot([x0, x0 + bar_len_px], [y0, y0], color=cfg.COLOR, linewidth=2,
            solid_capstyle="butt")
    # y grows downward in image coordinates, so "above the bar" is y0 - offset
    ax.text(x0 + bar_len_px / 2, y0 - 0.01 * ny, f"{length_inv_A:g} Å⁻¹",
            color=cfg.COLOR, fontsize=cfg.LABEL_FONTSIZE, ha="center", va="bottom")


def make_figure(cfg, input_path, output_path, show=True):
    img = load_grayscale(input_path)
    ny, nx = img.shape
    center = cfg.BEAM_CENTER if cfg.BEAM_CENTER is not None else (nx / 2.0, ny / 2.0)
    geometry = dict(camera_length_mm=cfg.CAMERA_LENGTH_MM,
                    wavelength_A=cfg.WAVELENGTH_A,
                    pixel_size_um=cfg.PIXEL_SIZE_UM)

    vmin = vmax = None
    if cfg.CONTRAST_PERCENTILES is not None:
        vmin, vmax = np.percentile(img, cfg.CONTRAST_PERCENTILES)

    # Figure aspect follows the image, so non-square images get no padding
    fig, ax = plt.subplots(figsize=(6, 6 * ny / nx))
    ax.imshow(img, cmap="gray", origin="upper", vmin=vmin, vmax=vmax)

    draw_res_rings(ax, img.shape, center, cfg, geometry)
    if cfg.SCALE_BAR_INV_A is not None:
        draw_scale_bar(ax, img.shape, cfg, geometry)

    ax.set_xlim(0, nx)
    ax.set_ylim(ny, 0)   # keep rings that extend past the edge from enlarging the canvas
    ax.set_axis_off()
    fig.subplots_adjust(0, 0, 1, 1)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=cfg.DPI, bbox_inches="tight", pad_inches=0)
    print(f"Saved: {output_path}")

    if show:
        plt.show()
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", nargs="?", help="input image (default: INPUT_PATH from config)")
    parser.add_argument("output", nargs="?", help="output image (default: OUTPUT_PATH from config)")
    parser.add_argument("--config",
                        help="settings file whose values override config.py; "
                             "it only needs the values that differ")
    parser.add_argument("--no-show", action="store_true",
                        help="save without opening a window")
    args = parser.parse_args()

    cfg = load_config(args.config)
    make_figure(cfg,
                args.input or cfg.INPUT_PATH,
                args.output or cfg.OUTPUT_PATH,
                show=not args.no_show)


if __name__ == "__main__":
    main()
