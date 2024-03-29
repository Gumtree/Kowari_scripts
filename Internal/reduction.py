from Internal import lib
import math
from gumpy.vis.event import MouseListener, MaskEventListener, AWTMouseListener
from gumpy.nexus.fitting import Fitting, GAUSSIAN_FITTING
from org.gumtree.vis.mask import RectangleMask
from org.gumtree.vis.hist2d.color import ColorScale


# Script control setup area
# script info
__script__.title = 'Kowari Reduction'
__script__.version = '2.0'

# Use below example to create parameters.
# The type can be string, int, float, bool, file.

SAVED_EFFICIENCY_FILENAME_PRFN = 'kowari.savedEfficiency'
SAVED_MASK_PRFN = 'kowari.savedMasks'

class NavMouseListener(MouseListener):
    
    def __init__(self):
        MouseListener.__init__(self)
        
    def on_double_click(self, event):
        x = event.getX()
        try:
            idx = var_jump.options.index(x)
            ind_jump.value = idx
        except:
            print 'script control has been updated, please run the reduction again.'
            
reg_changed = False
__mask_updated__ = False

class RegionEventListener(MaskEventListener):
    
    def __init__(self):
        MaskEventListener.__init__(self)
    
    def mask_added(self, mask):
        pass
            
    def mask_removed(self, mask):
        global reg_changed
        if not reg_changed:
            update_mask_list()
            run_intg()
    
    def mask_updated(self, mask):
        global reg_changed
        global __mask_updated__
        if not reg_changed:
            update_mask_list()
        __mask_updated__ = True
        
regionListener = RegionEventListener()

class MousePressListener(AWTMouseListener):
    def __init__(self):
        AWTMouseListener.__init__(self)
    
    def mouse_released(self, event):
        global __mask_updated__
        if __mask_updated__ :
            run_intg()
            __mask_updated__ = False
    
mouse_press_listener = MousePressListener()

if not 'DS' in globals():
    DS = None
    VI = None
    IR = None

INT_EXP_OPTIONS = ["default - use current mask", \
                   "use the whole detector", \
                   "split detector into 2 strips", \
                   "split detector into 3 strips", \
                   "split detector into 4 strips", \
                   "split detector into 5 strips", \
                   ]

prog_bar = Par('progress', 0)
ind_jump = Par('int', -1, options=[], command='jump_to_index()')
ind_jump.title = 'select to show data at index'
var_jump = Par('float', float('NAN'), [], command='jump_to_var()')
var_jump.title = 'select scan variable at '
g_jump = Group('Jump to Scan Index')
g_jump.add(ind_jump, var_jump)

def jump_to_var():
    var = var_jump.value
    log('jump to scan variable = ' + str(var))
    if math.isnan(var) :
        return
    idx = var_jump.options.index(var)
    ind_jump.value = idx

def update_plot2(ds):
    global Plot2
    dss = Plot2.ds
    f_curve = None
    if dss != None and len(dss) > 0:
        for item in dss:
            if str(item.title) == 'fitting':
                f_curve = item
    Plot2.set_dataset(ds)
    if not f_curve is None:
        Plot2.add_dataset(f_curve)
    
def update_plots(idx):
    if DS is None:
        return
    prog_bar.max = 2
    prog_bar.selection = 1
    stth = DS.stth
    is_fixed_stth = True
    if len(DS) > 1 and math.fabs(stth[0] - stth[-1]) > 1e-3:
        is_fixed_stth = False
    if is_fixed_stth:
        Plot1.set_dataset(DS[idx])
        Plot1.title = str(DS.id) + "_" + str(idx)
        prog_bar.selection = 2
#        Plot2.set_dataset(VI[idx])
        update_plot2(VI[idx])
        Plot2.title = str(DS.id) + "_integration_" + str(idx)
    else:
        DS.axes[2] = DS.two_theta_axes[idx]
        DS.axes.title = 'two theta'
        VI.axes[1] = DS.two_theta_axes[idx]
        VI.axes.title = 'two theta'
        Plot1.set_dataset(DS[idx])
        Plot1.title = str(DS.id) + "_" + str(idx)
        prog_bar.selection = 2
#        Plot2.set_dataset(VI[idx])
        update_plot2(VI[idx])
        Plot2.title = str(DS.id) + "_integration_" + str(idx)
    if Plot1.x_label != 'Two Theta (degree)':
        Plot1.x_label = 'Two Theta (degree)'
        Plot1.y_label = 'Detector Y (mm)'
    if Plot1.y_label != 'Two Theta (degree)':
        Plot2.x_label = 'Two Theta (degree)'
        Plot2.y_label = 'Counts'
    prog_bar.selection = 0
    
def jump_to_index():
    idx = ind_jump.value
    log('jump to index ' + str(idx))
    if idx < 0 or DS == None or idx >= len(DS):
        return
    update_plots(idx)
    if var_jump.value != var_jump.options[idx]:
        var_jump.value = var_jump.options[idx]

eff_corr_enabled = Par('bool', True)
eff_corr_enabled.title = 'efficiency correction enabled'
eff_map = Par('file', u'D:\EXPERIMENTS\STRESS\KWR0039477 calibration.nx.hdf')
d_map = get_prof_value(SAVED_EFFICIENCY_FILENAME_PRFN)
if not d_map is None and d_map.strip() != '':
    eff_map.value = d_map
eff_map.title = 'efficiency map file'
g_eff = Group('Efficiency Correction')
g_eff.add(eff_corr_enabled, eff_map)

geo_corr_enabled = Par('bool', True)
geo_corr_enabled.title = 'geometry correction enabled'
g_geo = Group('Geometry Correction')
g_geo.add(geo_corr_enabled)

reg_enabled = Par('bool', True)
reg_enabled.title = 'region selection enabled'
reg_enabled.colspan = 2
#reg_list = Par('string', '', command='change_masks()')
reg_list = Par('string', '')
def change_masks():
    global reg_changed
    reg_changed = True
    masks = Plot1.get_masks()
    if masks != None and len(masks) > 0:
        for mask in masks:
            Plot1.remove_mask(mask)
    if reg_list.value != None and reg_list.value.strip() != '':
        masks = str2maskstr(reg_list.value)
        for mask in masks:
            Plot1.add_mask_2d(float(mask[0]), float(mask[1]), \
                              float(mask[2]), float(mask[3]), mask[4])
    run_intg()
    reg_changed = False
    print 'masks are updated'
        
def str2maskstr(value):
    items = value.split(';')
    res = []
    for item in items:
        name = item[0:item.index('[')];
        rstr = item[item.index('[') + 1 : item.index(']')]
        range = rstr.split(',')
        range.append(name)
        res.append(range)
    return res

def str2mask(value):
    items = value.split(';')
    masks = []
    for item in items:
        name = item[0:item.index('[')];
        rstr = item[item.index('[') + 1 : item.index(']')]
        range = rstr.split(',')
        mask = RectangleMask(True, float(range[0]), float(range[2]), \
                             float(range[1]) - float(range[0]), \
                             float(range[3]) - float(range[2]))
        mask.name = name
        masks.append(mask)
    return masks

def mask2str(masks):
    res = ''
    for mask in masks:
        res += mask.name
        res += '[' + ('%.1f' % round(mask.minX, 1)) + ',' + ('%.1f' % round(mask.maxX, 1)) + ',' \
                + ('%d' % round(mask.minY)) + ',' + ('%d' % round(mask.maxY)) + ']'
        if masks.indexOf(mask) < len(masks) - 1:
            res += ';'
    return res

s_mask = get_prof_value(SAVED_MASK_PRFN)
if not s_mask is None and s_mask.strip() != '':
    reg_list.value = s_mask
reg_list.title = 'masks[x_min, x_max, y_min, y_max]'
reg_list.enabled = True
reg_list.colspan = 2
reg_discard = Act('discard_masks()', 'Discard Mask Change')
reg_accept = Act('accept_masks()', 'Accept Mask Change')
g_reg = Group('Region Selection')
g_reg.numColumns = 2
g_reg.add(reg_enabled, reg_list, reg_discard, reg_accept)
def accept_masks():
    change_masks()
def discard_masks():
    update_mask_list()

# Use below example to create a button
act_reduce = Act('reduce()', 'REDUCE SELECTED DATA')
 
fit = Group('Fitting in Plot2')
fit.numColumns = 2
fit_min = Par('float', 'NaN')
fit_max = Par('float', 'NaN')
fit_act = Act('fit_curve()', 'Gaussian Fit Plot2')
fit_act.colspan = 2
peak_pos = Par('float', 'NaN')
FWHM = Par('float', 'NaN')
fit.add(fit_min, fit_max, fit_act, peak_pos, FWHM)
def fit_curve():
    global Plot2
    ds = Plot2.ds
    if len(ds) == 0:
        log('Error: no curve to fit in Plot2.\n')
        return
    for d in ds:
        if d.title == 'fitting':
            Plot2.remove_dataset(d)
    d0 = ds[0]
    fitting = Fitting(GAUSSIAN_FITTING)
    try:
        fitting.set_histogram(d0, fit_min.value, fit_max.value)
        val = peak_pos.value
        if val == val:
            fitting.set_param('mean', val)
        val = FWHM.value
        if val == val:
            fitting.set_param('sigma', math.fabs(val / 2.35482))
        res = fitting.fit()
        res.var[:] = 0
        res.title = 'fitting'
        Plot2.add_dataset(res)
        mean = fitting.params['mean']
        mean_err = fitting.errors['mean']
        FWHM.value = 2.35482 * math.fabs(fitting.params['sigma'])
        FWHM_err = 5.54518 * math.fabs(fitting.errors['sigma'])
        log('POS_OF_PEAK=' + str(mean) + ' +/- ' + str(mean_err))
        log('FWHM=' + str(FWHM.value) + ' +/- ' + str(FWHM_err))
        log('Chi2 = ' + str(fitting.fitter.getQuality()))
        peak_pos.value = fitting.mean
#        print fitting.params
    except:
#        traceback.print_exc(file = sys.stdout)
        log('can not fit\n')
        
exp_mask = Par('str', INT_EXP_OPTIONS[0], options=INT_EXP_OPTIONS)
exp_b = Act('integration_export()', 'Export Profile')
g_exp = Group('Profile Export')
g_exp.add(exp_mask, exp_b)

exp_i = Act('intensity_export()', 'Export Integrated Intensity')
g_int = Group('Integrated Intensity Export')
g_int.add(exp_i)


def reduce():
    global DS
    global VI
    global IR
    
    old_id = -1
    if not DS is None:
        old_id = DS.id 
    li = __DATASOURCE__.getSelectedDatasets()
    if len(li) == 0:
        open_error('Please select a file from the file source view.')
        return
    if Plot1.pv.getPlot() is None:
        Plot1.set_dataset(instance([2, 2]))
        Plot1.set_color_scale(ColorScale.Spectrum)

    prog_bar.max = 5
    prog_bar.selection = 0
    df.datasets.clear()
    DS = df[str(li[0].location)]
    curr_idx = -1
    if old_id == DS.id:
        curr_idx = ind_jump.value
    location = DS.location
    id = DS.id
    title = DS.title
    if DS.ndim == 4 :
        DS = DS.get_reduced(1)
    DS = lib.fix_detector_dimension(DS)
    
    prog_bar.selection = 1
    if eff_corr_enabled.value and eff_map.value != None \
            and len(eff_map.value.strip()) > 0:
        log('running efficiency correction')
        map = lib.make_eff_map(df, str(eff_map.value))
        DS = lib.eff_corr(DS, map)
        
    prog_bar.selection = 2
    if geo_corr_enabled.value :
        log('running geometry correction')
    DS = lib.geo_corr(DS, geo_corr_enabled.value)

    DS.location = location
    DS.id = id
    DS.title = title
#    Plot1.set_dataset(DS[0])
#    Plot1.title = str(DS.id) + '_0'
#    Plot1.set_mask_listener(regionListener)
        
    masks = []
    if reg_enabled.value :
        if len(Plot1.get_masks()) > 0:
            masks = Plot1.get_masks()
        else :
            if reg_list.value != None and reg_list.value.strip() != '':
                masks = str2maskstr(reg_list.value)
                for mask in masks:
                    Plot1.add_mask_2d(float(mask[0]), float(mask[1]), \
                                      float(mask[2]), float(mask[3]), mask[4])
                masks = Plot1.get_masks()
    
    prog_bar.selection = 3
    log('running vertical integration')
    VI = lib.v_intg(DS, masks)
    
#    Plot2.set_dataset(VI[0])
#    Plot2.title = str(DS.id) + "_integration_0"

    ind_jump.options = range(DS.shape[0])
    var_jump.options = DS.axes[0].tolist()
    if curr_idx == -1:
        ind_jump.value = 0
    else:
        ind_jump.value = curr_idx
        update_plots(curr_idx)
    
    prog_bar.selection = 4
    log('running intensity integration')
    IR = lib.i_intg(VI)

    prog_bar.selection = 5
    Plot3.set_dataset(IR)
    Plot3.title = str(DS.id) + "_intensity"
    Plot3.set_mouse_listener(NavMouseListener())
    
    Plot1.set_awt_mouse_listener(mouse_press_listener)
    Plot1.set_mask_listener(regionListener)
    prog_bar.selection = 0
    
    set_prof_value(SAVED_MASK_PRFN , str(reg_list.value))
    set_prof_value(SAVED_EFFICIENCY_FILENAME_PRFN , str(eff_map.value))
    save_pref()
    
def run_intg():
    global DS
    global VI
    global IR
    log('running vertical integration')
    masks = Plot1.get_masks()
    VI = lib.v_intg(DS, masks)
#    Plot2.set_dataset(VI[0])
#    Plot2.title = str(DS.id) + "_integration_0"

    ind_jump.options = range(DS.shape[0])
    var_jump.options = DS.axes[0].tolist()
    update_plots(ind_jump.value)
    
    log('running intensity integration')
    IR = lib.i_intg(VI)
    Plot3.set_dataset(IR)
    Plot3.title = str(DS.id) + "_intensity"
    Plot3.set_mouse_listener(NavMouseListener())
    __mask_locked__ = False
    
    set_prof_value(SAVED_MASK_PRFN , str(reg_list.value))
    save_pref()

        
# def apply_region(ds, masks):
#    map = array.instance([ds.shape[-2], ds.shape[-1]], dtype=bool)
#    rds = instance(ds.shape)
#    x_axis = ds.axes[-1]
#    y_axis = ds.axes[-2]
#    for mask in masks :
#        for i in xrange(len(x_axis)):
#            if ix > 
        
    
# Use below example to create a new Plot
# Plot4 = Plot(title = 'new plot')

# This function is called when pushing the Run button in the control UI.
def __run_script__(fns):
    # Use the provided resources, please don't remove.
    reduce()
    
def __dataset_added__(fn):
    pass
    
def __dispose__():
    global Plot1
    global Plot2
    global Plot3
    Plot1.clear()
    Plot2.clear()
    Plot3.clear()

def precision_string(val, precision):
    return '%.2f' % val
    
def update_mask_list():
    if Plot1.ndim > 0:
        reg_list.value = mask2str(Plot1.get_masks())

if reg_list.value.strip() == '':
    update_mask_list()

def silent_reduce(ds, map=None):
    location = ds.location
    id = ds.id
    title = ds.title
    if ds.ndim == 4:
        ds = ds.get_reduced(1)
    
    if not map is None:
        ds = lib.eff_corr(ds, map)
        
    rds = lib.geo_corr(ds, geo_corr_enabled.value)
#    ds.close()
    rds.id = id
    return rds

#    masks = []
#    if reg_enabled.value :
#        try:
#            masks = Plot1.get_masks()
#        except:
#            pass
#    
#    vi = lib.v_intg(ds, masks)
#
#    vi.location = location
#    vi.id = id
#    vi.title = title
#        
#    ir = lib.i_intg(vi)
#    return [vi, ir]
    
def integration_export():
    global INT_EXP_OPTIONS
    path = selectSaveFolder()
    if path == None:
        return
    dss = __DATASOURCE__.getSelectedDatasets()
    if len(dss) == 0:
        print 'Error: please select at least one data file.'
    prog_bar.max = len(dss) + 1
    prog_bar.selection = 0
    if len(dss) == 0:
        return
    fi = File(path)
    if not fi.exists():
        if not fi.mkdir():
            print 'Error: failed to make directory: ' + path
            return
    if eff_corr_enabled.value and eff_map.value != None \
            and len(eff_map.value.strip()) > 0:
        map = lib.make_eff_map(df, str(eff_map.value))
    else:
        map = None
    dss_idx = 0
    for dinfo in dss:
        dss_idx += 1
        prog_bar.selection = dss_idx
        df.datasets.clear()
        log('exporting ' + dinfo.location)
        ds = df[str(dinfo.location)]
        rds = silent_reduce(ds, map)
        masks = []
        if exp_mask.value == INT_EXP_OPTIONS[0]:
            if reg_enabled.value :
                try:
                    masks = Plot1.get_masks()
                except:
                    pass
            if len(masks) == 0:
                if reg_list.value != None and reg_list.value.strip() != '':
                    masks = str2mask(reg_list.value)
            c_masks = []
            for m in masks:
                c_m = RectangleMask(True, -180, m.minY, 360, m.maxY - m.minY)
                c_masks.append(c_m)
            vi = lib.v_intg(rds, c_masks)
            vi.location = ds.location
            lib.v_export(vi, path)
        elif exp_mask.value == INT_EXP_OPTIONS[1]:
            vi = lib.v_intg(rds, masks)
            vi.location = ds.location
            lib.v_export(vi, path)
        else :
            idx = INT_EXP_OPTIONS.index(exp_mask.value)
            mask_group = make_mask_group(rds, idx)
            for mask in mask_group :
                vi = lib.v_intg(rds, [mask])
                vi.location = ds.location
                lib.v_export(vi, path)
    prog_bar.selection = dss_idx + 1
    prog_bar.selection = 0
    
    set_prof_value(SAVED_MASK_PRFN , str(reg_list.value))
    set_prof_value(SAVED_EFFICIENCY_FILENAME_PRFN , str(eff_map.value))
    save_pref()

    print 'Done'

def make_mask_group(ds, num):
    masks = []
    y_axis = ds.axes[1]
    y_step = (y_axis[-1] - y_axis[0]) / num
    for i in xrange(num) :
        mask = RectangleMask(True, -180, y_axis[0] + y_step * i, \
                             360, y_step)
        masks.append(mask)
    return masks

def intensity_export():
    path = selectSaveFolder()
    if path == None:
        return
    dss = __DATASOURCE__.getSelectedDatasets()
    if len(dss) == 0:
        print 'Error: please select at least one data file.'
    prog_bar.max = len(dss) + 1
    prog_bar.selection = 0
    if len(dss) == 0:
        return
    fi = File(path)
    if not fi.exists():
        if not fi.mkdir():
            print 'Error: failed to make directory: ' + path
            return
    if eff_corr_enabled.value and eff_map.value != None \
            and len(eff_map.value.strip()) > 0:
        map = lib.make_eff_map(df, str(eff_map.value))
    else:
        map = None
    dss_idx = 0
    for dinfo in dss:
        dss_idx += 1
        prog_bar.selection = dss_idx
        df.datasets.clear()
        log('exporting ' + dinfo.location)
        ds = df[str(dinfo.location)]
        rds = silent_reduce(ds, map)
        masks = []
        if reg_enabled.value :
            try:
                masks = Plot1.get_masks()
            except:
                pass
            if len(masks) == 0:
                if reg_list.value != None and reg_list.value.strip() != '':
                    masks = str2mask(reg_list.value)

        vi = lib.v_intg(rds, masks)
        ir = lib.i_intg(vi)
        ir.copy_metadata_shallow(vi)
        ir.location = ds.location
        lib.i_export(ir, path)
    prog_bar.selection = dss_idx + 1
    prog_bar.selection = 0
    
    set_prof_value(SAVED_MASK_PRFN , str(reg_list.value))
    set_prof_value(SAVED_EFFICIENCY_FILENAME_PRFN , str(eff_map.value))
    save_pref()

    print 'Done'
