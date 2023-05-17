""" script with OpenEO support to generate an annual average FCOVER composite out of the CGLS collection

    This script will be later converted into a UDP and saved in a Git repository to be called within OpenEO
    via it's URN (URL) and setting the Parameter explained in the parameter section of this script

    Note: this script (later UDP) will use the geoJSON standard (https://datatracker.ietf.org/doc/html/rfc7946)
          to specify the spatial extent.
          If the requested AOI is a bounding box (polygon) then this can lead to a mismatch in the returned raster
          file extent if the return raster is requested in a projected coordinate system.
          see: https://i.stack.imgur.com/AGwAk.png
          Possible solution: densifying the edges of the bounding box to account for nonlinear transformations along
                             the bounding box edges --> see script "BBOX_densification.py"
    NOTE: if no machine-2-machine authentication is used --> website will be opened to authenticate manually
"""

import openeo
from openeo.api.process import Parameter
from openeo.processes import if_, and_,gte, text_concat
import json
import os
import datetime

###########################
# PARAMETER section
pYear = 2000
#AOI = '{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[14.632191794994476, 47.1707469541707], [14.640151135432319, 47.26025412255243], [14.648145594708197, 47.34975629134882], [14.656175392834125, 47.43925351058935], [14.664240751705927, 47.52874583024814], [14.672341895123246, 47.61823330024366], [14.680479048809815, 47.7077159704386], [14.688652440433986, 47.79719389063955], [14.696862299629533, 47.886667110596754], [14.705108858016706, 47.97613568000396], [14.713392349223566, 48.065599648498065], [14.721713008907606, 48.15505906565887], [14.730071074777628, 48.244513981008865], [14.738466786615929, 48.33396444401288], [14.746900386300753, 48.42341050407786], [14.75537211782907, 48.512852210552516], [14.763882227339602, 48.602289612727056], [14.772430963136202, 48.69172275983287], [14.781018575711501, 48.781151701042226], [14.789645317770896, 48.8705764854679], [14.79831144425683, 48.95999716216288], [14.807017212373413, 49.04941378012001], [14.815762881611349, 49.138826388271646], [14.824548713773211, 49.228235035489256], [14.833374972999046, 49.317639770583135], [14.842241925792322, 49.40704064230191], [14.851149841046208, 49.49643769933227], [14.86009899007024, 49.58583099029844], [14.869089646617299, 49.67522056376195], [14.878122086910999, 49.764606468221], [14.887196589673403, 49.85398875211022], [14.89631343615314, 49.94336746380013], [14.905472910153897, 50.03274265159675], [14.914675298063274, 50.122114363741076], [14.923920888882089, 50.21148264840868], [14.933209974254012, 50.30084755370919], [14.94254284849565, 50.390209127685814], [14.951919808627025, 50.479567418314865], [14.96134115440249, 50.56892247350522], [14.970807188342043, 50.65827434109777], [14.980318215763084, 50.74762306886496], [14.989874544812618, 50.8369687045102], [14.999476486499903, 50.926311295667276], [15.009124354729533, 51.01565088989991], [15.018818466335004, 51.10498753470099], [15.02855914111274, 51.194321277492115], [15.038346701856572, 51.283652165622954], [15.048181474392752, 51.37298024637064], [15.058063787615398, 51.462305566939065], [15.067993973522478, 51.55162817445838], [15.077972367252304, 51.64094811598416], [15.087999307120487, 51.73026543849688], [15.098075134657503, 51.81958018890115], [15.108200194646708, 51.90889241402503], [15.118374835162955, 51.998202160619364], [15.128599407611722, 52.08750947535701], [15.138874266768823, 52.17681440483201], [15.14919977082068, 52.266116995559024], [15.159576281405178, 52.35541729397245], [15.170004163653084, 52.44471534642559], [15.18048378623012, 52.534011199189926], [15.191015521379565, 52.62330489845427], [15.20159974496556, 52.712596490323946], [15.212236836516963, 52.80188602081989], [15.22292717927192, 52.89117353587783], [15.233671160223015, 52.98045908134737], [15.244469170163125, 53.06974270299116], [15.255321603731947, 53.1590244464838], [15.266228859463181, 53.24830435741109], [15.277191339832447, 53.337582481269], [15.288209451305868, 53.42685886346267], [15.299283604389412, 53.51613354930542], [15.310414213678959, 53.605406584017786], [15.321601697911069, 53.6946780127264], [15.332846480014586, 53.78394788046306], [15.344148987162937, 53.87321623216349], [15.355509650827281, 53.96248311266645], [15.366928906830397, 54.0517485667124], [15.378407195401444, 54.14101263894253], [15.389944961231484, 54.23027537389752], [15.401542653529912, 54.319536816016466], [15.413200726081694, 54.408797009635435], [15.424919637305507, 54.498055998986544], [15.43669985031274, 54.58731382819653], [15.448541832967411, 54.676570541285464], [15.460446057947019, 54.76582618216558], [15.472413002804302, 54.855080794639775], [15.484443150029966, 54.94433442240049], [15.32946432114462, 54.951035235584904], [15.174438667699565, 54.95754435741059], [15.01936752273769, 54.963861695749095], [14.864252222247538, 54.969987161117416], [14.70909410507974, 54.9759206666854], [14.553894512862955, 54.98166212828293], [14.398654789919497, 54.98721146440689], [14.24337628318035, 54.99256859622801], [14.088060342099944, 54.99773344759726], [13.932708318570457, 55.00270594505233], [13.777321566835756, 55.00748601782365], [13.621901443404939, 55.01207359784036], [13.466449306965567, 55.01646861973588], [13.310966518296501, 55.02067102085352], [13.155454440180465, 55.024680741251515], [12.999914437316225, 55.028497723708234], [12.844347876230513, 55.032121913726805], [12.688756125189704, 55.03555325953982], [12.533140554111062, 55.03879171211349], [12.3775025344739, 55.04183722515197], [12.221843439230394, 55.04468975510105], [12.066164642716187, 55.04734926115195], [11.910467520560768, 55.04981570524462], [11.75475344959766, 55.052089052071075], [11.599023807774389, 55.054169269078216], [11.443279974062303, 55.05605632647069], [11.287523328366207, 55.05775019721333], [11.1317552514339, 55.05925085703343], [10.975977124765457, 55.06055828442282], [10.820190330522536, 55.06167246063968], [10.66439625143748, 55.0
EPSG_output = 3035
resolution = 100
output_root = r'/data/people_vol1/tests'
''' Note: 
    pYear: integer
    AOI: str representation of GeoJSON in EPSG:4326
    EPSG: integer; projection of the requested raster result EPSG format
    resolution: integer, float; resolution of the requested raster result
    output_root: absolute file path to folder to save resulting GeoTiff
    '''
##################################

########## WORK section
# Establish connection to OpenEO instance (note that authentication is not necessary to just build the UDP)
connection = openeo.connect(
    # url="openeo.vito.be"
    url="openeo-dev.vito.be"
)
# connection.authenticate_oidc()

param_geo = Parameter(
        name="geometry",
        description="Geometry as GeoJSON feature(s).",
        schema={
            "type": "object",
            "subtype": "geojson"
        }
    )

param_year = Parameter.integer(
    name="year", default=2021,
    description="The year for which to generate an annual mean composite")

param_resolution = Parameter.number(
    name="resolution", default=100,
    description="The desired resolution, specified in units of the projection system, which is meters by default.")

# depending on the year choose the correct FCOVER catalog ID
# CGLS_FCOVER300_V1_GLOBAL (300m dataset) or CGLS_FCOVER_V2_GLOBAL (1km dataset)
# Note: maybe switch to an approach where the catalog ID is given as parameter and ARIES decides on year by itself
#THIS WILL BE REPLACED BY IF PROCESS BELOW
if (pYear >= 1999) and (pYear < 2015):
    collection_id = 'CGLS_FCOVER_V2_GLOBAL'
elif (pYear >= 2015) and (pYear < datetime.date.today().year):
    collection_id = 'CGLS_FCOVER300_V1_GLOBAL'
elif pYear >= datetime.date.today().year:
    raise ValueError('The annual average FCOVER can not request for future years or '
                     'up to the moment the current year is finished')
else:
    raise ValueError('For the requested processing year no OpenEO collection ID is specified.')
print(f'* the collection ID {collection_id} is used for the annual FCOVER generation.')

# get the name of the band we want to process
info = connection.describe_collection(collection_id)['cube:dimensions']['bands']['values'][0]

# load a dataset --> filter only temporal

# TODO text_concat not supported?
start = text_concat([param_year,1,1],"-")
end = text_concat([param_year,12,31],"-")
start="2020-01-01"
end="2020-12-31"

datacube1 = connection.load_collection(
    'CGLS_FCOVER300_V1_GLOBAL',
    temporal_extent=[start, end],
    bands=[info])

datacube2 = connection.load_collection(
    'CGLS_FCOVER_V2_GLOBAL',
    temporal_extent=[start, end],
    bands=[info])

datacube = if_(gte(param_year,2015),datacube1,datacube2)
# masking to valid data and rescaling
data_rescaled = datacube.apply(lambda x: if_(and_(x >= 0, x <= 250), x/250.))

# reduce the temporal dimension with mean reducer
data_temp_aggregated = data_rescaled.reduce_dimension(dimension='t', reducer='mean')

# resample output to correct EPSG
resampled = data_temp_aggregated.resample_spatial(
    resolution=param_resolution,
    projection=EPSG_output,
    method='bilinear')

# filter spatial by BBOX given in the specified EPSG
resampled_AOI = resampled.filter_spatial(geometries=param_geo)

# run (fast method when we only request ONE final file and do not need metadata)
#resampled_AOI.download(os.path.join(output_root, f'FCOVER_annual-average_{pYear}_{resolution}m_EPSG{EPSG_output}.tif'))

description= """
Given a year and area of interest, returns a mean composite of [FCover](https://land.copernicus.eu/global/products/fcover).
"""

spec = {
        "id": "CGLS_FCOVER_ANNUAL_MEAN",
        "summary": "Annual mean composite of Copernicus Global Land FCover",
        "description": description,
        "parameters": [
            param_geo.to_dict(),
            param_year.to_dict(),
            param_resolution.to_dict()
        ],
        "process_graph": resampled_AOI.flat_graph()
    }

print(json.dumps(spec,indent=2))
