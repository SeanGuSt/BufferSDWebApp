import numpy as np
def getTitrationData(temp):
    fh_in = open(temp, "r")
    x = []
    y = []
    while True:
      temp = fh_in.readline()                   #read line
      if temp == "":                            #check for end of file
          break                                  #if end of file, quit
      if len(temp.strip()) != 0:                #ignore blank lines
         llist =  [int(s) for s in temp.split() if s.isdigit()]  #get integers
         if len(llist) > 0:                     #check length of integer list
            if llist[0] == 0:                   #first item in integer list is zero
               vals = temp.split()              #split original string
               x.append(float(vals[1]))
               y.append(float(vals[3]))
               while True:                         #Now read rest of data table
                  temp = fh_in.readline()       #read next line
                  if len(temp.strip()) == 0:    #check for blank line
                     break                      #if blank, break out of inner loop
                  vals = temp.split()           #otherwise, split original string
                  x.append(float(vals[1]))
                  y.append(float(vals[3]))
    return np.array(x), np.array(y)


