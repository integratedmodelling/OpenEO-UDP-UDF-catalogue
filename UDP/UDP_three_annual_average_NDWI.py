"""
UDP to load the three annual average NDWI generated from Landsat7 and Landsat8 on GEE

Export algorithm to UDP json, e.g.

    python UDP/UDP_three_annual_average_NDWI.py > UDP/json/udp_three_annual_average_NDWI.json

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, process, add
from openeo.rest.udp import build_process_dict

# Establish connection to OpenEO instance (note that authentication is not necessary to just build the UDP)
connection = openeo.connect(url="openeo.vito.be")

# set up the UDP parameters
param_geo = Parameter(
    name="geometry",
    description="Geometry as GeoJSON feature(s).",
    schema={"type": "object", "subtype": "geojson"},
)

param_year = Parameter.integer(
    name="year",
    default=2020,
    description="The year for which to load the NDWI dataset. temp: 2000 up to 2021.",
)

param_warp = Parameter.boolean(
    name="output_warp",
    default=False,
    description="Boolean switch if output should be warped to given projection and resolution, default=False.",
)

param_epsg = Parameter.integer(
    name="output_epsg",
    default=3035,
    description="The desired output projection system, which is EPSG:3035 by default.",
)

param_resolution = Parameter.number(
    name="resolution",
    default=100,
    description="The desired resolution, specified in units of the projection system, which is meters by default.",
)

start = process("text_merge", data=[param_year, "01", "01"], separator="-")
end = process("text_merge", data=[add(param_year, 1), "01", "01"], separator="-")

# get datacube of the single collections via the STAC
cube = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/Landsat_three-annual_NDWI_v1/collection.json",
    temporal_extent=[start, end],
    bands=['NDWI']
)

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="bilinear")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns the three-annual average of the Landsat NDWI generated on the GEE.
"""

spec = build_process_dict(
    process_id="udp_three_annual_average_ndwi",
    summary="Load the Landsat three-annual average NDWI dataset for specified year. "
            "Returns a single band RasterCube.",
    description=description.strip(),
    parameters=[
        param_geo,
        param_year,
        param_warp,
        param_epsg,
        param_resolution
    ],
    process_graph=cube,
)

print(json.dumps(spec, indent=2))
