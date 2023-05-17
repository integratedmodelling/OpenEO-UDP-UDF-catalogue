import logging
import inspect

import openeo
from openeo.util import TimingLogger


def main():
    logging.basicConfig(level=logging.INFO)

    connection = openeo.connect(
        url="openeo-dev.vito.be",
    )
    connection.authenticate_oidc()

    polygon = {
        "type": "Polygon",
        "coordinates": [
            [
                [5.046, 51.23],
                [5.016, 51.21],
                [5.019, 51.20],
                [5.140, 51.21],
                [5.135, 51.24],
                [5.046, 51.23],
            ]
        ],
    }

    cube = connection.datacube_from_process(
        process_id="dummy_udp",
        namespace="https://raw.githubusercontent.com/integratedmodelling/OpenEO-UDP-UDF-catalogue/main/UDP/json/dummy_udp.json",
        year=2020,
        resolution=300,
        geometry=polygon,
    )

    print("Equivalent curl command:")
    kwargs = {}
    if "obfuscate_auth" in inspect.signature(connection.as_curl).parameters:
        kwargs["obfuscate_auth"] = True
    print(connection.as_curl(cube, **kwargs))

    result = "example-dummy.nc"
    with TimingLogger(title=f"Downloading {result}"):
        cube.download("example-dummy.nc")


if __name__ == "__main__":
    main()
