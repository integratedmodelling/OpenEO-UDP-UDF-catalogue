from openeo.udf import XarrayDataCube, inspect

def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """ remap cube values by given dictionary

    Note: currently implace the values

    :param cube: data cube
    :param context: dictionary to provide external data - key class_mapping is used to provide external re-mapping dict
    :return: remapped data cube
    """
    class_mapping = context["class_mapping"]
    array = cube.get_array()
    for k, v in class_mapping.items():
        # Note: JSON-encoding of the class mapping converted the keys from int to strings, so we have to undo that
        k = int(k)
        array.values[array.values == k] = v
    return cube
