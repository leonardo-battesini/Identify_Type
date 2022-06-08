from datetime import datetime
import numpy as np
import re
import logging


def isNumberFlo(n):
    try:
        float(n)
    except ValueError:
        return False
    return True

def convertStrToStrNumber(text):
    text = str(text)
    text = re.sub('[^0-9]', '', text)
    return str(text)

def convertColumn(type, column):
    if type == 'digit':
        column = column.fillna(0)
        column = column.convert_dtypes(convert_integer=True)
    elif type == 'flo':
        column = column.fillna(0)
        column = column.convert_dtypes(convert_floating=True)
    elif type == 'nul':
        logging.warning('Column with all values NULL: ' + column.name)
        column = column.fillna('')
        column = column.convert_dtypes(convert_string=True)
    elif type == 'empt':
        logging.warning('Column with all values EMPTY: ' + column.name)
        column = column.fillna('')
        column = column.convert_dtypes(convert_string=True)
    elif type == 'date':
        column = column.convert_dtypes(convert_string=True)
        column = column.fillna(np.nan)
    elif type == 'txt':
        column = column.fillna('')
        column = column.convert_dtypes(convert_string=True)
    return column

def trataColumn(column):
    data_types = {}

    for value in column:
        if str(value) == 'nan':                        #if null
            if 'nul' not in data_types.keys():
                data_types['nul'] = 1
            else:
                data_types['nul'] += 1
                
        elif str(value).replace(" ", "").isdigit():    #if digit
            if 'digit' not in data_types.keys():
                data_types['digit'] = 1
            else:
                data_types['digit'] += 1
            
        elif isNumberFlo(str(value).replace(" ", "")): #if float
            if 'flo' not in data_types.keys():
                data_types['flo'] = 1
            else:
                data_types['flo'] += 1
                
        elif len(value.replace(" ", "")) == 0:         #if empty
            if 'empt' not in data_types.keys():
                data_types['empt'] = 1
            else:
                data_types['empt'] += 1

        elif isDate(str(value)):                       #if date
            if 'date' not in data_types.keys():
                data_types['date'] = 1
            else:
                data_types['date'] += 1
                
        else:                                          #if not treated
            if 'txt' not in data_types.keys():
                data_types['txt'] = 1
            else:
                data_types['txt'] += 1

    max_type = max(data_types, key=data_types.get)

    if len(data_types) == 1:
        return(convertColumn(max_type, column))
    else:
        try:
            del data_types['nul']
        except:
            try:
                del data_types['empt']
            except:
                1==2
        
        if len(data_types) >= 2:
            try:
                del data_types['empt']
            except:
                1==2
        
        if len(data_types) == 1:
            return(convertColumn(max_type, column))

        ### ALERTA
        if (sum(data_types.values())/10*8 > data_types[max_type]):  # total do max_type < 80% do total 
            logging.warning('DIFFERENCE OF PERCENTAGE OF DATA TYPES IN THIS COLUMN IS BIGGER THEN 80%: ' + column.name)
        
        if max_type == 'txt':
            return(convertColumn(max_type, column))

        if max_type == 'flo' or (len(data_types) == 2 and 'flo' in data_types.keys() and 'digit' in data_types.keys()):
            for i in range(column.size):
                if not isNumberFlo(column[i]):
                    column[i] = convertStrToStrNumber(column[i])
            return(convertColumn(max_type, column))

        if max_type == 'digit':
            for i in range(column.size):
                if not str(column[i]).replace(" ", "").isdigit():
                    column[i] = column[i].replace(" ", "")
                    column[i] = convertStrToStrNumber(column[i])

            return(convertColumn(max_type, column))

        if max_type == 'date':
            for i in range(column.size):
                if not isDate(column[i]):
                    logging.warning('Data value replaced with NaN: ' + str(column[i]))
                    column[i] = np.nan

            return(convertColumn(max_type, column))
        
        logging.warning('CASE NOT TREATED, PLEASE VERIFY!! ', data_types, column.iloc[:10])
        return(convertColumn(max_type, column))

def isDate(value):
    try: ### 22/05/2003
        date = datetime.strptime(value, '%d/%m/%Y').date()
        return(1)
    except:
        try: ### 22-05-2003
            date = datetime.strptime(value, '%d-%m-%Y').date()
            return(2)
        except:
            try: ### 2003-05-22
                date = datetime.strptime(value, '%Y-%m-%d').date()
                return(3)
            except:
                try: ### 2003/05/22
                    date = datetime.strptime(value, '%Y/%m/%d').date()
                    return(4)
                except:
                    try: ### 22/05/2003 12:42
                        date = datetime.strptime(value, '%d/%m/%Y %H:%M').date()
                        return(5)
                    except:
                        try: ### 2003/05/22 12:42
                            date = datetime.strptime(value, '%Y/%m/%d %H:%M').date()
                            return(6)
                        except:
                            try: ### 22-05-2003 12:42
                                date = datetime.strptime(value, '%d-%m-%Y %H:%M').date()
                                return(7)
                            except:
                                try: ### 2003-05-22 12:42
                                    date = datetime.strptime(value, '%Y-%m-%d %H:%M').date()
                                    return(8)
                                except:
                                    try: ### 22/05/2003 12:42:59
                                        date = datetime.strptime(value, '%d/%m/%Y %H:%M:%S').date()
                                        return(9)
                                    except:
                                        return(isDate2(value))

def isDate2(value):
    try: ### 2003/05/22 12:42:59
        date = datetime.strptime(value, '%Y/%m/%d %H:%M:%S').date()
        return(10)
    except:
        try: ### 22-05-2003 12:42:59
            date = datetime.strptime(value, '%d-%m-%Y %H:%M:%S').date()
            return(11)
        except:
            try: ### 2003-05-22 12:42:59
                date = datetime.strptime(value, '%Y-%m-%d %H:%M:%S').date()
                return(12)
            except:
                return(0)

def trataDf(df):
    columns = list(df.columns)

    for column in columns:
        df[column] = trataColumn(df[column])
    return df
