import time

def is_dst(t:int):
  year = time.localtime(t)[0] # get current year
  # wd: 0-sunday .. 6-saturday
  wd_end_march   = (time.localtime(time.mktime((year, 3,31,1,0,0,0,0,0)))[6]+1)%7
  wd_end_october = (time.localtime(time.mktime((year,10,31,0,0,0,0,0,0)))[6]+1)%7
  dst_on  = time.mktime((year, 3,31-wd_end_march  ,1,0,0,0,0,0)) # last sunday of March   01h UTC: DST on
  dst_off = time.mktime((year,10,31-wd_end_october,0,0,0,0,0,0)) # last sunday of October 00h UTC: DST off
  # between last sunday of March and last sunday of October
  return t >= dst_on and t < dst_off

# micropython ntp syncs 1 second too late
# maybe t+1 should be used
def localtime(t:int):
  return time.localtime(t+3600*(1+is_dst(t)))
