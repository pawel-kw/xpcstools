# Correlation function fitting tools

from pylab import *
from glob import glob
import lmfit
import fabio
import pyFAI
import inputparser
import argparse # parsing command line arguments
import datatojson

def simExp(t,params):
    '''Simple exponential decay. Careful with units!
    '''
    contrast = params['contrast'].value
    baseline = params['baseline'].value
    Gamma = params['Gamma'].value
    res = baseline + contrast * exp(-2 * Gamma * t)
    return res

def KWWmodel(t,params):
    '''Simple exponential decay. Careful with units!
    '''
    contrast = params['contrast'].value
    baseline = params['baseline'].value
    Gamma = params['Gamma'].value
    gamma = params['gamma'].value
    res = baseline + contrast * exp(-2 * (Gamma * t) ** gamma)
    return res

def linearModel(xdata,params):
    a = params['a']
    res = a * xdata
    return res

def errfunc(params,xdata,ydata,yerr,fitfunc):
    res = (fitfunc(xdata,params) - ydata)/yerr
    return res

class xpcsfitter(object):
    '''Main class for fitting XPCS correlation functions
    '''
    def __init__(self,dataFileName,errFileName='none'):
        # Init variables:
        self.q = 0
        self.t_val = 0
        self.cf_array = 0
        self.err_array = 0
        self.fit_params = lmfit.Parameters()
        self.init_fit_params()
        self.fit_results = {}
        # Read data file:
        self.read_data(dataFileName)
        # Read error bars:
        if errFileName != 'none':
            self.read_err_data(errFileName)
        else:
            self.err_array = ones(shape(self.cf_array))

    def read_data(self,dataFileName):
        '''Reads the fit results file and populates the internal
        variables with data
        '''
        raw_data = loadtxt(dataFileName)
        self.t_val = raw_data[1:,0]
        self.q = raw_data[0,1:]
        self.cf_array = raw_data[1:,1:]

    def read_err_data(self,errFileName):
        '''Reads the error bar data file and populates the internal
        variables with data
        '''
        raw_data = loadtxt(errFileName)
        self.err_array = raw_data[1:,1:]

    def init_fit_params(self):
        '''Initializes fit parameters
        '''
        self.fit_params
        self.fit_params.add('contrast',value=0.1,vary=True)
        self.fit_params.add('baseline',value=1.0,vary=True)
        self.fit_params.add('Gamma',value=1.0,vary=True)
        self.fit_params.add('gamma',value=1.0,vary=True)

    def fit_SimExp(self):
        '''Perform simple exponential decay fit to the data
        '''
        FIT_NAME = 'SimExp'
        self.fit_params['gamma'].value = 1.0
        self.fit_params['gamma'].vary = False
        self.init_fit_res(FIT_NAME)
        for i in xrange(len(self.q)):
            ydata = self.cf_array[:,i]
            yerr = self.err_array[:,i]
            xdata = self.t_val
            fit_out = lmfit.minimize(errfunc,self.fit_params,
                                     args=(xdata,ydata,yerr,simExp))
            fit_out.leastsq()
            self.save_fit_res(FIT_NAME,fit_out.params,i)

    def init_fit_res(self,res_name):
        '''Initializes the results container with zeros
        '''
        self.fit_results[res_name] = {}
        curr_res = self.fit_results[res_name]
        curr_res['q'] = {i: self.q[i] for i in range(len(self.q))}
        for key in self.fit_params.keys():
            curr_res[key] = {'data': zeros(len(self.q)),
                             'err': zeros(len(self.q))}

    def save_fit_res(self,res_name,results,qno):
        '''Writes the fit results to the result container
        '''
        curr_res = self.fit_results[res_name]
        for key in results.keys():
            curr_res[key]['data'][qno] = results[key].value
            curr_res[key]['err'][qno] = results[key].stderr

    def fit_KWW(self):
        '''Perform KWW fit of the data
        '''

    def save_to_file(self,filename):
        '''Saves the fit results into a json data file
        '''
        datatojson.savedata(filename,self.fit_results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python XPCS correlation function fitting.')
    parser.add_argument('-d',dest='dataFile', metavar='./cf_data.txt', type=str,
                        help='Correlation function file',required=True)
    parser.add_argument('-e',dest='errorFile', metavar='./err_cf_data.txt', type=str,
                        help='Correlation function error bars file',required=False)
    args = parser.parse_args()
    fitter = xpcsfitter(args.dataFile,args.errorFile)
    fitter.fit_SimExp()
    print(fitter.fit_results['SimExp']['Gamma']['err'])
    fitter.save_to_file('./fit_res.json')

