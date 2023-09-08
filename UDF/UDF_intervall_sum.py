from openeo.udf import XarrayDataCube

def apply_datacube(cube: XarrayDataCube, context: dict) -> XarrayDataCube:
    """calculation of the sum for a timestep representing an interval (here 10 daily)

    :param cube: data cube
    :param context: dictionary to provide external data - key class_mapping is used to provide external re-mapping dict
    :return: original DataCube with inline adjusted values
    """
    # get the array with the time dimension
    array = cube.get_array()

    # extract number of days for a timestamp intervall
    xdays = [10 if d <= 20 else m - 20 for (d, m) in zip(array.t.dt.day.values, array.t.dt.days_in_month.values)]

    # multiply the array values of each timestamp with the amount of days
    for i in range(array.values.shape[0]):
        array.values[i, :, :] = array.values[i, :, :] * xdays[i]

    return cube
