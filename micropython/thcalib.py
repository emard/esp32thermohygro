# {serial1:array,serial2:array,...}

# calib table as array with even number of elements
# starting from index 0 (even element), each even,odd pair
# of numbers means one calibration point as:
# direct reading in -> log written out
t  = {0:[-40,-40, 105,105],0x12345678:[-40,-40, 105,105]}
rh = {0:[0,0, 100,100],0x12345678:[0,0, 100,100]}
