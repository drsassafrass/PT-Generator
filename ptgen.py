import csv
import re
import fnmatch
import os
import datetime
import shutil

siteid = ""
seqnum = []
STATCODE = "00"
totAmt = [] 
ACT = "00"
TRANTYPE ="00"
pCode = [] 
price = "10000000"
quantity = []
odometer = []
OID = "0"
pump = [] 
tranNum = []
tranDate = []
tranTime = []
fill = "00000000"
id_vehicle = []
id_card = []
part_id ="000"
id_acct = []
vehicle = []
end = "00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000DCF000000000000000000000000"
fileDate = ""

#Formats date in the proper PT file format
def tFormat(time):
    return (time[0:2]+time[3:5])

def dFormat(date):
    fDate = date[8:10] + date[0:2] + date[3:5]
    return fDate


def decimalSplit(number, x, y): #y is decimal true/false
    if x: #quantity value check
        if y: #check if it has a decimal or not
            temp = number.split('.')
            for i in range(5-len(temp[0])):
                temp[0]= "0"+temp[0]
            for i in range(3-len(temp[1])):
                temp[1]= temp[1]+"0"
            quantity.append(temp[0]+temp[1])
        else:
            temp = number
            for i in range(5-len(temp)):
                temp = "0"+temp
            quantity.append(temp + "000")
    else:
        if y:
            temp = number.split('.')
            for i in range(4-len(temp[0])):
                temp[0]= "0"+temp[0]
            if len(temp[1])>2:
                temp[1]= temp[1][0:2]
                for i in range(2-len(temp[1])):
                    temp[1]= temp[1]+"0"
            else:
                for i in range(2-len(temp[1])):
                    temp[1]= temp[1]+"0"
            totAmt.append(temp[0]+temp[1])
        else:
            temp = number
            for i in range(4-len(number)):
                temp = "0"+temp
            totAmt.append(temp+"00")

def decimalCheck(number, x):
    decimalfind = re.compile(r"\d+\.\d+")
    if decimalfind.match(number):
        decimalSplit(number, x, True)
    else:
        decimalSplit(number, x, False)

#Ensures the value that was put into it has the proper amount of zeros
def format(oD, num):
    temp = oD
    for i in range(num-len(oD)):
        temp = "0"+temp
    return temp

#pulls today's date in the format requred of the naming covention
def cday():
    now = datetime.datetime.now()
    day=""
    month=""
    if len(str(now.month))<2:
        month = "0" + str(now.month)
    else:
        month = str(now.month)
    if len(str(now.day))<2:
        day = "0" + str(now.month)
    else:
        day = str(now.day)
    return month + day + str(now.year)[2:4]

def ptGen():
    runCount = 0
    firstRun = True
    raw_id = ""
    rowdata = []
    #Pulls filename from directory where the script lives
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file,'}h*.d1c'):
            filename = file
    with open(filename, newline='') as csvfile:
        
        reader = csv.reader(csvfile, quotechar="\"")
        
        for row in reader:
            rowdata = row
            tranNum.append(rowdata[3][1:8])
            if firstRun: #Pulls all the single use variables into memory from the csv
                raw_id = rowdata[0]
                raw_id = re.sub(r'[a-z_\s-]','', raw_id, flags=re.IGNORECASE)
                firstRun = False
                tranDate = dFormat(rowdata[1])
                for x in range((6-len(raw_id))):
                    raw_id = '0' + raw_id
                siteid = raw_id
            for file in os.listdir('.'):
                if fnmatch.fnmatch(file,'}d*.d1c'):
                    DFile = file
            with open(DFile, newline='') as csvfile: #opening the data file csv
                dreader = csv.reader(csvfile, quotechar="\"")
                dPattern = "[0-9]" + tranNum[runCount] #!TODO
                for drow in dreader:
                    if re.search(dPattern, drow[3]):
                        decimalCheck(drow[10], True) #True = Quantity
                        decimalCheck(drow[48], False)
                        pCode.append(drow[11])
                        tranTime.append(tFormat(drow[2]))
            for file in os.listdir('.'):
                if fnmatch.fnmatch(file,'}v*.d1c'):
                    VFile = file    
            with open(VFile, newline='') as csvfile: #opening the variable csv file
                vreader = csv.reader(csvfile, quotechar="\"") 
                for vrow in vreader:
                    if tranNum[runCount] == vrow[3][1:5]:
                        if vrow[8] == "SEQUENCE#":
                            seqnum.append(vrow[9])
                        elif vrow[8] == "ODOMETER":
                            odometer.append(format(vrow[9],7))
                        elif vrow[8] == "pump":
                            pump.append(format(vrow[9],2))
                        elif vrow[8] == "ID_VEHICLE":
                            id_vehicle.append(format(vrow[9],8))
                        elif vrow[8] == "ID_CARD":
                            id_card.append(format(vrow[9],7))
                        elif vrow[8] == "ID_ACCT":
                            id_acct.append(format(vrow[9],6))
                        elif vrow[8] == "VEHICLE":
                            vehicle.append(format(vrow[9],4))

                        #checks for null values in the variables 
                        if len(odometer) < runCount:
                            odometer.append("0000000")
                        elif len(seqnum)< runCount:
                            seqnum.append("0000")
                        elif len(pump)< runCount:
                            pump.append("00")
                        elif len(id_vehicle)< runCount:
                            id_vehicle.append("00000000")
                        elif len(id_card)< runCount:
                            id_card.append("0000000")
                        elif len(id_acct)< runCount:
                            id_acct.append("000000")
                        elif len(vehicle)< runCount:
                            vehicle.append("0000")
                                     
            runCount+=1
    #creates directories for the sites, pt file dates, and d1c file backups
    if not os.path.exists("%s" % siteid):
        os.makedirs("%s" % siteid)
    os.chdir("%s" % siteid)
    if not os.path.exists("%s" % tranDate):
        os.makedirs("%s" % tranDate)
    os.chdir("%s" % tranDate)
    if not os.path.exists("d1c files"):
        os.makedirs("d1c files")
    ptFileName = cday()
    f= open("pt%s.dat" % ptFileName,"w+")
    #Outputs the data line by line to the .dat file
    for i in range(runCount):
        f.write(siteid+seqnum[i]+STATCODE+totAmt[i]+ACT+TRANTYPE+pCode[i]+price+quantity[i]+odometer[i]+OID+pump[i]+tranNum[i]+tranDate+tranTime[i]+fill+id_vehicle[i]+id_card[i]+part_id+id_acct[i]+vehicle[i]+end+"\n")
    os.chdir("..") 
    os.chdir("..")
    #
    cwd = os.getcwd()
    dest = os.getcwd() + '\\{0}\\{1}\\d1c files\\'.format(siteid,tranDate)
    h = "\\}}h{0}.d1c".format(tranDate)
    d = "\\}}d{0}.d1c".format(tranDate)
    v = "\\}}v{0}.d1c".format(tranDate)
    shutil.move(cwd + h, dest + h)
    shutil.move(cwd + d, dest + d)
    shutil.move(cwd + v, dest + v)

ptGen()