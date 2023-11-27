"""
UDP to load the annual biomass dataset for AGB, BGB, StandingBiomass awa SD from the ESA forest carbon monitoring
dataset --> the original 20m dataset

Export algorithm to UDP json, e.g.

    python UDP/UDP_biomass_fcm-20m.py > UDP/json/udp_biomass_fcm-20m.json

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, and_, gte, process, add, eq
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
    description="The year for which to load the forest carbon monitoring. only 2020 or 2021.",
)

param_warp = Parameter.boolean(
    name="output_warp",
    default=False,
    description="Boolean switch if output should be warped to given projection and resolution, default=False.",
)

param_epsg = Parameter.integer(
    name="output_epsg",
    default=4326,
    description="The desired output projection system, which is EPSG:4326 by default.",
)

param_resolution = Parameter.number(
    name="resolution",
    default=0.00045,
    description="The desired resolution, specified in units of the projection system, which is degree by default.",
)

param_band = Parameter.string(
    name="band",
    default="AGB",
    description="Which band of the dataset to load (AGB, AGB-SD, BGB, BGB-SD, GSV, GSV-SD)."
)

start = process("text_merge", data=[param_year, "01", "01"], separator="-")
end = process("text_merge", data=[add(param_year, 1), "01", "01"], separator="-")

# get datacube of the single collections (1km up to 2019, 300m 2021 onwards)
cube = connection.load_stac(
    "/data/MTDA/PEOPLE_EA/STAC_catalogs/ESA_forest_carbon_monitoring_20m/collection.json",
    temporal_extent=[start, end],
    bands=[param_band]
)

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="bilinear")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns the specified band of the ESA forest carbon monitoring 20m DEMO dataset.
"""

spec = build_process_dict(
    process_id="udp_biomass_fcm-20m",
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

print(json.dumps(spec, indent=2))
