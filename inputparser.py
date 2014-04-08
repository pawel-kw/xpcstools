# input file parser
import sys
import numpy
import pylab
from ConfigParser import RawConfigParser

class inputparser(object):
    '''PYXPCS and PYXSVS input file parser
    '''
    def __init__(self,inputFileName,**kwargs):
        '''A utility to read and parse the old pyxpcs and the new
        pyxsvs input files.
        '''
        self.config = RawConfigParser()
        self.Parameters = {}
        self.initParameters()
        # Read input file
        self.config.read(inputFileName)
        self.parseInput(self.config)
        self.setParameters(**kwargs) # Overwrite parameters (if any are given)

    def initParameters(self):
        r'''Acts on the :sefl.Parameters: dictionary. Sets initial parameter values.
        '''
        self.Parameters = {
                'oldInputFormat' : False,
                'saveDir' : '',
                'dataDir' : '',
                'flatFieldFile' : '',
                'useFlatField' : True,
                'maskFile' : '',
                'defaultMaskFile' : '',
                'q1' : 0.0,
                'q2' : 0.0,
                'qs' : 0.0,
                'dq' : 0.0,
                'outPrefix' : '',
                'wavelength' : 0.0,
                'cenx' : 0.0,
                'ceny' : 0.0,
                'pixSize' : 0.0,
                'sdDist' : 0.0,
                'dchi' : 5,
                'rmin' : 25,
                'rmax' : 100,
                'mode'  : 'XSVS',
                'exposureList' : '',
                'exposureParams' : {},
                }

    def parseInput(self,config):
        r'''Function reading the input file and setting the
        *self.Parameters* acordingly.
        '''
        # First, recognize if it's the old pyxpcs or the new pyxsvs format
        if config.has_section('Main'):
            self._parseNewInput(config)
        elif config.has_section('Directories'):
            self._parseOldInput(config)

    def _parseNewInput(self,config):
        r'''Function reading the input file and setting the
        :self.Parameters: acordingly.
        '''
        self.Parameters['oldInputFormat'] = False
        self.Parameters['saveDir'] = config.get('Main','save dir')
        self.Parameters['dataDir'] = config.get('Main','data dir')
        self.Parameters['flatFieldFile'] = config.get('Main','flat field')
        try:
            self.Parameters['maskFile'] = config.get('Main','mask')
        except:
            print 'Mask not set in the config file'
        self.Parameters['defaultMaskFile'] = config.get('Main','default mask')
        self.Parameters['q1'] = config.getfloat('Main','q1')
        self.Parameters['q2'] = config.getfloat('Main','q2')
        self.Parameters['qs'] = config.getfloat('Main','qs')
        self.Parameters['dq'] = config.getfloat('Main','dq')
        self.Parameters['outPrefix'] = config.get('Main','sample name')
        self.Parameters['wavelength'] = config.getfloat('Main','wavelength')
        self.Parameters['cenx'] = config.getfloat('Main','cenx')
        self.Parameters['ceny'] = config.getfloat('Main','ceny')
        self.Parameters['pixSize'] = config.getfloat('Main','pix')
        self.Parameters['sdDist'] = config.getfloat('Main','sddist')
        if config.has_option('Main','mode'):
            self.Parameters['mode'] = config.get('Main','mode')
        else:
            self.Parameters['mode'] = 'XSVS' # Assuming default XSVS data mode
        if self.Parameters['mode'] == 'XSVS':
            secList = config.sections()
            secList.remove('Main')
            exposureList = numpy.sort(secList)
            self.Parameters['exposureList'] = exposureList
            for i in xrange(len(exposureList)):
                exposure = exposureList[i]
                currExpParams = {}
                currExpParams['dataSuf'] = config.get(exposure,'data suffix')
                currExpParams['dataPref'] = config.get(exposure,'data prefix')
                currExpParams['n1'] = config.getint(exposure,'first data file')
                currExpParams['n2'] = config.getint(exposure,'last data file')
                currExpParams['expTime'] = config.getfloat(exposure,'exp time')
                self.Parameters['exposureParams'][exposure] = currExpParams
        elif self.Parameters['mode'] == 'XPCS':
            expParams = {}
            self.Parameters['exposureList'] = ['Exp_bins']
            expParams['dataSuf'] = config.get('Exp_bins','data suffix')
            expParams['dataPref'] = config.get('Exp_bins','data prefix')
            expParams['n1'] = config.getint('Exp_bins','first data file')
            expParams['n2'] = config.getint('Exp_bins','last data file')
            expParams['expTime'] = config.getfloat('Exp_bins','exp time')
            expParams['binStart'] = config.getfloat('Exp_bins','bin start')
            expParams['binStop'] = config.getfloat('Exp_bins','bin stop')
            expParams['binStep'] = config.getint('Exp_bins','bin step')
            self.Parameters['exposureParams']['Exp_bins'] = expParams
            # Generate different exposures by binning frames
            #fileBins = range(expParams['binStart'],
            #                 expParams['binStop'],expParams['binStep'])
            fileBins = [int(x) for x in pylab.logspace(expParams['binStart'],
                                                 expParams['binStop'],
                                                 expParams['binStep'])]
            exposureList = range(len(fileBins))
            for ii in xrange(len(fileBins)):
                exposureLabel = 'Exp_%d' % ii
                exposureList[ii] = exposureLabel
                currExpParams = {}
                currExpParams['dataSuf'] = expParams['dataSuf']
                currExpParams['dataPref'] = expParams['dataPref']
                currExpParams['n1'] = expParams['n1']
                currExpParams['n2'] = expParams['n2']
                currExpParams['expTime'] = expParams['expTime'] * fileBins[ii]
                currExpParams['img_to_bin'] = fileBins[ii]
                self.Parameters['exposureParams'][exposureLabel] = currExpParams
            self.Parameters['exposureList'] = exposureList

    def _parseOldInput(self,config):
        r'''Function reading the old pyxpcs input file and setting the
        :self.Parameters: acordingly. The old input file will still need some new fields:
            *default mask* and *flat_field*.
        '''
        self.Parameters['oldInputFormat'] = True
        self.Parameters['saveDir'] = config.get('Directories','save dir')
        self.Parameters['dataDir'] = config.get('Directories','data dir')
        try:
            self.Parameters['flatFieldFile'] = config.get('Directories','flat field')
        except:
            print 'Flat field not set in the config file'
        try:
            self.Parameters['maskFile'] = config.get('Directories','mask')
        except:
            print 'Mask not set in the config file'
        self.Parameters['defaultMaskFile'] = config.get('Directories','default mask')
        self.Parameters['q1'] = config.getfloat('Analysis','q1')
        self.Parameters['q2'] = config.getfloat('Analysis','q2')
        self.Parameters['qs'] = config.getfloat('Analysis','qs')
        self.Parameters['dq'] = config.getfloat('Analysis','dq')
        self.Parameters['outPrefix'] = config.get('Filenames','sample name')
        self.Parameters['wavelength'] = config.getfloat('Beam','wavelength')
        self.Parameters['cenx'] = config.getfloat('Beam','cenx')
        self.Parameters['ceny'] = config.getfloat('Beam','ceny')
        self.Parameters['pixSize'] = config.getfloat('Detector','pix')
        self.Parameters['sdDist'] = config.getfloat('Detector','sddist')
        expParams = {}
        self.Parameters['exposureList'] = ['Exp_bins']
        expParams['dataSuf'] = config.get('Filenames','data suffix')
        expParams['dataPref'] = config.get('Filenames','data prefix')
        expParams['n1'] = config.getint('Filenames','first data file')
        expParams['n2'] = config.getint('Filenames','last data file')
        self.Parameters['exposureParams']['Exp_bins'] = expParams

    def setParameters(self,**kwargs):
        r'''Sets the parameters given in keyword - value pairs to known settings
        keywords. Unknown key - value pairs are skipped.
        '''
        for kw in kwargs:
            if kw in self.Parameters.keys():
                self.Parameters[kw] = kwargs[kw]
            else:
                pass # Ignoring unkwonw settings

