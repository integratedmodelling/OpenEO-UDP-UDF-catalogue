"""
UDP to load the prepared INCA c-factor raster files for usage in RUSLE function (soil retention)

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, text_concat, add
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

start = text_concat([2000, "01", "01"], separator="-")
end = text_concat([add(param_year, 1), "01", "01"], separator="-")

cube = connection.load_disk_collection(format="GTiff",
                                       glob_pattern="/data/users/Public/buchhornm/PEOPLE_INCA_cfactor/PEOPLE_INCA_c-factor_*_v1-1_100m_EPSG3035.tif",
                                       options=dict(date_regex='.*_(\d{4})(\d{2})(\d{2})_v1-1_100m_EPSG3035.tif'))

# filter temporal and spatial
cube = cube.filter_spatial(geometries=param_geo)
cube = cube.filter_temporal([start, end])

# reduce the temporal dimension to last observation - closest to requested year
cube = cube.reduce_dimension(dimension='t', reducer=lambda x: x.last(ignore_nodata=False))

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="near")
cube = if_(param_warp, cube_resample, cube)

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
