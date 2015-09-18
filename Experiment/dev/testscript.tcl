# Arbitrary Scan Block
title "hmmscan sx time 10.0"
newfile HISTOGRAM_XYT
histmem mode time
histmem preset 10.0

drive sx 0.0
histmem start block
save 0

drive sx 1.0
histmem start block
save 1



# Multi-dimensional Scan Block
title "scanND (sy 0.0 2.0 3:sx 0.0 5.0 8) time 10.0"
histmem mode time
histmem preset 10.0

drive sy 0.0
drive sx 0.0
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 0.71428573
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 1.4285715
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.142857
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.857143
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 3.5714288
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 4.2857146
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 5.0000005
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sy 1.0
drive sx 0.0
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 0.71428573
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 1.4285715
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.142857
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.857143
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 3.5714288
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 4.2857146
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 5.0000005
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sy 2.0
drive sx 0.0
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 0.71428573
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 1.4285715
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.142857
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 2.857143
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 3.5714288
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 4.2857146
newfile HISTOGRAM_XYT
histmem start block
save 0

drive sx 5.0000005
newfile HISTOGRAM_XYT
histmem start block
save 0



drive sz 300.0
user test

# Advanced Multi-dimensional Scan Block
title "scan (<sx,sz> <0.0,0.0> <3.0,3.0> 4:sy 0.0 3.0 4) time 0.0"
histmem mode time
histmem preset 0.0

drive sx 0.0
drive sz 0.0
newfile HISTOGRAM_XYT
drive sy 0.0
histmem start block
save 0

drive sy 1.0
histmem start block
save 1

drive sy 2.0
histmem start block
save 2

drive sy 3.0
histmem start block
save 3

drive sx 1.0
drive sz 1.0
newfile HISTOGRAM_XYT
drive sy 0.0
histmem start block
save 0

drive sy 1.0
histmem start block
save 1

drive sy 2.0
histmem start block
save 2

drive sy 3.0
histmem start block
save 3

drive sx 2.0
drive sz 2.0
newfile HISTOGRAM_XYT
drive sy 0.0
histmem start block
save 0

drive sy 1.0
histmem start block
save 1

drive sy 2.0
histmem start block
save 2

drive sy 3.0
histmem start block
save 3

drive sx 3.0
drive sz 3.0
newfile HISTOGRAM_XYT
drive sy 0.0
histmem start block
save 0

drive sy 1.0
histmem start block
save 1

drive sy 2.0
histmem start block
save 2

drive sy 3.0
histmem start block
save 3



