import math
from gumpy.nexus import array, dataset
from au.gov.ansto.bragg.datastructures.util import AxisRecord
from au.gov.ansto.bragg.kowari.dra.core import GeometryCorrection
SKIP_LEFT = 5
SKIP_RIGHT = 5
SKIP_TOP = 5
SKIP_BOTTOM = 5
LOWER_LIM = 0.001
DEGREE_RAD_COEFFICIENT = 180 / math.pi
DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE = 1078.0

def make_eff_map(df, path):
    global SKIP_LEFT
    global SKIP_RIGHT
    global SKIP_TOP
    global SKIP_BOTTOM
    global LOWER_LIM
    
    map = df[path]
    title = map.title
    if map.ndim == 4:
        map = map[0,0]
    elif map.ndim == 3:
        map = map[0]
    
    map = map.float_copy()
    map.title = title
    shape = map.shape
    
#    ctr = map[SKIP_LEFT:shape[0] - SKIP_RIGHT, SKIP_BOTTOM:shape[1] - SKIP_TOP]
    ctr = map
    avg = ctr.sum() / ctr.size
    print avg
    ctr *= 1.0 / avg

    map[0:SKIP_LEFT, :] = 1
    map[shape[0] - SKIP_RIGHT : shape[0], :] = 1
    map[SKIP_LEFT : shape[0] - SKIP_RIGHT, 0 : SKIP_BOTTOM] = 1
    map[SKIP_LEFT : shape[0] - SKIP_RIGHT, shape[1] - SKIP_TOP : shape[1]] = 1

#    ctr[ctr < LOWER_LIM] = 1
    return map
    
    
def eff_corr(ds, map):
#    for fm in ds:
#        fm /= map
    res = ds / map
    res.copy_metadata_shallow(ds)
    res.append_log('Processed with: efficiency correction with ' + str(map.title))
    return res

def geo_corr(ds, enabled):
    global DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE
    global DEGREE_RAD_COEFFICIENT
    sdd = DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE
    try:
        sdd = ds.sample_to_detector_distance
    except:
        pass
    sdds = sdd ** 2
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
    
    if enabled:
        d_shape = [y_len, x_len]
        pixel_2theta = array.instance([y_len, x_len + 1], dtype = float)
        
        if is_fixed_stth :
            res = dataset.instance(ds.shape, dtype = float)
            
            y_bounds = ds.axes[-2].__iArray__
            y_centres = AxisRecord.createCentres(y_bounds)
            x_bounds = ds.axes[-1].__iArray__
            GeometryCorrection.calculateTwoThetaPixel(sdd, sdds, x_bounds, cosStth, sinStth, \
                                                 y_centres, pixel_2theta.__iArray__)
            axis_2theta = array.instance([x_len + 1], dtype = float)
            GeometryCorrection.calculateTwoThetaAxis(sdd, sdds, x_bounds, cosStth, \
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
            res.axes[0] = ds.axes[0]
            res.axes[1] = ds.axes[1]
            res.axes[2] = axis_2theta
            res.axes[2].title = 'two theta'
            res.copy_metadata_shallow(ds)
            res.append_log('Processed with: geometry curve correction')
            res.append_log('Processed with: calculating two theta on LDS=%.1f mm' % sdd)
        else:
            res = dataset.instance(ds.shape, dtype = float)
            
            y_bounds = ds.axes[-2].__iArray__
            y_centres = AxisRecord.createCentres(y_bounds)
            x_bounds = ds.axes[-1].__iArray__
            two_theta_axes = array.instance([ds.shape[0], x_len + 1], dtype = float)
            for i in xrange(ds.shape[0]):
                currentStth = stth[i] / DEGREE_RAD_COEFFICIENT
                sinStth = math.sin(currentStth)
                cosStth = math.cos(currentStth)
                pixel_2theta = array.instance([y_len, x_len + 1], dtype = float)
                GeometryCorrection.calculateTwoThetaPixel(sdd, sdds, x_bounds, cosStth, sinStth, \
                                                     y_centres, pixel_2theta.__iArray__)
                axis_2theta = array.instance([x_len + 1], dtype = float)
                GeometryCorrection.calculateTwoThetaAxis(sdd, sdds, x_bounds, cosStth, \
                                                     sinStth, axis_2theta.__iArray__)
                two_theta_axes[i] = axis_2theta
                relocateLeftIndexArray = array.instance(d_shape, dtype = int)
                relocateRightIndexArray = array.instance(d_shape, dtype = int)
                relocateLeftRateArray = array.instance(d_shape, dtype = float)
                relocateRightRateArray = array.instance(d_shape, dtype = float)
                relocateCounterArray = array.instance(d_shape, dtype = float)
                
                GeometryCorrection.rebinWithTwoTheta(ds[i].__iArray__, ds[i].var.__iArray__, \
                            res[i].__iArray__, res[i].var.__iArray__, pixel_2theta.__iArray__, \
                            axis_2theta.__iArray__, relocateLeftIndexArray.__iArray__, \
                            relocateRightIndexArray.__iArray__, relocateLeftRateArray.__iArray__, \
                            relocateRightRateArray.__iArray__, relocateCounterArray.__iArray__, \
                            True)
            res.axes[0] = ds.axes[0]
            res.axes[1] = ds.axes[1]
            res.axes[2] = two_theta_axes[0]
            res.axes[2].title = 'two theta'
            res.copy_metadata_shallow(ds)
            res.two_theta_axes = two_theta_axes
            res.append_log('Processed with: geometry curve correction')
            res.append_log('Processed with: calculating two theta on LDS=%.1f mm' % sdd)
        return res
    else:
        x_bounds = ds.axes[2].__iArray__
        two_theta_axes = array.instance([ds.shape[0], x_len + 1], dtype = float)
        for i in xrange(ds.shape[0]):
                currentStth = stth[i] / DEGREE_RAD_COEFFICIENT
                sinStth = math.sin(currentStth)
                cosStth = math.cos(currentStth)
                axis_2theta = array.instance([x_len + 1], dtype = float)
                GeometryCorrection.calculateTwoThetaAxis(sdd, sdds, x_bounds, cosStth, \
                                                     sinStth, axis_2theta.__iArray__)
                two_theta_axes[i] = axis_2theta
            
        ds.axes[2] = two_theta_axes[0]
        ds.axes[2].title = 'two theta'
        ds.two_theta_axes = two_theta_axes
        ds.append_log('Processed with: calculating two theta on LDS=%.1f mm' % sdd)
        return ds

#def calc_tth(ds, idx):
#    sdd = DEFAULT_SAMPLE_TO_DETECTOR_DISTANCE
#    try:
#        sdd = ds.sample_to_detector_distance
#    except:
#        pass
#    sdds = sdd ** 2
#    stth = ds.stth
#    if not hasattr(stth, '__len__') :
#        stth = [stth]
#    currentStth = stth[idx] / DEGREE_RAD_COEFFICIENT
#    sinStth = math.sin(currentStth)
#    cosStth = math.cos(currentStth)
#    
#    y_len = ds.axes[-2].size - 1
#    x_len = ds.axes[-1].size - 1
#    axis_2theta = array.instance([x_len + 1], dtype = float)
#    x_bounds = ds.axes[2].__iArray__
#    GeometryCorrection.calculateTwoThetaAxis(sdds, x_bounds, cosStth, \
#                                             sinStth, axis_2theta.__iArray__)
#    print axis_2theta
#    return axis_2theta
    
def v_intg(ds, masks):
    if len(masks) > 0 :
        is_fixed_stth = True
        if len(ds) > 1 and math.fabs(ds.stth[0] - ds.stth[-1]) > 1e-3:
            is_fixed_stth = False
        if is_fixed_stth:
            x_axis = ds.axes[-1]
            y_axis = ds.axes[-2]
            res = dataset.instance([ds.shape[0], ds.shape[2]], float('NaN'), dtype=float)
            for mask in masks:
                y_iMin = int((mask.minY - y_axis[0]) / (y_axis[-1] - y_axis[0]) \
                             * (y_axis.size - 1))
                if y_iMin < 0 :
                    y_iMin = 0
                if y_iMin >= y_axis.size:
                    continue
                y_iMax = int((mask.maxY - y_axis[0]) / (y_axis[-1] - y_axis[0]) \
                             * (y_axis.size - 1)) + 1
                if y_iMax < 0:
                    continue
                x_iMin = int((mask.minX - x_axis[0]) / (x_axis[-1] - x_axis[0]) \
                             * (x_axis.size - 1))
                if x_iMin < 0:
                    x_iMin = 0;
                if x_iMin >= x_axis.size:
                    continue
                x_iMax = int((mask.maxX - x_axis[0]) / (x_axis[-1] - x_axis[0]) \
                             * (x_axis.size - 1)) + 1
                if x_iMax < 0:
                    continue
                res[:, x_iMin : x_iMax] = ds[:, y_iMin : y_iMax, x_iMin : x_iMax].intg(1)
            res.axes[0] = ds.axes[0]
            res.axes[1] = ds.axes[2]
            mask = masks[0]
            res.copy_metadata_shallow(ds)
            res.append_log('Processed with: apply mask y in [' + str(mask.minY) + ',' \
                           + str(mask.maxY) + '], x in [' + str(mask.minX) + ',' + str(mask.maxX) + ']')
            return res
        else :
            y_axis = ds.axes[-2]
            res = dataset.instance([ds.shape[0], ds.shape[2]], float('NaN'), dtype=float)
            for i in xrange(len(ds)):
                x_axis = ds.two_theta_axes[i]
                for mask in masks:
                    y_iMin = int((mask.minY - y_axis[0]) / (y_axis[-1] - y_axis[0]) \
                                 * (y_axis.size - 1))
                    if y_iMin < 0 :
                        y_iMin = 0
                    if y_iMin >= y_axis.size:
                        continue
                    y_iMax = int((mask.maxY - y_axis[0]) / (y_axis[-1] - y_axis[0]) \
                                 * (y_axis.size - 1)) + 1
                    if y_iMax < 0:
                        continue
                    x_iMin = int((mask.minX - x_axis[0]) / (x_axis[-1] - x_axis[0]) \
                                 * (x_axis.size - 1))
                    if x_iMin < 0:
                        x_iMin = 0;
                    if x_iMin >= x_axis.size:
                        continue
                    x_iMax = int((mask.maxX - x_axis[0]) / (x_axis[-1] - x_axis[0]) \
                                 * (x_axis.size - 1)) + 1
                    if x_iMax < 0:
                        continue
                    res[i, x_iMin : x_iMax] = ds[i, y_iMin : y_iMax, x_iMin : x_iMax].intg(0)
            res.axes[0] = ds.axes[0]
            res.axes[1] = ds.axes[2]
            mask = masks[0]
            if hasattr(ds, 'two_theta_axes'):
                res.two_theta_axes = ds.two_theta_axes
            res.copy_metadata_shallow(ds)
            res.append_log('Processed with: apply mask y in [' + str(mask.minY) + ',' \
                           + str(mask.maxY) + '], x in [' + str(mask.minX) + ',' + str(mask.maxX) + ']')
            return res
    else:
        return ds.intg(1)
            
def i_intg(ds):
    return ds.sum(0)

def v_export(ds, path):
    sn = 'KWR%07d'%ds.id
    ext = ''
    log = ds.log
    if log.__contains__('efficiency') :
        ext += 'e'
    if log.__contains__('geometry') :
        ext += 'g'
    if log.__contains__('y in [') :
        minfo = log[log.index('y in [') : ]
        minfo = minfo[6 : minfo.index(']')]
        ext += '_' + minfo.replace(',', '_')
    if len(ext) > 0 :
        if not ext.startswith('_') :
            sn += '_'
        sn += ext
    sn += '.xyd'
    
    f = open(path + '/' + sn, 'w')
    
    if f is None:
        print 'failed to make file ' + path + '/' + sn
        
    loc = ds.location
    if loc.startswith('/') :
        loc = loc[1:]
    if len(ds) > 1:
        text = '# Raw nexus file: %s\n' % loc
        text += '# \texperiment_title=%s \tsample_name=%s\n' % (str(ds.experiment_title), \
                                                               str(ds.sample_name))
        text += '# \tsample_description=%s\n' % str(ds.sample_description)
        text += '# \tuser_name=%s\n' % str(ds.user_name)
        text += '# DETECTOR resolution=(421,421) \tactive_width=280.0 mm \tmode=%s \tpreset=%s\n' % \
                    (str(ds.mode), str(ds.preset))
        text += '# SAMPLE environment\n'
        text += '# \tsx=%.5f mm \tsy=%.5f mm \tsz=%.5f mm\n' % (ds.sx[0], ds.sy[0], ds.sz[0])
        text += '# \tsom=%.5f degrees \tstth=%.5f degrees\n' % (ds.som[0], ds.stth[0])
        text += '# MONOCHROMATOR environment\n'
        text += '# \tmphi=%.5f degrees \tmchi=%.5f degrees\n' % (ds.mphi[0], ds.mchi[0])
        text += '# \tmx=%.5f mm \tmy=%.5f mm\n' % (ds.mx[0], ds.my[0])
        text += '# \tmom=%.5f degrees \tmtth=%.5f degrees\n' % (ds.mom[0], ds.mtth[0])
        text += '# \tmf1=%.5f degrees \tmf2=%.5f degrees\n' % (ds.mf1[0], ds.mf2[0])
        text += '# SLITS environment\n'
        text += '# \tpsp=%.5f mm \tpsw=%.5f mm \tpsho=%.5f mm\n' % (ds.psp[0], ds.psw[0], ds.psho[0])
        text += '# \tssp=%.5f mm \tssho=%.5f mm\n' % (ds.ssp[0], ds.ssho[0])
        text += '# ' + log.replace('\n', '\n# ') + '\n'
        scan_var = ds.axes[0]
        x_axis = ds.axes[1]
        for i in xrange(ds.shape[0]):
            if hasattr(ds, 'two_theta_axes'):
                x_axis = ds.two_theta_axes[i]
            text += '# Scan variable: %s=%f\n' % (scan_var.title, scan_var[i])
            text += '# time=%f seconds \tbm1_counts=%d\n' % (ds.detector_time[i], ds.bm1_counts[i])
            text += '# Two Theta \tIntensity Integration \tSigma\n'
            for j in xrange(ds.shape[1]):
                val = ds[i, j]
                var = ds.var[i, j]
                text += '%10.5f %15.5f %15.5f\n' % ((x_axis[j + 1] + x_axis[j]) / 2, \
                                        (val if not math.isnan(val) else 0), \
                                        (math.sqrt(var) if not math.isnan(var) and var != 0 else 1))
            text += '\n'
    else :
        text = '# Raw nexus file: %s\n' % loc
        text += '# \texperiment_title=%s \tsample_name=%s\n' % (str(ds.experiment_title), \
                                                               str(ds.sample_name))
        text += '# \tsample_description=%s\n' % str(ds.sample_description)
        text += '# \tuser_name=%s\n' % str(ds.user_name)
        text += '# DETECTOR resolution=(421,421) \tactive_width=280.0 mm \tmode=%s \tpreset=%s\n' % \
                    (str(ds.mode), str(ds.preset))
        text += '# SAMPLE environment\n'
        text += '# \tsx=%.5f mm \tsy=%.5f mm \tsz=%.5f mm\n' % (ds.sx, ds.sy, ds.sz)
        text += '# \tsom=%.5f degrees \tstth=%.5f degrees\n' % (ds.som, ds.stth)
        text += '# MONOCHROMATOR environment\n'
        text += '# \tmphi=%.5f degrees \tmchi=%.5f degrees\n' % (ds.mphi, ds.mchi)
        text += '# \tmx=%.5f mm \tmy=%.5f mm\n' % (ds.mx, ds.my)
        text += '# \tmom=%.5f degrees \tmtth=%.5f degrees\n' % (ds.mom, ds.mtth)
        text += '# \tmf1=%.5f degrees \tmf2=%.5f degrees\n' % (ds.mf1, ds.mf2)
        text += '# SLITS environment\n'
        text += '# \tpsp=%.5f mm \tpsw=%.5f mm \tpsho=%.5f mm\n' % (ds.psp, ds.psw, ds.psho)
        text += '# \tssp=%.5f mm \tssho=%.5f mm\n' % (ds.ssp, ds.ssho)
        text += '# ' + log.replace('\n', '\n# ') + '\n'
        scan_var = ds.axes[0]
        x_axis = ds.axes[1]
        for i in xrange(ds.shape[0]):
            if hasattr(ds, 'two_theta_axes'):
                x_axis = ds.two_theta_axes[i]
            text += '# Scan variable: %s=%f\n' % (scan_var.title, scan_var[i])
            text += '# time=%f seconds \tbm1_counts=%d\n' % (ds.detector_time, ds.bm1_counts)
            text += '# Two Theta \tIntensity Integration \tSigma\n'
            for j in xrange(ds.shape[1]):
                val = ds[i, j]
                var = ds.var[i, j]
                text += '%10.5f %15.5f %15.5f\n' % ((x_axis[j + 1] + x_axis[j]) / 2, \
                                        (val if not math.isnan(val) else 0), \
                                        (math.sqrt(var) if not math.isnan(var) and var != 0 else 1))
            text += '\n'
    f.write(text)
    f.close()
    

def i_export(ds, path):
    sn = 'KWR%07d'%ds.id
    ext = ''
    log = ds.log
    if log.__contains__('efficiency') :
        ext += 'e'
    if log.__contains__('geometry') :
        ext += 'g'
    if log.__contains__('y in [') :
        minfo = log[log.index('y in [') : ]
        minfo = minfo[6 : minfo.index(']')]
        ext += '_' + minfo.replace(',', '_')
    if len(ext) > 0 :
        if not ext.startswith('_') :
            sn += '_'
        sn += ext
    sn += '.xid'
    
    f = open(path + '/' + sn, 'w')
    
    if f is None:
        print 'failed to make file ' + path + '/' + sn
        
    loc = ds.location
    if loc.startswith('/') :
        loc = loc[1:]
    if len(ds) > 1:
        text = '# Raw nexus file: %s\n' % loc
        text += '# \texperiment_title=%s \tsample_name=%s\n' % (str(ds.experiment_title), \
                                                               str(ds.sample_name))
        text += '# \tsample_description=%s\n' % str(ds.sample_description)
        text += '# \tuser_name=%s\n' % str(ds.user_name)
        text += '# DETECTOR resolution=(421,421) \tactive_width=280.0 mm \tmode=%s \tpreset=%s\n' % \
                    (str(ds.mode), str(ds.preset))
        text += '# SAMPLE environment\n'
        text += '# \tsx=%.5f mm \tsy=%.5f mm \tsz=%.5f mm\n' % (ds.sx[0], ds.sy[0], ds.sz[0])
        text += '# \tsom=%.5f degrees \tstth=%.5f degrees\n' % (ds.som[0], ds.stth[0])
        text += '# MONOCHROMATOR environment\n'
        text += '# \tmphi=%.5f degrees \tmchi=%.5f degrees\n' % (ds.mphi[0], ds.mchi[0])
        text += '# \tmx=%.5f mm \tmy=%.5f mm\n' % (ds.mx[0], ds.my[0])
        text += '# \tmom=%.5f degrees \tmtth=%.5f degrees\n' % (ds.mom[0], ds.mtth[0])
        text += '# \tmf1=%.5f degrees \tmf2=%.5f degrees\n' % (ds.mf1[0], ds.mf2[0])
        text += '# SLITS environment\n'
        text += '# \tpsp=%.5f mm \tpsw=%.5f mm \tpsho=%.5f mm\n' % (ds.psp[0], ds.psw[0], ds.psho[0])
        text += '# \tssp=%.5f mm \tssho=%.5f mm\n' % (ds.ssp[0], ds.ssho[0])
        text += '# ' + log.replace('\n', '\n# ') + '\n'
        x_axis = ds.axes[0]
        text += '# %s \tIntensity Integration \tSigma\n' % x_axis.title
        for i in xrange(len(ds)):
            val = ds[i]
            var = ds.var[i]
            text += '%10.5f %15.5f %15.5f\n' % (x_axis[i], \
                                (val if not math.isnan(val) else 0), \
                                (math.sqrt(var) if not math.isnan(var) and var != 0 else 1))
        text += '\n'
    else :
        text = '# Raw nexus file: %s\n' % loc
        text += '# \texperiment_title=%s \tsample_name=%s\n' % (str(ds.experiment_title), \
                                                               str(ds.sample_name))
        text += '# \tsample_description=%s\n' % str(ds.sample_description)
        text += '# \tuser_name=%s\n' % str(ds.user_name)
        text += '# DETECTOR resolution=(421,421) \tactive_width=280.0 mm \tmode=%s \tpreset=%s\n' % \
                    (str(ds.mode), str(ds.preset))
        text += '# SAMPLE environment\n'
        text += '# \tsx=%.5f mm \tsy=%.5f mm \tsz=%.5f mm\n' % (ds.sx, ds.sy, ds.sz)
        text += '# \tsom=%.5f degrees \tstth=%.5f degrees\n' % (ds.som, ds.stth)
        text += '# MONOCHROMATOR environment\n'
        text += '# \tmphi=%.5f degrees \tmchi=%.5f degrees\n' % (ds.mphi, ds.mchi)
        text += '# \tmx=%.5f mm \tmy=%.5f mm\n' % (ds.mx, ds.my)
        text += '# \tmom=%.5f degrees \tmtth=%.5f degrees\n' % (ds.mom, ds.mtth)
        text += '# \tmf1=%.5f degrees \tmf2=%.5f degrees\n' % (ds.mf1, ds.mf2)
        text += '# SLITS environment\n'
        text += '# \tpsp=%.5f mm \tpsw=%.5f mm \tpsho=%.5f mm\n' % (ds.psp, ds.psw, ds.psho)
        text += '# \tssp=%.5f mm \tssho=%.5f mm\n' % (ds.ssp, ds.ssho)
        text += '# ' + log.replace('\n', '\n# ') + '\n'
        x_axis = ds.axes[0]
        text += '# %s \tIntensity Integration \tSigma\n' % x_axis.title
        val = ds[0]
        var = ds.var[0]
        text += '%10.5f %15.5f %15.5f\n' % (x_axis[0], \
                                        (val if not math.isnan(val) else 0), \
                                        (math.sqrt(var) if not math.isnan(var) and var != 0 else 1))
        text += '\n'
        
    f.write(text)
    f.close()