"""
UDP to generate an annual average FCOVER product from the Copernicus FCOVER datasets

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, and_, gte, process, add
from openeo.rest.udp import build_process_dict
import os
import pathlib

# Establish connection to OpenEO instance (note that authentication is not necessary to just build the UDP)
connection = openeo.connect(url="openeo-dev.vito.be")

# set up the UDP parameters
param_geo = Parameter(
    name="geometry",
    description="Geometry as GeoJSON feature(s).",
    schema={"type": "object", "subtype": "geojson"},
)

param_year = Parameter.integer(
    name="year",
    default=2021,
    description="The year for which to generate an annual mean composite",
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

start = process("text_concat", data=[param_year, "01", "01"], separator="-")
end = process("text_concat", data=[add(param_year, 1), "01", "01"], separator="-")

datacube1 = connection.load_collection(
    "CGLS_FCOVER300_V1_GLOBAL", temporal_extent=[start, end], bands=["FCOVER"]
)

datacube2 = connection.load_collection(
    "CGLS_FCOVER_V2_GLOBAL", temporal_extent=[start, end], bands=["FCOVER"]
)

cube = if_(gte(param_year, 2015), datacube1, datacube2)

# masking to valid data and rescaling
cube = cube.apply(lambda x: if_(and_(x >= 0, x <= 250), x / 250.0))

# reduce the temporal dimension with mean reducer
cube = cube.reduce_dimension(dimension="t", reducer=lambda data: data.mean())

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="bilinear")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns a mean composite of [FCover](https://land.copernicus.eu/global/products/fcover).
"""

spec = build_process_dict(
    process_id="udp_annual_avg_fcover",
    summary="Annual mean composite of Copernicus Global Land FCOVER. Returns a single band RasterCube.",
    description=description.strip(),
    parameters=[
        param_geo,
        param_year,
        param_warp,
        param_epsg,
        param_resolution,
    ],
    process_graph=cube,
)

# dump to json file to be usable as UDP
this_script = pathlib.Path(__file__)
json_file = os.path.normpath(os.path.join(this_script.parent, 'json', this_script.name.lower().split('.')[0] + '.json'))
print(f"Writing UDP to {json_file}")
with open(json_file, "w", encoding="UTF8") as f:
    json.dump(spec, f, indent=2)
