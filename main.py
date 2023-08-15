#file_path = "RC_SpSel.uasset"
#file_path = ("SCENARIO_CH00.uasset")
file_path = ("ImageText.uasset")

import csv
import os
def bytereplace(bytes_data,new_bytes,pos):
    bytes_data=bytes_data[:pos]+new_bytes+bytes_data[pos+len(new_bytes):]
    return bytes_data

def printbytes(byte_data):
    for byte in byte_data:
        print(f'{byte:02X}',end=" ")
def convertUassetText(filepath):
    stringData=[]
    dataheadersize = 19
    noerror=True
    previousEndCheck=0
    with (open(filepath, "rb") as file):
        bytes_data = file.read()
        """
        title_num=int.from_bytes(bytes_data[8:12], byteorder='little')
        title_position = int.from_bytes(bytes_data[24:28], byteorder='little')
        title_len = int.from_bytes(bytes_data[28:32], byteorder='little')
        chunks_position=int.from_bytes(bytes_data[32:36], byteorder='little')
        chunks_len = int.from_bytes(bytes_data[36:40], byteorder='little')
        chunks2_position = int.from_bytes(bytes_data[40:44], byteorder='little')
        chunks2_len = int.from_bytes(bytes_data[44:48], byteorder='little')
        unk=int.from_bytes(bytes_data[48:52], byteorder='little')
        """
        data_position = int.from_bytes(bytes_data[52:56], byteorder='little')
        data_num=int.from_bytes(bytes_data[data_position+14:data_position+18], byteorder='little')
        """
        pos=title_position
        for i in range(0,title_num+1):
            title_data_len = int.from_bytes(bytes_data[pos:pos+2], byteorder='big')
            pos=pos+2
            title_data=bytes_data[pos:pos+title_data_len]
            title_data=title_data.decode("utf-8")
            pos=pos+title_data_len
            print("data[",i,"][",str(title_data),"]",sep="")
            """
        pos=data_position
        pos=pos+18#for data header skip...
        for i in range(0,data_num):
            header=bytes_data[pos:pos + dataheadersize]
            printbytes(header)
            pos=pos+dataheadersize

            temp = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)
            if temp==0:
                pos=pos+4

            data_len = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=True)
            isUnicode=False

            try:
                #unicode uses negative values...
                if data_len<0:
                    data_len=-data_len;
                    #print("Unicode String!")
                    data_len=data_len*2
                    isUnicode=True
                #data length header skip
                pos=pos+4


                if isUnicode:
                    data = bytes_data[pos:pos + data_len - 2]
                    data = data.decode('utf-16le')
                else:
                    data = bytes_data[pos:pos + data_len - 1]
                    data = data.decode("ascii")
                #add length for next line
                pos = pos + data_len
                #raincode uses 0D 0A to new line...
                data = data.replace('\x0d\x0a', '|')
                print("data[", i, "][", str(data), "]", sep="")
                if len(data)>0:
                    stringData.append(data)
                else:
                    stringData.append("")

                #skip 38 5B 01 00

                temp = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)

                printbytes(bytes_data[pos:pos + 4])
                print()
                if temp<100:
                    pos=pos+temp
                pos=pos+4
            except:
                print('\033[31m'+"data[",i,"]Exception occured!"+'\033[0m',sep="")
                stringData.append("")
                noerror=False
            pass
        #print(bytes_data)
    with open('%s.txt'%os.path.splitext(filepath)[0], 'wb') as file:
        file.write(bytes([0xFF, 0xFE]))
        for i in range(0,len(stringData)):
            outputstr= stringData[i].encode('utf-16le')
            if i == len(stringData)-1:
                file.write(outputstr)
            else:
                file.write(outputstr)
                file.write(bytes([0x0A, 0x00]))
    return noerror

def repackUassetText(file_path):
    stringData = []
    bytes_data=""
    data_header = []
    data_pos_start = []
    data_pos_end = []
    data_end=""
    data_position=0
    data_num=0
    dataheadersize = 19
    previousEndCheck = 0
    with open('%s.txt' % os.path.splitext(file_path)[0], 'r', encoding='utf-16le') as file:
        for item in file:
            item= item.replace("\x0a", "")
            item = item.replace("\ufeff", "")
            stringData.append(item)
    with open(file_path, "rb") as file:
        bytes_data = file.read()
        data_position = int.from_bytes(bytes_data[52:56], byteorder='little')
        data_num = int.from_bytes(bytes_data[data_position + 14:data_position + 18], byteorder='little')
        pos = data_position

        data_header = bytes_data[pos:pos+18]

        if len(stringData) != data_num:
            print("data length is not match,so append a blank one...")
            for i in range(0,data_num-len(stringData)):
                stringData.append("")
                print("append a blank one...")
        pos = pos + 18  # for data header skip...
        for i in range(0, data_num):
            data_for_start=bytes_data[pos:pos + dataheadersize]

            pos = pos + dataheadersize

            temp = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)
            if temp == 0:
                data_for_start = data_for_start + bytes_data[pos:pos + 4]
                pos = pos + 4
            try:
                stringData[i] = stringData[i].replace("|", "\x0D\x0A")
                if len(stringData[i]) == 0:
                    data_for_start = data_for_start
                else:
                    data_for_start = data_for_start + (-(len(stringData[i]) + 1)).to_bytes(4, byteorder='little', signed=True)
            except:
                pass
            data_pos_start.append(data_for_start)

            if len(stringData[i]) == 0:
                data_len =0
            else:
                data_len = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=True)
            isUnicode = False

            # unicode uses negative values...
            if data_len < 0:
                data_len = -data_len
                # print("Unicode String!")
                data_len = data_len * 2
                isUnicode = True
            # data length header skip
            if len(stringData[i]) != 0:
                pos = pos + 4
            """
            if isUnicode:
                data = bytes_data[pos:pos + data_len - 2]
                data = data.decode('utf-16le')
            else:
                data = bytes_data[pos:pos + data_len - 1]
                data = data.decode("ascii")
            """
            # add length for next line
            pos = pos + data_len
            # raincode uses 0D 0A to new line...
            #data = data.replace('\x0d\x0a', '|')
            #print("data[", i, "][", str(data), "]", sep="")
            #stringData.append(data)
            # skip 38 5B 01 00

            temp = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)

            #printbytes(bytes_data[pos:pos + 4])
            #print()

            if temp < 100:
                data_pos_end.append(bytes_data[pos:pos + 4 + temp])
                pos = pos + temp
            else:
                data_pos_end.append(bytes_data[pos:pos + 4])
            pos = pos + 4
            if i>=data_num-1:
                #check all data is go there...
                if pos!=len(bytes_data):
                    print("size not match,so add on last one...")
                    data_end=bytes_data[pos:]
                pass
            pass
        # print(bytes_data)
    string_in_bytes = len(data_header)
    for i in range(0,data_num):
        string_in_bytes+=len(data_pos_start[i])
        data_for_string = stringData[i].encode("utf-16")
        data_for_string = data_for_string[2:]
        string_in_bytes +=len(data_for_string)
        if len(stringData[i]) != 0:
            string_in_bytes+=2
        string_in_bytes +=len(data_pos_end[i])
    string_in_bytes = string_in_bytes-4
    data_size_head = int.from_bytes(bytes_data[44:48], byteorder='little')
    #data_size_header = int.from_bytes(bytes_data[data_size_head+8:data_size_head+12], byteorder='little')

    string_in_bytes = string_in_bytes + len(data_end)
    #i don't know why I should I put this here...
    #string_in_bytes = string_in_bytes + 8

    data_size_head=data_size_head
    bytes_data=bytereplace(bytes_data,string_in_bytes.to_bytes(4, byteorder='little'),(data_size_head+8))

    with open('out/%s.uasset' % os.path.splitext(file_path)[0], 'wb') as file:

        file.write(bytes_data[0:data_position])
        file.write(data_header)
        for i in range(0, data_num):
            file.write(data_pos_start[i])
            data_for_string = stringData[i].encode("utf-16")
            data_for_string=data_for_string[2:]
            file.write(data_for_string)
            if len(stringData[i])!=0:
                file.write(b'\x00')
                file.write(b'\x00')
            file.write(data_pos_end[i])
        if len(data_end)>0:
            file.write(data_end)

    pass
def walkinsizefolder(folder_path):
    fileCount=0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.uasset'):
                file_path = os.path.join(root, file)
                if convertUassetText(file_path) == False:
                    print('\033[31m' + "Exception occured in file[" + file + "] export!!" + '\033[0m', sep="")
                fileCount+=1
    print("files=",fileCount)

def csvFileList(csvfile):
    with open(csvfile, 'r', newline='', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            #print(row[0],row[1],row[2])
            filelocation=row[0]+"/"+row[1]
            print(filelocation)
            if row[2] == "0":
                if convertUassetText(filelocation) == False:
                    print('\033[31m' + "Exception occured in file["+row[1]+"] export!!" + '\033[0m', sep="")
#csvFileList("filelist.csv")
#convertUassetText2(file_path)
convertUassetText(file_path)
#repackUassetText(file_path)

#walkinsizefolder("TextsJP")

