# -*- coding: utf-8 -*-
"""
@author: Sindre Vatnehol
@institute: Insitute of Marine Research, Bergen - Norway
@emai: sindre.vatnehol@hi.no
"""

#Requiered fcuntions
import requests
import xml.etree.ElementTree as ET
import numpy as np
import xmltodict
import pandas as pd
from xml.dom import minidom
import dateutil.parser as parser
import os
from echolab2.instruments import EK80, EK60


class define_metadata_structure (object):
    """
    Defining an empty metadata structure for further usage.
    
    The empty structured can then be filled inn by the user, or to use functions
    
    The structure follows the metadata definition of the ICES acoustic format, 
    with addition of some metadata requiered to be added in LSSS software
    """
    def __init__(self): 
        
        
        #Instrument list including the information of transceiver and transducer 
        self.Instrument = pd.DataFrame(data={'Frequency': [None],
                                                  'TransducerLocation':[None],
                                                  'TransducerManufacturer':[None],
                                                  'TransducerModel':[None],
                                                  'TransducerSerial':[None],
                                                  'TransducerBeamType':[None],
                                                  'TransducerDepth':[None],
                                                  'TransducerOrientation':[None],
                                                  'TransducerPSI':[None],
                                                  'TransducerBeamAngleMajor':[None],
                                                  'TransducerBeamAngleMinor':[None],
                                                  'TransceiverManufacturer':[None],
                                                  'TransceiverModel':[None],
                                                  'TransceiverSerial':[None],
                                                  'TransceiverFirmware':[None],
                                                  })

        
        #Calibration list - metadatainformation about the calibration
        self.Calibration = pd.DataFrame(data={'Date':[None],
                                                   'AcquisitionMethod':[None],
                                                   'ProcessingMethod':[None],
                                                   'AccuracyEstimate':[None],
                                                   })


        
        #DataAcquisition list - metadata about the software used to collect the data. I.eks. Simrad EK80 software
        self.DataAcquisition = pd.DataFrame(data={'SoftwareName':[None],
                                                   'SoftwareVersion':[None],
                                                   'StoredDataFormat':[None],
                                                   'PingDutyCycle':[None],
                                                   })

        
        
        #DataProcessing list - information aboutthe dataprocessing. 
        self.DataProcessing = pd.DataFrame(data={'SoftwareName': [None],
                                                  'SoftwareVersion':[None],
                                                  'TriwaveCorrection':[None],
                                                  'ChannelID':[None],
                                                  'Bandwidth':[None],
                                                  'Frequency':[None],
                                                  'TransceiverPower':[None],
                                                  'OnAxisGain':[None],
                                                  'OnAxisGainUnit':[None],
                                                  'SaCorrection':[None],
                                                  'Absorption':[None],
                                                  'AbsorptionDescription':[None],
                                                  'SoundSpeed':[None],
                                                  'SoundSpeedDescription':[None],
                                                  'TransducerPSI':[None],
                                                  })
    
        
        #Cruise list
        self.Cruise = pd.DataFrame(data={'Survey': [None],
                                          'Country':[None],
                                          'PlatformName':[None],
                                          'Platform':[None],
                                          'PlatformNumber': [None],
                                          'Nation':[None],
                                          'NationCode':[None],
                                          'StartDate':[None],
                                          'EndDate':[None],
                                          'Organisation':[None],
                                          'LocalID':[None]
                                          })
    

        self.AcousticCategory = pd.DataFrame(data={'LSSSacousticCategory': [None],
                                          'commonName':[None],
                                          'pgnapescode':[None],
                                          'icesCode':[None]
                                          })
    
                
    
    
        
class IMR_metadata_fill_in_Cruise(object):
    """
    Fill inn IMR metadata for the cruise table. 
    
    This requieres connection the IMR reference API (only avaliable within IMR)
    
    input: 
            - localCruiseID : the cruiseID of the local server
            - platform:  name of the vessel
            - ICESsurvey: The ICES vocabulary of that particular survey
            
    #TODO: 
        1. The IMR reference should also have the ICESsurvey code within the reference table
    """
    
    def __init__(self,localCruiseID = 2021818,ICESsurvey=None):
        
        #Search for vessel name when given a cruiseCode
        cruise = requests.get("http://tomcat7.imr.no:8080/apis/nmdapi/cruise/v2?type=ListAll")
        tmp = xmltodict.parse(cruise.text)
        grabPlatform=False
        for element in tmp['list']['row']: 
            for el in element['element']: 
                if el['@name'] == 'delivery': 
                    if el['#text'] == str(localCruiseID):
                          grabPlatform=True
                if grabPlatform==True: 
                    if el['@name'] == 'shipname': 
                        platform=el['#text']
                        break
            if grabPlatform==True: 
                break
        
        #Grab information regarding the survey
        cruise = requests.get("http://tomcat7.imr.no:8080/apis/nmdapi/cruise/v2?type=findByCruise&shipname="+platform+"&cruisenr="+str(localCruiseID))
        tmp = xmltodict.parse(cruise.text)
        for element in tmp['list']['row']['element']: 
            name = (element['@name'])
            text = (element['#text'])
            if name == 'starttime': 
                starttime = text
            elif name == 'stoptime': 
                stoptime = text
            elif name == 'callsignal': 
                callsignal = text
                
        
        plat = requests.get("http://tomcat7.imr.no:8080/apis/nmdapi/reference/v2/dataset/platform?version=2.0")
        tmp2 = xmltodict.parse(plat.text)
        for element in tmp2['list']['row']: 
            if 'platformCodes' in list(element):
                if type(element['platformCodes']['platformCode'])==list: 
                    for el in element['platformCodes']['platformCode']: 
                        if el['sysname'] == 'Ship name': 
                            if el['value']== platform: 
                                platformNumber = element['platformNumber']
                                nationCode = element['nationCode']
                                nation = element['nation']
                                break
                else: 
                    el = element['platformCodes']['platformCode']
                    if el['sysname'] == 'Ship name': 
                        if el['value']== platform: 
                            platformNumber = element['platformNumber']
                            nationCode = element['nationCode']
                            nation = element['nation']
                            break
        
        #Prepare and output a pandas dataframe
        self.df = pd.DataFrame(data={'Survey': [ICESsurvey],
                          'Country':['NO'],
                          'PlatformName':[platform],
                          'Platform':[callsignal],
                          'PlatformNumber': platformNumber,
                          'Nation':[nation],
                          'NationCode':[nationCode],
                          'StartDate':[parser.parse(starttime).date().isoformat()],
                          'EndDate':[parser.parse(stoptime).date().isoformat()],
                          'Organisation':[612],
                          'LocalID':[localCruiseID]
                          })

    
    
    
        
class IMR_metadata_fill_in_Calibration(object):
    """
    Fill inn IMR standard metadata for the calibration table. 
    
    
    input: 
            - Date : the calibration Date
            - platform:  name of the vessel
            - ICESsurvey: The ICES vocabulary of that particular survey
            
    """
    
    def __init__(self,Date = '',accuracy = '0.06'):
        
        self.df = pd.DataFrame(data={'Date':[Date],
                                       'AcquisitionMethod':['SS'],
                                       'ProcessingMethod':['calibration.exe'],
                                       'AccuracyEstimate':[accuracy],
                                       })
    
        
    


class IMR_metadat_fill_in_AcousticCategory (object):
    """
    Fill in IMR metadata for acoustic category. 
    
    This requiere connection within the IMR firewall. 
    
    It outputs the connections between LSSS acoustic category vocabular, 
    with other databases vocabular such as PGNAPES and ICES DB. 
    
    TODO: 
        ICES filed must be added to the reference table
    
    """
    
    
    def __init__(self): 

        
        speciesCat = requests.get("http://tomcat7.imr.no:8080/apis/nmdapi/reference/v2/model/acousticCategory?version=2.0")
        tmp = xmltodict.parse(speciesCat.text)
        

        self.AcousticCategory = pd.DataFrame(data={'LSSSacousticCategory': [None],
                                          'commonName':[None],
                                          'pgnapescode':[None],
                                          'icesCode':[None]
                                          })
    
                
        for element in tmp['list']['row']: 
            if  'icescode' in element:
                aco = pd.DataFrame(data={'LSSSacousticCategory': [element['acousticCategory']],
                                              'commonName':[element['commonName']],
                                              'pgnapescode':[element['pgnapescode']],
                                              'icesCode':[element['icescode']]
                                              })
            else: 
                aco = pd.DataFrame(data={'LSSSacousticCategory': [element['acousticCategory']],
                                              'commonName':[element['commonName']],
                                              'pgnapescode':[element['pgnapescode']],
                                              'icesCode':[None]
                                              })
                
            self.AcousticCategory=self.AcousticCategory.append(aco)
        self.AcousticCategory=self.AcousticCategory[1:]
            
            
        
        
        
        
            
        
        
 
class make_LSSS_ICES_Acoustic_Category (object):
    """
    function to prepare the linkage between IMR AND ICES species category
    
    """
    def __init__(self,file_location='',AcousticCategory=None): 
        
        data = ET.Element('ices-acoustic-category')
        for row in AcousticCategory.iterrows():
            aco = ET.SubElement(data, 'i')
            aco.set('acousticCategory',str(row[1].LSSSacousticCategory))
            aco.set('ices',row[1].icesCode)
        
        mydata = minidom.parseString(ET.tostring(data)).toprettyxml(indent="   ")
        myfile = open(file_location+'IcesAcousticCategory.xml', "w")
        myfile.write(str(mydata))
        myfile.close()
        
 
    
    


# Detect FileType
def ek_detect(fname):
    with open(fname, 'rb') as f:
        file_header = f.read(8)
        file_magic = file_header[-4:]
        if file_magic.startswith(b'XML'):
            return "EK80"
        elif file_magic.startswith(b'CON'):
            return "EK60"
        else:
            return None

def ek_read(fname):
    ftype = ek_detect(fname)
    if ftype == "EK80":
        ek80_obj = EK80.EK80()
        ek80_obj.read_raw(fname)
        return ek80_obj
    elif ftype == "EK60":
        ek60_obj = EK60.EK60()
        ek60_obj.read_raw(fname)
        return ek60_obj





        
 
class RAW_metadat_fill_in_Tables (object):
    """
    function to read metadata information from RAW files. 
    
    TODO: Test if it also works on EK60
    
    """
    def __init__(self,path=''): 
        
        #Scan the last files (first files often don't have all channel data during calibration)
        for file in os.listdir(path)[-5:-1]: 
            file_name = os.path.join(path,file)
            filename_, file_extension = os.path.splitext(file_name)
            if file_extension == '.raw': 
                break
            
        #Read echosounder data
        fid = ek_read(file_name)
            
        
        
        # Get all channels
        all_channels = list(fid.raw_data)
        
        #Placeholder
        Frequency = []
        Transducer_location=[]
        Transducer_model=[]
        Transducer_serial=[]
        Transducer_BeamType=[]
        TransducerDepth=[]
        Transducer_orientation=[]
        Transducer_PSI=[]
        Transducer_BeamAngle_ATW=[]
        Transducer_BeamAngle_ALO=[]
        Transceiver_Model=[]
        Transceiver_serial=[]
        Transceiver_firmvare=[]
        ChannelID=[]
        Transceiver_power=[]
        Transmit_PulseLength=[]
        OnAxisGain=[]
        OnAxisGainUnit=[]
        SaCorrection=[]
        
        
        #Loop through eachchannel
        for chan in all_channels:
            
            #Get data
            raw_data = fid.raw_data[chan][0]
        
            #Get configuration data
            tmp = raw_data.configuration
            
            #Get info of the software
            xml = xmltodict.parse(tmp[0]['raw_xml'])
            SoftwareName = xml['Configuration']['Header']['@ApplicationName']
            SoftwareVersion = xml['Configuration']['Header']['@Version']
            
            #get the rest of teh info
            for key, value in  tmp[0].items(): 
                if key == 'transducer_frequency':
                    Frequency.append(value)
                elif key == 'transducer_mounting': 
                    Transducer_location.append(value)
                elif key == 'transducer_name': 
                    Transducer_model.append(value)
                elif key == 'transducer_serial_number': 
                    Transducer_serial.append(value)
                elif key == 'transducer_beam_type': 
                    Transducer_BeamType.append(value)
                elif key == 'transducer_offset_z': 
                    TransducerDepth.append(value)
                elif key == 'transducer_orientation': 
                    Transducer_orientation.append(value)
                elif key == 'equivalent_beam_angle':
                    Transducer_PSI.append(value)
                elif key == 'beam_width_athwartship': 
                    Transducer_BeamAngle_ATW.append(value)
                elif key == 'beam_width_alongship': 
                    Transducer_BeamAngle_ALO.append(value)
                elif key == 'transceiver_type': 
                    Transceiver_Model.append(value)
                elif key == 'serial_number': 
                    Transceiver_serial.append(value)
                elif key == 'transceiver_software_version': 
                    Transceiver_firmvare.append(value)
                elif key == 'transceiver_name': 
                    ChannelID.append(value)
                elif key == 'max_tx_power_transducer': 
                    Transceiver_power.append(value)
                elif key == 'pulse_duration': 
                    Transmit_PulseLength.append(value[1])
                elif key == 'gain': 
                    OnAxisGain.append(value[1])
                    OnAxisGainUnit.append('dB')
                elif key == 'sa_correction':
                    SaCorrection.append(value[1])
        
        
        
        #Output teh DataAcquisition table
        self.DataAcquisition = pd.DataFrame(data={'SoftwareName':[SoftwareName],
                                                       'SoftwareVersion':[SoftwareVersion],
                                                       'StoredDataFormat':['.raw'],
                                                       'PingDutyCycle':['Varying'],
                                                       })
        
        
        #Instrument list
        self.Instrument = pd.DataFrame(data={'Frequency': Frequency,
                                  'TransducerLocation':Transducer_location,
                                  'TransducerManufacturer':['Simrad']*len(Frequency),
                                  'TransducerModel':Transducer_model,
                                  'TransducerSerial':Transducer_serial,
                                  'TransducerBeamType':Transducer_BeamType,
                                  'TransducerDepth':TransducerDepth,
                                  'TransducerOrientation':Transducer_orientation,
                                  'TransducerPSI':Transducer_PSI,
                                  'TransducerBeamAngleMajor':np.maximum(Transducer_BeamAngle_ATW,Transducer_BeamAngle_ALO),
                                  'TransducerBeamAngleMinor':np.minimum(Transducer_BeamAngle_ATW,Transducer_BeamAngle_ALO),
                                  'TransceiverManufacturer':['Simrad']*len(Frequency),
                                  'TransceiverModel':Transceiver_Model,
                                  'TransceiverSerial':Transceiver_serial,
                                  'TransceiverFirmware':Transceiver_firmvare,
                                  
                                  })
        
        
        
        #DataProcessing list
        self.DataProcessing = pd.DataFrame(data={'SoftwareName': [None]*len(ChannelID),
                                                  'SoftwareVersion':[None]*len(ChannelID),
                                                  'TriwaveCorrection':[None]*len(ChannelID),
                                                  'ChannelID':ChannelID,
                                                  'Bandwidth':[None]*len(ChannelID),
                                                  'Frequency':Frequency,
                                                  'TransceiverPower':Transceiver_power,
                                                  'OnAxisGain':OnAxisGain,
                                                  'OnAxisGainUnit':OnAxisGainUnit,
                                                  'SaCorrection':SaCorrection,
                                                  'Absorption':[None]*len(ChannelID),
                                                  'AbsorptionDescription':[None]*len(ChannelID),
                                                  'SoundSpeed':[None]*len(ChannelID),
                                                  'SoundSpeedDescription':[None]*len(ChannelID),
                                                  'TransducerPSI':Transducer_PSI,
                                                  })
                    
                    
class LSSS_config_maker (object):
    """
    function to read metadata information from RAW files. 
    
    TODO: Test if it also works on EK60
    
    """
    def __init__(self,metadata,lsss_filename = [],DataDir = '',ReportDir = '',WorkDir=''): 
        #Start the XML document
        data = ET.Element('survey')
        data.set('version','2')
        
        #configuration field
        configuration = ET.SubElement(data,'configuration')
        SurveyConfiguration= ET.SubElement(configuration,'unit')
        SurveyConfiguration.set('name','SurveyConfiguration')
        SurveyConfiguration.set('version','3')
        configuration= ET.SubElement(SurveyConfiguration,'configuration')
        parameters= ET.SubElement(configuration,'parameters')
        
        
        
        #Survey Configuration
        SurveyConf= ET.SubElement(SurveyConfiguration,'unit')
        SurveyConf.set('name','SurveyConf')
        SurveyConf= ET.SubElement(SurveyConf,'configuration')
        parameters= ET.SubElement(SurveyConf,'parameters')
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','UseLocalDatabase')
        parameter.text = 'false'
        
                
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','Nation')
        parameter.text = metadata.Cruise.Nation[0]
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','PlatformId')
        parameter.text = metadata.Cruise.PlatformNumber[0]
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','Platform')
        parameter.text = metadata.Cruise.PlatformName[0]
                
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SurveyId')
        parameter.text = str(metadata.Cruise.LocalID[0])
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','Survey')
        parameter.text = str(metadata.Cruise.LocalID[0])
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','StartDate')
        parameter.text = metadata.Cruise.StartDate[0]
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','StartTime')
        parameter.text = '00:00'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','StopDate')
        parameter.text = metadata.Cruise.EndDate[0]
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','StopTime')
        parameter.text = '23:59'
                
                
        
        
        
        
        #AcousticCategoryConf Configuration
        AcousticCategoryConf= ET.SubElement(SurveyConfiguration,'unit')
        AcousticCategoryConf.set('name','AcousticCategoryConf')
        AcousticCategoryConf= ET.SubElement(AcousticCategoryConf,'configuration')
        parameters= ET.SubElement(AcousticCategoryConf,'parameters')
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','StoreRawDataSpecies')
        parameter.text = 'false'
        
        species= ET.SubElement(AcousticCategoryConf,'species')
        for index, row in metadata.AcousticCategory.iterrows(): 
            specie= ET.SubElement(species,'species')
            specie.set('id',str(row.LSSSacousticCategory))
            specie.set('purpose','1')
            specie.set('name',str(row.commonName))
        
        species= ET.SubElement(AcousticCategoryConf,'speciesMappings')
        for index, row in metadata.AcousticCategory.iterrows(): 
            specie= ET.SubElement(species,'species')
            specie.set('id',str(row.LSSSacousticCategory))
            specie.set('name',str(row.commonName))
        
        
        
        
        #GridConfig Configuration
        GridConf= ET.SubElement(SurveyConfiguration,'unit')
        GridConf.set('name','GridConf')
        GridConf= ET.SubElement(GridConf,'configuration')
        parameters= ET.SubElement(GridConf,'parameters')
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','HorizontalGridUnit')
        parameter.text = 'nmi'
                
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','HorizontalGridSize')
        parameter.text = '0.1'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','MinHorizontalGridSize')
        parameter.text = '0.1'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SchoolHorizontalGridSize')
        parameter.text = '0.05'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','VerticalGridSizePelagic')
        parameter.text = '10'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','VerticalGridSizeBottom')
        parameter.text = '5'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SchoolVerticalGridSizePelagic')
        parameter.text = '5'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SchoolVerticalGridSizeBottom')
        parameter.text = '1'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','VerticalExtentBottom')
        parameter.text = '10'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','PreferredHorizontalSize')
        parameter.text = '5,10,20'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','AutomaticDetailMode')
        parameter.text = 'True'
        
        
        #Mistc config and ICES meta
        MiscConf= ET.SubElement(SurveyConfiguration,'unit')
        MiscConf.set('name','SurveyMiscConf')
        MiscConf= ET.SubElement(MiscConf,'unit')
        MiscConf.set('name','SurveyIcesConf')
        MiscConf= ET.SubElement(MiscConf,'configuration')
        MiscConf= ET.SubElement(MiscConf,'IcesAcousticMetadata')
        parameter= ET.SubElement(MiscConf,'parameter')
        parameter.set('name','Survey')
        parameter.text = metadata.Cruise.Survey[0]
        
        parameter= ET.SubElement(MiscConf,'parameter')
        parameter.set('name','Platform')
        parameter.text = metadata.Cruise.Platform[0]
        
        parameter= ET.SubElement(MiscConf,'parameter')
        parameter.set('name','Organisation')
        parameter.text = str(metadata.Cruise.Organisation[0])
        
        
        #ICES instrument
        
        Instruments= ET.SubElement(MiscConf,'Instruments')
        for index, row in metadata.Instrument.iterrows(): 
            Instrument= ET.SubElement(Instruments,'Instrument')
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','Frequency')
            parameter.text = str(int(row.Frequency/1000))
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerLocation')
            parameter.text = row.TransducerLocation
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerManufacturer')
            parameter.text = row.TransducerManufacturer
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerModel')
            parameter.text = row.TransducerModel
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerSerial')
            parameter.text = str(row.TransducerSerial)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerBeamType')
            parameter.text = str(row.TransducerBeamType)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerDepth')
            parameter.text = str(row.TransducerDepth)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerOrientation')
            parameter.text = row.TransducerOrientation
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerPSI')
            parameter.text = str(row.TransducerPSI)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerBeamAngleMajor')
            parameter.text = str(row.TransducerBeamAngleMajor)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransducerBeamAngleMinor')
            parameter.text = str(row.TransducerBeamAngleMinor)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransceiverManufacturer')
            parameter.text = str(row.TransceiverManufacturer)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransceiverModel')
            parameter.text = row.TransceiverModel
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransceiverSerial')
            parameter.text = str(row.TransceiverSerial)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','TransceiverFirmware')
            parameter.text = str(row.TransceiverFirmware)
            
            parameter= ET.SubElement(Instrument,'parameter')
            parameter.set('name','Comments')
            parameter.text = ''
        
        
        
        ##DataConf config and ICES meta
        DataConf= ET.SubElement(SurveyConfiguration,'unit')
        DataConf.set('name','DataConf')
        config= ET.SubElement(DataConf,'configuration')
        parameters= ET.SubElement(config,'parameters')
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SortByTime')
        parameter.text = 'false'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','TimeGrouping')
        parameter.text = 'DAYS'
            
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','DataDir')
        parameter.text = DataDir
            
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','ReportsDir')
        parameter.text = ReportDir
            
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','WorkDir')
        parameter.text = WorkDir
            
        
        DataConfPromus= ET.SubElement(DataConf,'unit')
        DataConfPromus.set('name','DataConfPromus')
        config= ET.SubElement(DataConfPromus,'configuration')
        parameters= ET.SubElement(config,'parameters')
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','SortByTime')
        parameter.text = 'false'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','TimeGrouping')
        parameter.text = 'DAYS'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','MS70 time offset')
        parameter.text = 'DAYS'
        
        parameter= ET.SubElement(parameters,'parameter')
        parameter.set('name','AutoSelectt')
        parameter.text = 'true'
            
        
                
        display = ET.SubElement(data,'display')
        display = ET.SubElement(display,'moduleManager')
        display.set('name','SouthModuleManager')
        display.set('divider','0.7668')
        display = ET.SubElement(display,'module')
        display.set('name','InterpretationModule')
        display.set('visible','false')
        display.set('floating','false')
        display.set('relativeSize','1.2661')
        
        mydata = minidom.parseString(ET.tostring(data)).toprettyxml(indent="   ")
        myfile = open(lsss_filename, "w")
        myfile.write(str(mydata))
        myfile.close()


