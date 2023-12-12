"""
UDP to load the annual biomass dataset for AGB, BGB, StandingBiomass awa SD from the ESA forest carbon monitoring
dataset

Note: wished by BC3 - the clostest year will be used to the requested time e.g. requested year is 2000 then data
      of year 2020 is given back!

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
    default=2020,
    description="The year for which to load the forest carbon monitoring.",
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

param_band = Parameter.string(
    name="band",
    default="AGB",
    description="Which band of the dataset to load (AGB, AGB-SD, BGB, BGB-SD, GSV, GSV-SD)."
)


# get datacube of the latest observation available
start = text_concat([2000, "01", "01"], separator="-")
end = text_concat([add(param_year, 1), "01", "01"], separator="-")

cube1 = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/ESA_forest_carbon_monitoring_100m/collection.json",
    temporal_extent=[start, end],
    bands=[param_band]
)
# reduce the temporal dimension to last observation
cube1 = cube1.reduce_dimension(dimension='t', reducer=lambda x: x.last(ignore_nodata=False))

# get backwards cube
cube2 = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/ESA_forest_carbon_monitoring_100m/collection.json",
    temporal_extent=['2020-01-01', '2021-01-01'],
    bands=[param_band]
)

# do the selection of the cube we need
# before 2020 that is the year 2020 and after that it is the latest available dataset
cube = if_(gte(param_year, 2020), cube1, cube2)

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="bilinear")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns the specified band of the ESA forest carbon monitoring DEMO dataset.
"""

spec = build_process_dict(
    process_id="udp_biomass_fcm-100m",
    summary="Load the ESA forest carbon monitoring dataset for specified year and band. "
            "Returns a single band RasterCube.",
    description=description.strip(),
    parameters=[
        param_geo,
        param_year,
        param_warp,
        param_epsg,
        param_resolution,
        param_band
    ],
    process_graph=cube,
)

# dump to json file to be usable as UDP
this_script = pathlib.Path(__file__)
json_file = os.path.normpath(os.path.join(this_script.parent, 'json', this_script.name.lower().split('.')[0] + '.json'))
print(f"Writing UDP to {json_file}")
with open(json_file, "w", encoding="UTF8") as f:
    json.dump(spec, f, indent=2)
