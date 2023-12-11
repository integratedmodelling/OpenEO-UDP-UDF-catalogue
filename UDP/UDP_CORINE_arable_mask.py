"""
UDP to generate an arable/non-arable mask by remapping the CORINE Accounting layers

"""
import json
import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, process, add
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

param_remap_dict = Parameter(
    name="remapping_dict",
    default={141: 0, 211: 1, 212: 1, 213: 1, 221: 0, 222: 0, 223: 0, 231: 0, 241: 0, 242: 0, 243: 0, 244: 0, 311: 0,
             312: 0, 313: 0, 321: 0, 322: 0, 323: 0, 324: 0, 333: 0, 334: 0},
    description="dict with the remapping values.",
    schema={"type": "object"},
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

start = process("text_concat", data=[2000, "01", "01"], separator="-")
end = process("text_concat", data=[add(param_year, 1), "01", "01"], separator="-")

cube = connection.load_collection(
    "CORINE_LAND_COVER_ACCOUNTING_LAYERS", temporal_extent=[start, end], bands=["CLC_ACC"]
)

# reduce the temporal dimension to last observation
cube = cube.reduce_dimension(dimension='t', reducer=lambda x: x.last(ignore_nodata=False))

# reclassify using the dic
# load the UDF from URL (NOTE: you have to use the raw file download)
url_raw = 'https://raw.githubusercontent.com/integratedmodelling/OpenEO-UDP-UDF-catalogue/main/UDF/UDF_remapping.py'
udf = openeo.UDF.from_url(url_raw, context={"class_mapping": {"from_parameter": param_remap_dict.name}})
cube = cube.apply(process=udf)

# warp to specified projection and resolution if needed
cube_resample = cube.resample_spatial(resolution=param_resolution, projection=param_epsg, method="near")
cube = if_(param_warp, cube_resample, cube)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Creates a arable/non-arable mask for the CORINE Accounting Layers based on a given remapping dictionary.
"""

spec = build_process_dict(
    process_id="udp_CORINE_arable_mask",
    summary="arable/non-arable mask based on CORINE ACC remapped with custom dictionary. "
            "Returns a single band RasterCube.",
    description=description.strip(),
    parameters=[
        param_geo,
        param_year,
        param_remap_dict,
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
