# Data availability and preparation

## Ownership and access

The BRUV survey records and survey-site coordinates used in this project are owned by **MarAlliance**. They are not included in this repository and may not be redistributed from it. Researchers seeking access should contact MarAlliance directly and comply with its data-sharing, attribution and use conditions.

This directory intentionally contains documentation only. The scripts expect authorized users to supply the required source data locally.

## Survey sites

The mapping workflow expects an authorized local copy of `Las_Perlas_GRTS_sites.csv`. This file is excluded from version control because the survey-site coordinates belong to MarAlliance.

## Bathymetry

The original GMRT v4.5 GeoTIFF and all derived spatial layers are excluded from version control. Authorized users may download a user-defined GeoTIFF from the [GMRT MapTool](https://www.gmrt.org/GMRTMapTool) using approximately:

```text
West:  -79.30
East:  -78.60
South:   8.00
North:   8.75
CRS:   WGS 84 / EPSG:4326
```

Save the downloaded raster outside the repository. The mapping workflow then:

1. retains negative elevation values as bathymetry;
2. assigns land values to NoData in the ocean raster;
3. uses cubic-spline resampling for display;
4. generates a separate land mask from values greater than or equal to zero;
5. extracts a zero-metre coastline; and
6. generates 10 m bathymetric contours.

The expected generated filename is:

```text
Las_Perlas_clean_bathymetry.tif
```

Place it in this `data` directory before running the PyQGIS build script.

## Locally generated layers

The workflow generates the following files locally; they are not included in the public repository:

- `Las_Perlas_bathymetry_contours_10m.gpkg` — 10 m bathymetric contours
- `Las_Perlas_coastline.gpkg` — coastline derived from the zero-metre contour
- `Las_Perlas_land_mask.tif` — pale-grey land mask
- `locator_countries.geojson` — regional locator boundaries

