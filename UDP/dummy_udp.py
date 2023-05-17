"""
Export algorithm to UDP json, e.g.

    python UDP/dummy_udp.py > UDP/json/dummy_udp.json

"""

import json

import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, and_, gte, text_concat, process
from openeo.rest.udp import build_process_dict


# Establish connection to OpenEO instance (note that authentication is not necessary to just build the UDP)
connection = openeo.connect(
    # url="openeo.vito.be"
    url="openeo-dev.vito.be"
)
# connection.authenticate_oidc()

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

param_resolution = Parameter.number(
    name="resolution",
    default=100,
    description="The desired resolution, specified in units of the projection system, which is meters by default.",
)

# TODO: legacy `text_merge` vs new `text_concat`, see https://github.com/Open-EO/openeo-python-driver/issues/196
# start = text_concat([param_year, 1, 1], "-")
# end = text_concat([param_year, 12, 31], "-")
start = process("text_merge", data=[param_year, 1, 1], separator="-")
end = process("text_merge", data=[param_year, 12, 31], separator="-")


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

# resample output to correct EPSG
cube = cube.resample_spatial(
    resolution=param_resolution, projection=3035, method="bilinear"
)

# filter spatial by BBOX given in the specified EPSG
cube = cube.filter_spatial(geometries=param_geo)

description = """
Given a year and area of interest, returns a mean composite of [FCover](https://land.copernicus.eu/global/products/fcover).
"""

spec = build_process_dict(
    process_id="dummy_udp",
    summary="Annual mean composite of Copernicus Global Land FCover",
    description=description.strip(),
    parameters=[
        param_geo,
        param_year,
        param_resolution,
    ],
    process_graph=cube,
)

print(json.dumps(spec, indent=2))
