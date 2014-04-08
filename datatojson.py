# A tool to save data organized in a dictionary into a json file.
# Contains also reading function.

from pylab import *
import json
import sys
from lmfit import Parameters

def convarray(data):
    for item in data.keys():
        if type(data[item]) == type(zeros(1)):
            data[item] = data[item].tolist()
        elif type(data[item]) == type({}):
            data[item] = convarray(data[item])
        elif isinstance(data[item],Parameters):
            print 'Hurray!'
    return data

def savedata(filename,data):
    '''Data saving function. Saves the provided dictionary containing
    data to a text file in json format.

    Input parameters:
    filename -- path and file name of the destination file
    data -- data in the form of a dictionary

    Returns:
    res -- operation code:
        0 -- for succesful saving,
        1 -- if the provided data is not a dictionary
        2 -- problems with saving to the provided directory/file
    '''
    if not type(data) == type({}):
        print 'Data need to be presented as a dictionary object!'
        res = 1
        pass
    else:
        # json does not handle numpy.ndarray
        # all arrays must be changed to lists before saving the data
        #for item in data.keys():
        #    if type(data[item]) == type(zeros(1)):
        #        data[item] = data[item].tolist()
        data = convarray(data)
        # Conver data to JSON
        try:
            #jdata = json.dumps(data)
            jdata = json.dumps(data, sort_keys=True, indent=4)
        except TypeError:
            res = 1
            print 'Given data is not JSON serializable!'
            return res
        # Save data to file
        try:
            f = open(filename,'w')
            f.write(jdata)
            f.close()
            res = 0
            return res
        except:
            res = 2
            print 'Problems saving data to %s' % filename
            return res

def loaddata(filename):
    '''Loads data from a json file

    Input parameters:
    filename -- path to data file

    Returns:
    data -- data dictionary from the file,
            None in case of problems with reading the file
    '''
    try:
        f = open(filename,'r')
        data = json.load(f)
        f.close()
        return data
    except:
        print 'Problems reading data file: %s' % filename
        return None



