# -*- coding: utf-8 -*-
"""
Created on Thu May  6 12:51:58 2021

@author: sindrev
"""



def runReportFromLSSS(URLprefix= 'http://localhost:8000',
                     lsssFile=[],
                     alternative_datadir_path = [],
                     frequency=38,
                     makeNewDB = True):
    
    
    
    
    import requests, json
    from datetime import date
    
            
        
    
    def get(path, params=None):
        
        """
        Function to 
        """
        url = URLprefix + path
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        raise ValueError(url + ' returned status code ' + str(response.status_code) + ': ' + response.text)
    
    
    def post(path, params=None, json=None, data=None):
        url = URLprefix + path
        response = requests.post(url, params=params, json=json, data=data)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 204:
            return None
        raise ValueError(url + ' returned status code ' + str(response.status_code) + ': ' + response.text)
    

    
    if makeNewDB == True: 
        print("Disconnected database")
        post("/lsss/application/config/unit/DatabaseConf/connected", json={'value':False})
        
        print("Create a new database")
        post('/lsss/application/config/unit/DatabaseConf/create') #, json={'empty':True})
        
    print("Connect to the new database")
    r = requests.post(URLprefix + "/lsss/application/config/unit/DatabaseConf/connected", json={'value':True})
    print("Connect to the new database: " + str(r.status_code))
    
    print("Opening survey")
    post('/lsss/survey/open', json={'value':lsssFile})
    
    
    #overwrite path
    print('Load echosounder data')
    if alternative_datadir_path != []:
        post('/lsss/survey/config/unit/DataConf/parameter/DataDir', json={'value':alternative_datadir_path})
    
        
    #Hack to load all files
    #LSSS only load those files set in the .lsss file. T
    #Underneath will load the whole survey
    r = requests.get(URLprefix + '/lsss/survey/config/unit/DataConf/files')
    firstIndex = 0
    lastIndex = len(r.json()) - 1
    post('/lsss/survey/config/unit/DataConf/files/selection', json={'firstIndex':firstIndex, 'lastIndex':lastIndex})
        
        
    # Wait until the program is ready for further processing
    get('/lsss/data/wait')

    
    # Store to local LSSS DB
    print('Storing to database (This takes time)')
    post('/lsss/module/InterpretationModule/database', json={'quality':1,'frequencies':[frequency, frequency]})
    
    
    
    get('/lsss/data/wait')
    
        
    #write the LUF25 report
    r = requests.get(URLprefix + '/lsss/database/report/25')

    
    with open(get('/lsss/survey/config/unit/DataConf/parameter/ReportsDir')['value']+'/test.xml', 'w+') as f:
            f.write(r.text)

    get('/lsss/data/wait')
    
    post('/lsss/survey/close')
    
    