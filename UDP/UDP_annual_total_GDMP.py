"""
UDP to generate an annual total GDMP product from the Copernicus GDMP datasets (1km & 300m)

Export algorithm to UDP json, e.g.

    python UDP/UDP_annual_total_GDMP.py > UDP/json/udp_annual_total_gdmp.json

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, and_, gte, process, add
from openeo.rest.udp import build_process_dict

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
    description="The year for which to generate an annual total composite.",
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

datacube1 = connection.load_collection(
    "CGLS_GDMP300_V1_GLOBAL", temporal_extent=[start, end], bands=["GDMP"]
)

datacube2 = connection.load_collection(
    "CGLS_GDMP_V2_GLOBAL", temporal_extent=[start, end], bands=["GDMP"]
)

cube = if_(gte(param_year, 2015), datacube1, datacube2)

# masking to valid data and rescaling
cube = cube.apply(lambda x: if_(and_(x >= 0, x <= 32767), x * 0.02))

# since GDMP comes in kg/ha/day we have to multiply the timestep values with the amount of days in the 10-interval
# load the UDF from URL (NOTE: you have to use the raw file download)
url_raw = 'https://raw.githubusercontent.com/integratedmodelling/OpenEO-UDP-UDF-catalogue/main/UDF/UDF_intervall_sum.py'
udf = openeo.UDF.from_url(url_raw)
cube = cube.apply_dimension(process=udf, dimension='t')

# reduce the temporal dimension with sum reducer
cube = cube.reduce_dimension(dimension="t", reducer=lambda data: data.sum())

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="bilinear")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by geometry given as GeoJSON
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns a sum composite of [GDMP](https://land.copernicus.eu/global/products/dmp).
"""

spec = build_process_dict(
    process_id="udp_annual_total_gdmp",
    summary="Annual total composite of Copernicus Global Land GDMP. Returns a single band RasterCube.",
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

print(json.dumps(spec, indent=2))
