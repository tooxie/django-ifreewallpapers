import time

def time_to_duration(timestamp):
  #~ This function is based on code from xavinsky at 1et0.org
  #~ ztimeout = default number of minutes since user is considered as online
  ztimeout=4
  seconde=1
  minute=seconde*60
  jour=1440*minute
  nbjvisible=300000000
  timegmt=time.time()
  last_action=time.mktime(timestamp.timetuple())
  d=last_action-timegmt
  isoff=False
  if -d/(60*60*24)<nbjvisible:
    if last_action+ztimeout*minute<float(timegmt):
      isoff=True;
    if d>-60:
      ff=str(int(d))+' sec'
    elif d>-60*60:
      ff=str(int(d/(60)))+' min'
    elif d>-60*60*24:
      ff=str(int(d/(60*60)))+' h'
    elif d>-60*60*30*24:
      ff=str(int(d/(60*60*24)))+' jour(s)'
    elif d>-60*60*30*24*12:
      ff=str(int(d/(60*60*24*30)))+' mois'
    else:
      ff=str(int(d/(60*60*24*30*12)))+' année(s)'
    return (ff,isoff) 
  return ()

