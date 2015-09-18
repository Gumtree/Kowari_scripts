# Advanced Multi-dimensional Scan Block
title "scan (<sx,sy> <4.5,5.5> <4.6,5.6> 3:sz 313.0 312.0 3) time 20.0"
histmem mode time
histmem preset 20.0

set START_NUMBER 0
set loopnumber 0
for {set idx0 0} {$idx0 < 3} {incr idx0} {
	set savenumber 0
	if {$START_NUMBER <= $loopnumber} {
		newfile HISTOGRAM_XYT
		drive sx [expr $idx0*0.049999952+4.5]
		drive sy [expr $idx0*0.049999952+5.5]
	}
	for {set idx1 0} {$idx1 < 3} {incr idx1} {
		if {$START_NUMBER <= $loopnumber} {
			drive sz [expr $idx1*-0.5+313.0]
			broadcast sx = [expr $idx0*0.049999952+4.5]
			broadcast sy = [expr $idx0*0.049999952+5.5]
			broadcast sz = [expr $idx1*-0.5+313.0]
			broadcast CURRENT LOOP = $loopnumber
			histmem start block
			save $savenumber
		}
		incr savenumber
		incr loopnumber
	}
}


