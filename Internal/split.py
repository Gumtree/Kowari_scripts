# Script control setup area
# script info
__script__.title = 'Split large HDF file'
__script__.version = '2.0'

# Use below example to create parameters.
# The type can be string, int, float, bool, file.
n_frame = Par('int', 100)
n_frame.title = 'Number of frames per file'
def arg1_changed():
    print 'arg1=' + str(arg1_name.value)

# Use below example to create a button
act1 = Act('split_all()', 'split all') 
#def split():
#    li = __DATASOURCE__.getSelectedDatasets()
#    for item in li:
#        df.datasets.clear()
#        ds = df[str(item.location)]
#        start = 0
#        while start < ds.shape[0]:
#            stop = start + n_frame.value
#            if stop > ds.shape[0]:
#                stop = ds.shape[0]
#            di = ds[start:stop]
#            di.save_copy(os.path.dirname(ds.location) + '/KWR' \
#                         + ('%07d' % int(ds.id)) + '_' + str(start) \
#                         + '_' + str(stop - 1) + '.hdf')
#            start = stop
    
def split_all():
    folder = selectSaveFolder()
    if folder == None:
        return
    li = __DATASOURCE__.getSelectedDatasets()
    for item in li:
        start = 0
        while True:
            df.datasets.clear()
            ds = df[str(item.location)]
            if start >= ds.shape[0]:
                break
            stop = start + n_frame.value
            if stop > ds.shape[0]:
                stop = ds.shape[0]
            flen = ds.shape[0]
            nxRoot = ds.__iNXroot__
            split_group(nxRoot, flen, start, stop)
            ds.save_copy(folder + '/KWR' \
                         + ('%07d' % int(ds.id)) + '_' + str(start) \
                         + '_' + str(stop - 1) + '.hdf')
            start = stop
    
def split_group(ncGroup, full_length, start, stop):
    for subGroup in ncGroup.getGroupList():
        split_group(subGroup, full_length, start, stop)
    for ncDataItem in ncGroup.getDataItemList():
        dataitem = SimpleData(ncDataItem)
        if len(dataitem) == full_length:
            newItem = dataitem[start : stop]
        elif len(dataitem) == full_length + 1:
            newItem = dataitem[start : stop + 1]
        else:
            continue
        newNcItem = newItem.__iDataItem__
        newNcItem.setShortName(ncDataItem.getShortName())
        ncGroup.addDataItem(newNcItem)
    
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
