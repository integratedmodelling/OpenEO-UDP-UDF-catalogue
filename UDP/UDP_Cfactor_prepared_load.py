"""
UDP to load the prepared INCA c-factor raster files for usage in RUSLE function (soil retention)

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, text_concat, add, gte
from openeo.rest.udp import build_process_dict
import os
import pathlib

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
    default=2021,
    description="The year for which to extract the c-factor. closest dataset is used.",
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

start = text_concat([param_year, "01", "01"], separator="-")
end = text_concat([add(param_year, 1), "01", "01"], separator="-")

cube1 = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/PEOPLE_INCA_cfactor/collection.json",
    temporal_extent=[start, end],
    bands=['cfactor']
)

# get cube after 2021
cube2 = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/PEOPLE_INCA_cfactor/collection.json",
    temporal_extent=['2021-01-01', '2022-01-01'],
    bands=['cfactor']
)

# make selection to fake data after 2021
cube = if_(gte(param_year, 2022), cube2, cube1)

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="near")
cube = if_(param_warp, cube_resample, cube)

# filter temporal and spatial
cube = cube.filter_spatial(geometries=param_geo)

description = """
Loads the prepared c-factor raster dataset from the INCA tool for the soil retention claculation.
"""

spec = build_process_dict(
    process_id="udp_Cfactor_prepared_load",
    summary="Loads the prepared annual INCA c-factor raster for RUSLE calculation. "
            "Returns a single band RasterCube.",
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
