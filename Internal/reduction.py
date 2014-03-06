import math
from gumpy.nexus import array, dataset
from au.gov.ansto.bragg.datastructures.util import AxisRecord
from au.gov.ansto.bragg.kowari.dra.core import GeometryCorrection
SKIP_LEFT = 5
SKIP_RIGHT = 5
SKIP_TOP = 5
SKIP_BOTTOM = 5
LOWER_LIM = 0.1
DEGREE_RAD_COEFFICIENT = 180 / math.pi
DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE = 1078.0

def make_eff_map(df, path):
    global SKIP_LEFT
    global SKIP_RIGHT
    global SKIP_TOP
    global SKIP_BOTTOM
    global LOWER_LIM
    
    map = df[path]
    if map.ndim == 4:
        map = map[0,0]
    elif map.ndim == 3:
        map = map[0]
    
    map = map.float_copy()
    map[0:SKIP_LEFT, :] = 1
    shape = map.shape
    map[shape[0] - SKIP_RIGHT : shape[0], :] = 1
    map[SKIP_LEFT : shape[0] - SKIP_RIGHT, 0 : SKIP_BOTTOM] = 1
    map[SKIP_LEFT : shape[0] - SKIP_RIGHT, shape[1] - SKIP_TOP : shape[1]] = 1

    ctr = map[SKIP_LEFT:shape[0] - SKIP_RIGHT, SKIP_BOTTOM:shape[1] - SKIP_TOP]
    avg = ctr.sum() / ctr.size
    ctr /= avg
    ctr[ctr < LOWER_LIM] = 1
    return map
    
    
def eff_corr(ds, map):
    for fm in ds:
        fm /= map

def geo_corr(ds):
    sdds = DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE ** 2
    try:
        sdds = ds.sample_to_detector_distance ** 2
    except:
        pass
    stth = ds.stth
    if not hasattr(stth, '__len__') :
        stth = [stth]
    is_fixed_stth = True
    if math.fabs(stth[0] - stth[-1]) > 1e-3:
        is_fixed_stth = False
    
    currentStth = stth[0] / DEGREE_RAD_COEFFICIENT
    sinStth = math.sin(currentStth)
    cosStth = math.cos(currentStth)
    
    y_len = ds.axes[-2].size - 1
    x_len = ds.axes[-1].size - 1
    d_shape = [y_len, x_len]
    pixel_2theta = array.instance([y_len, x_len + 1], dtype = float)
    
    if is_fixed_stth :
        res = dataset.instance(ds.shape, dtype = float)
        
        y_bounds = ds.axes[-2].__iArray__
        y_centres = AxisRecord.createCentres(y_bounds)
        x_bounds = ds.axes[-1].__iArray__
        GeometryCorrection.calculateTwoThetaPixel(sdds, x_bounds, cosStth, sinStth, \
                                             y_centres, pixel_2theta.__iArray__)
        axis_2theta = array.instance([x_len + 1], dtype = float)
        GeometryCorrection.calculateTwoThetaAxis(sdds, x_bounds, cosStth, \
                                             sinStth, axis_2theta.__iArray__)
        relocateLeftIndexArray = array.instance(d_shape, dtype = int)
        relocateRightIndexArray = array.instance(d_shape, dtype = int)
        relocateLeftRateArray = array.instance(d_shape, dtype = float)
        relocateRightRateArray = array.instance(d_shape, dtype = float)
        relocateCounterArray = array.instance(d_shape, dtype = float)
        
        for i in xrange(ds.shape[0]):
            GeometryCorrection.rebinWithTwoTheta(ds[i].__iArray__, ds[i].var.__iArray__, \
                        res[i].__iArray__, res[i].var.__iArray__, pixel_2theta.__iArray__, \
                        axis_2theta.__iArray__, relocateLeftIndexArray.__iArray__, \
                        relocateRightIndexArray.__iArray__, relocateLeftRateArray.__iArray__, \
                        relocateRightRateArray.__iArray__, relocateCounterArray.__iArray__, \
                        i == 0)
        r2.axes[2]=axis_2theta
        res.copy_metadata_shallow(ds)
        res.append_log('geometry curve correction')
    else:
        pass
    return res

def v_intg(ds):
    return ds.intg(1)