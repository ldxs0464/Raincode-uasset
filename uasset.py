import openpyxl
import os
def bytereplace(bytes_data,new_bytes,pos):
    bytes_data=bytes_data[:pos]+new_bytes+bytes_data[pos+len(new_bytes):]
    return bytes_data

def printbytes(byte_data):
    for byte in byte_data:
        print(f'{byte:02X}',end=" ")

def tobytes(byte_data):
    data=""
    for byte in byte_data:
        data=data+format(byte,'02X')
    return data

def getfileName(input_string):
    if len(input_string)>0:
        last_slash_index = input_string.rfind('/')
        extracted_string = input_string[last_slash_index + 1:]
        return extracted_string
    else:
        return input_string
def repackUassetText(filepath):
    stringData=[]
    data_header = []
    data_pos_start = []
    data_pos_end = []
    dataheadersize = 19
    endSize = 4

    #import mods
    exportInTxt=True
    exportInExcel=False
    convertLineFeed=True

    with open('%s.txt' % os.path.splitext(filepath)[0], 'r', encoding='utf-16le') as file:
        for item in file:
            item= item.replace("\x0a", "")
            item = item.replace("\ufeff", "")
            item = item.replace("|", "\x0D\x0A")
            stringData.append(item)

    with (open(filepath, "rb") as file):
        bytes_data = file.read()
        #go to data position...
        data_position = int.from_bytes(bytes_data[52:56], byteorder='little')
        #data count(how many files)
        data_num=int.from_bytes(bytes_data[data_position+14:data_position+18], byteorder='little')
        pos=data_position

        if len(stringData) != data_num:
            print("data length is not match,so append a blank one...")
            for i in range(0,data_num-len(stringData)):
                stringData.append("")
                print("append a blank one...")

        data_header = bytes_data[pos:pos+18]
        #sheet['A1']=tobytes(bytes_data[pos:pos+18])

        # for data header skip...
        pos=pos+18
        for i in range(0,data_num):
            print(i,"/",data_num-1,end=" : ")

            header=bytes_data[pos:pos + dataheadersize]
            printbytes(header)
            data_pos_start.append(bytes_data[pos:pos + dataheadersize])
            pos=pos+dataheadersize

            #sheetpos = "A" + str(i + 2)
            #sheet[sheetpos] = getfileName(filepath)

            #sheetpos = "B" + str(i + 2)
            #sheet[sheetpos] = str(i)

            #sheetpos="C"+str(i+2)
            #sheet[sheetpos]= tobytes(header)
            #if saveInAction:
            #    workbook.save('%s.xlsx' % os.path.splitext(filepath)[0])

            data_len = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=True)
            isUnicode=False

            if data_len<10000:
                #unicode uses negative values...
                if data_len<0:
                    data_len=-data_len;
                    #print("Unicode String!")
                    data_len=data_len*2
                    isUnicode=True
                #data length header skip
                pos=pos+4


                #add length for next line
                pos = pos + data_len
            else:
                pass



            #skip 38 5B 01 00
            #calculate length...
            endbyte = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)
            if endbyte < 100:
                endbyte = endbyte + 4 +endSize
            else:
                endbyte=endSize

            # position editing...

            unk1 = int(header[10])
            match unk1:
                case 0x1c:
                    endbyte=0
                case 0x18:
                    endbyte=endbyte-4
                case 0x1A:
                    endbyte=0
                    pass

            pass

            #sheetpos = "E" + str(i + 2)
            #sheet[sheetpos]= tobytes(bytes_data[pos:pos + endbyte])
            data_pos_end.append(bytes_data[pos:pos + endbyte])

            pos=pos+endbyte
            pass

            print()
        #print(bytes_data)
    string_in_bytes = len(data_header)
    for i in range(0,data_num):
        string_in_bytes+=len(data_pos_start[i])
        data_for_string = stringData[i].encode("utf-16")
        data_for_string = data_for_string[2:]
        string_in_bytes +=len(data_for_string)
        if len(stringData[i]) != 0:
            string_in_bytes+=6
        string_in_bytes +=len(data_pos_end[i])
    data_size_head = int.from_bytes(bytes_data[44:48], byteorder='little')
    string_in_bytes=string_in_bytes-4
    bytes_data = bytereplace(bytes_data, string_in_bytes.to_bytes(4, byteorder='little'), (data_size_head + 8))

    with open('%s.uasset' % os.path.splitext(filepath)[0], 'wb') as file:

        file.write(bytes_data[0:data_position])
        file.write(data_header[0:len(data_header)])
        for i in range(0, data_num):
            file.write(data_pos_start[i])
            data_for_string = stringData[i].encode("utf-16")
            data_for_string = data_for_string[2:]

            if len(stringData[i]) > 0:
                file.write((-(len(stringData[i]) + 1)).to_bytes(4, byteorder='little', signed=True))
            file.write(data_for_string)
            if len(stringData[i]) != 0:
                file.write(b'\x00')
                file.write(b'\x00')
            file.write(data_pos_end[i])

    pass
def convertUassetText(filepath):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    stringData=[]
    dataheadersize = 19
    endSize = 4

    #export mods
    saveInAction=False
    exportInTxt=True
    exportInExcel=False
    convertLineFeed=True
    with (open(filepath, "rb") as file):
        bytes_data = file.read()
        #go to data position...
        data_position = int.from_bytes(bytes_data[52:56], byteorder='little')
        #data count(how many files)
        data_num=int.from_bytes(bytes_data[data_position+14:data_position+18], byteorder='little')
        pos=data_position

        sheet['A1']=tobytes(bytes_data[pos:pos+18])

        # for data header skip...
        pos=pos+18
        for i in range(0,data_num):
            print(i,"/",data_num-1,end=" : ")

            header=bytes_data[pos:pos + dataheadersize]
            printbytes(header)

            pos=pos+dataheadersize

            sheetpos = "A" + str(i + 2)
            sheet[sheetpos] = getfileName(filepath)

            sheetpos = "B" + str(i + 2)
            sheet[sheetpos] = str(i)

            sheetpos="C"+str(i+2)
            sheet[sheetpos]= tobytes(header)
            if saveInAction:
                workbook.save('%s.xlsx' % os.path.splitext(filepath)[0])

            data_len = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=True)
            isUnicode=False

            if data_len<10000:
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

                if convertLineFeed:
                    data = data.replace('\x0d\x0a', '|')
                stringData.append(data)
                sheetpos = "D" + str(i + 2)
                sheet[sheetpos] = data

                if saveInAction:
                    workbook.save('%s.xlsx' % os.path.splitext(filepath)[0])

                #add length for next line
                pos = pos + data_len
            else:
                pass



            #skip 38 5B 01 00
            #calculate length...
            endbyte = int.from_bytes(bytes_data[pos:pos + 4], byteorder='little', signed=False)
            if endbyte < 100:
                endbyte = endbyte + 4 +endSize
            else:
                endbyte=endSize

            # position editing...

            unk1 = int(header[10])
            match unk1:
                case 0x1c:
                    endbyte=0
                case 0x18:
                    endbyte=endbyte-4
                case 0x1A:
                    endbyte=0
                    pass

            pass

            sheetpos = "E" + str(i + 2)
            sheet[sheetpos]= tobytes(bytes_data[pos:pos + endbyte])
            if saveInAction:
                workbook.save('%s.xlsx' % os.path.splitext(filepath)[0])


            pos=pos+endbyte
            pass

            print()
        #print(bytes_data)
    if pos != len(bytes_data):
        print("Length is not matched(Check the code!)")
        input()
    if not saveInAction:
        if exportInExcel:
            workbook.save('%s.xlsx' % os.path.splitext(filepath)[0])
    if exportInTxt:
        with open('%s.txt'%os.path.splitext(filepath)[0], 'w',encoding='utf-16le') as file:
            file.write('\ufeff')
            for i in range(0,len(stringData)):
                if i == len(stringData)-1:
                    file.write(stringData[i])
                else:
                    file.write(stringData[i]+'\n')
#convertUassetText("RCSFL.uasset")
def extractinsizefolder(folder_path):
    fileCount=0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.uasset'):
                file_path = os.path.join(root, file)
                print(file)
                convertUassetText(file_path)
                fileCount+=1
    print("files=",fileCount)

def importinsizefolder(folder_path):
    fileCount=0
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.uasset'):
                file_path = os.path.join(root, file)
                print(file)
                repackUassetText(file_path)
                fileCount+=1
    print("files=",fileCount)
#extractinsizefolder("Texts")
#convertUassetText("RCSpeakerList.uasset")
importinsizefolder("Texts")
#repackUassetText("RCInvestigationName.uasset")