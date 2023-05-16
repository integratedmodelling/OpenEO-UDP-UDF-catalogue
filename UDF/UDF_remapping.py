import numpy
from openeo.udf import XarrayDataCube
from openeo.processes import nan
import xarray


def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """ remap cube values by given dictionary

    :param cube: data cube
    :param context: dictionary to provide external data - key class_mapping is used to provide external re-mapping dict
    :return: data cube with remapped values (new cube)
    """
    class_mapping = context["class_mapping"]

    array: xarray.DataArray = cube.get_array()
    result = numpy.full_like(array.values, nan())

    for k, v in class_mapping.items():
        # Note: JSON-encoding of the class mapping converted the keys from int to strings, so we have to undo that
        k = int(k)
        result[array.values == k] = v

    return XarrayDataCube(array=xarray.DataArray(result, dims=array.dims, coords=array.coords))
