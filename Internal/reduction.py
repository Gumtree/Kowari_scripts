from Internal import lib
import math

# Script control setup area
# script info
__script__.title = 'Kowari Reduction'
__script__.version = '1.0'

# Use below example to create parameters.
# The type can be string, int, float, bool, file.

DS = None
VI = None
IR = None

ind_jump = Par('int', -1, options = [], command = 'jump_to_index()')
ind_jump.title = 'select to show data at index'
var_jump = Par('float', float('NAN'), [], command = 'jump_to_var()')
var_jump.title = 'select to show data with scan variable at '
g_jump = Group('Jump to Scan Index')
g_jump.add(ind_jump, var_jump)

def jump_to_var():
    var = var_jump.value
    log('jump to scan variable = ' + str(var))
    if math.isnan(var) :
        return
    idx = var_jump.options.index(var)
    ind_jump.value = idx
    
def jump_to_index():
    idx = ind_jump.value
    log('jump to index ' + str(idx))
    if idx < 0 or DS == None or idx >= len(DS):
        return
    Plot1.set_dataset(DS[idx])
    Plot2.set_dataset(VI[idx])
    if var_jump.value != var_jump.options[idx]:
        var_jump.value = var_jump.options[idx]

eff_corr_enabled = Par('bool', True)
eff_corr_enabled.title = 'efficiency correction enabled'
eff_map = Par('file', '')
eff_map.title = 'efficiency map file'
g_eff = Group('Efficiency Correction')
g_eff.add(eff_corr_enabled, eff_map)

geo_corr_enabled = Par('bool', True)
geo_corr_enabled.title = 'geometry correction enabled'
g_geo = Group('Geometry Correction')
g_geo.add(geo_corr_enabled)

reg_enabled = Par('bool', True)
reg_enabled.title = 'region selection enabled'
g_reg = Group('Region Selection')
g_reg.add(reg_enabled)

# Use below example to create a button
act1 = Act('reduce()', 'Reduce Selected Data') 
def reduce():
    global DS
    global VI
    global IR
    df.datasets.clear()
    li = __DATASOURCE__.getSelectedDatasets()
    if len(li) == 0:
        open_error('Please select a file from the file source view.')
        return
    DS = df[str(li[0].location)]
    location = DS.location
    id = DS.id
    title = DS.title
    DS = DS.get_reduced(1)
    Plot1.set_dataset(DS[0])
    
    if eff_corr_enabled.value and eff_map.value != None \
            and len(eff_map.value.strip()) > 0:
        log('efficiency correction')
        map = lib.make_eff_map(df, str(eff_map.value))
        lib.eff_corr(DS, map)
        
    if geo_corr_enabled.value :
        log('geometry correction')
        DS = lib.geo_corr(DS)
        
    DS.location = location
    DS.id = id
    DS.title = title
    Plot1.set_dataset(DS[0])
    ind_jump.options = range(DS.shape[0])
    var_jump.options = DS.axes[0].tolist()
    ind_jump.value = 0
        
    VI = lib.v_intg(DS)
    Plot2.set_dataset(VI[0])
    
    IR = lib.i_intg(VI)
    Plot3.set_dataset(IR)
    
# Use below example to create a new Plot
# Plot4 = Plot(title = 'new plot')

# This function is called when pushing the Run button in the control UI.
def __run_script__(fns):
    # Use the provided resources, please don't remove.
    global Plot1
    global Plot2
    global Plot3
    
    # check if a list of file names has been given
    if (fns is None or len(fns) == 0) :
        print 'no input datasets'
    else :
        for fn in fns:
            # load dataset with each file name
            ds = df[fn]
            print ds.shape
    print arg1_name.value
    
def __dispose__():
    global Plot1
    global Plot2
    global Plot3
    Plot1.clear()
    Plot2.clear()
    Plot3.clear()
