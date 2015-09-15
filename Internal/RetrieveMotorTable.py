# Script control setup area
# script info
__script__.title = 'Retrieve Motor Values'
__script__.version = '1.0'

# Use below example to create parameters.
# The type can be string, int, float, bool, file.
motor_names = Par('string', 'sx, sy, sz, som, time')

# Use below example to create a button
act1 = Act('retrieve()', 'Retrieve') 
act2 = Act('retrieve_all()', 'Retrieve to Single File')

def retrieve():
    path = selectSaveFolder()
    if path == None:
        return
    names = motor_names.value.split(',')
    
    for i in xrange(len(names)) :
        names[i] = str(names[i].strip())
    dss = __DATASOURCE__.getSelectedDatasets()
    for dinfo in dss:
        df.datasets.clear()
        loc = dinfo.getLocation()
        ds = df[str(loc)]
        dname = ds.name
        of = open(path + '/' + dname[0 : dname.index('.')] + '.csv', 'w')
        of.write(motor_names.value + '\n')
        line = ''
        if len(ds) == 1 :
            line = ('1, ' * len(names))[0 : -2]
            of.write(line + '\n')
            line = ''
            for name in names[0 : -1]:
                line += '%.2f, ' % ds[name]
            line += '%.2f' % ds[names[-1]]
            of.write(line + '\n')
        else:
            for i in xrange(len(names)):
                if math.fabs(ds[names[i]][0] - ds[names[i]][-1]) < 0.05 :
                    line += '0'
                else :
                    line += '1'
                if i < len(names) - 1 :
                    line += ', '
            of.write(line + '\n')
            for i in xrange(len(ds)):
                line = ''
                for name in names[0 : -1] :
                    line += '%.2f, ' % ds[name][i]
                line += '%.2f' % ds[names[-1]][i]
                of.write(line + '\n')
        of.close()
        print 'finished processing ' + dname
            
def retrieve_all():
    path = selectSaveFolder()
    if path == None:
        return
    names = motor_names.value.split(',')
    
    for i in xrange(len(names)) :
        names[i] = str(names[i].strip())
    dss = __DATASOURCE__.getSelectedDatasets()

    of1 = open(path + '/' + 'all.csv', 'w')
    of1.write(motor_names.value + '\n')
    of2 = open(path + '/' + 'all_with_filenames.csv', 'w')
    of2.write('filename, ' + motor_names.value + '\n')

    for dinfo in dss:
        df.datasets.clear()
        loc = dinfo.getLocation()
        ds = df[str(loc)]
        dname = ds.name
        if len(ds) == 1 :
            line = ''
            for name in names[0 : -1]:
                line += '%.2f, ' % ds[name]
            line += '%.2f' % ds[names[-1]]
            of1.write(line + '\n')
            of2.write(dname + ', ' + line + '\n')
        else:
            for i in xrange(len(ds)):
                line = ''
                for name in names[0 : -1] :
                    line += '%.2f, ' % ds[name][i]
                line += '%.2f' % ds[names[-1]][i]
                of1.write(line + '\n')
                of2.write(dname + ', ' + line + '\n')
        print 'finished processing ' + dname
    of1.close()
    of2.close()
    
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
