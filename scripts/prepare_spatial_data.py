"""Prepare Las Perlas bathymetry layers with QGIS/GDAL command-line tools.

Run this script from the QGIS Python environment and provide the original GMRT
GeoTIFF as its only argument:

    python prepare_spatial_data.py C:/path/to/GMRT_topography.tif

The script creates the cleaned bathymetry, land mask, coastline and 10 m depth
contours in the repository's data directory.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


def executable(name: str) -> str:
    """Return an installed GDAL executable or stop with a clear message."""
    found = shutil.which(name)
    if not found:
        raise SystemExit(
            f"{name} was not found. Run the script from the QGIS/OSGeo4W "
            "Python environment so the GDAL tools are on PATH."
        )
    return found


def run(*arguments: str) -> None:
    """Run one external command and fail immediately if it is unsuccessful."""
    print("Running:", " ".join(arguments))
    subprocess.run(arguments, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Original GMRT topography GeoTIFF")
    args = parser.parse_args()

    source = args.source.resolve()
    if not source.exists():
        raise SystemExit(f"Input raster does not exist: {source}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    gdalwarp = executable("gdalwarp")
    gdal_contour = executable("gdal_contour")
    gdal_calc = executable("gdal_calc.py")

    resampled = DATA_DIR / "_bathymetry_resampled_all.tif"
    bathymetry = DATA_DIR / "Las_Perlas_clean_bathymetry.tif"
    land = DATA_DIR / "Las_Perlas_land_mask.tif"
    coastline = DATA_DIR / "Las_Perlas_coastline.gpkg"
    contours = DATA_DIR / "Las_Perlas_bathymetry_contours_10m.gpkg"

    run(
        gdalwarp, "-overwrite", "-r", "cubicspline", "-tr", "0.00025",
        "0.00025", "-tap", "-co", "COMPRESS=DEFLATE", "-co", "TILED=YES",
        "-co", "PREDICTOR=3", str(source), str(resampled),
    )

    run(
        sys.executable, gdal_calc, "-A", str(resampled),
        f"--outfile={bathymetry}", "--calc=where(A<0,A,-9999)",
        "--NoDataValue=-9999", "--type=Float32", "--co=COMPRESS=DEFLATE",
        "--co=TILED=YES", "--overwrite",
    )

    run(
        sys.executable, gdal_calc, "-A", str(source), f"--outfile={land}",
        "--calc=where(A>=0,1,-9999)", "--NoDataValue=-9999", "--type=Byte",
        "--co=COMPRESS=DEFLATE", "--co=TILED=YES", "--overwrite",
    )

    if coastline.exists():
        coastline.unlink()
    run(gdal_contour, "-f", "GPKG", "-fl", "0", "-a", "elev_m",
        str(source), str(coastline))

    if contours.exists():
        contours.unlink()
    run(gdal_contour, "-f", "GPKG", "-a", "depth_m", "-i", "10",
        "-snodata", "-9999", str(bathymetry), str(contours))

    resampled.unlink(missing_ok=True)
    print(f"Spatial layers written to {DATA_DIR}")


if __name__ == "__main__":
    main()
