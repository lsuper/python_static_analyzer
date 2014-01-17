'''
Created on Sep 9, 2012

@author: psachdev
'''
#import manager
import namespaceanalyzer
import permission
import SearchIntents
import DbManager
import logging
import sys

from androguard.core.bytecodes import apk
from androguard.core.bytecodes import dvm
from androguard.core.analysis.analysis import *

from multiprocessing import Pool

def handler (signum, sigframe):
    raise Exception ("Killed");


def analyze((apkEntry, OUT)):
    try:
        OUT = OUT + '/'
        fileName = apkEntry['packageName'] + '.apk'
        path = apkEntry['fileDir']
        print "FileName Analyzed :"  + fileName
        tokens = namespaceanalyzer.NameSpaceMgr.GetTokensStatic (path, '/')
        category =  tokens [len (tokens) - 1]
        #print category
        filename = path + '/' + fileName
        outFileName = '/package.txt'
        outFileName = OUT + outFileName
        instance = namespaceanalyzer.NameSpaceMgr()
    
        a = apk.APK(filename)
        d = dvm.DalvikVMFormat (a.get_dex())
        dx = uVMAnalysis (d)
    
        packages = instance.execute (filename, outFileName, dbMgr, fileName, category, a, d, dx)
                
        outfile_perm = '/permissions.txt'
        outfile_perm = OUT + outfile_perm
        permission.StaticAnalyzer (filename, outfile_perm, packages, dbMgr, fileName, a, d, dx)
                
        outfile_links = '/links.txt'
        outfile_links = OUT + outfile_links
        SearchIntents.Intents(filename, outfile_links, packages, dbMgr, fileName, a, d, dx);
        dbMgr.androidAppDB.apkInfo.update({'packageName':apkEntry['packageName']}, {'$set': {'isApkUpdated': False}})
        return apkEntry['packageName']
    except Exception as e:
        e.args = [apkEntry['packageName']]
        raise e

if __name__ == '__main__':
    OUT = sys.argv[1]
    analyzedApkFile = open(OUT + '/' + 'filelist.txt', 'a+')
    '''
    Database Handle used to insert fields
    '''
    dbMgr = DbManager.DBManagerClass()
    
    '''
    Example of how the various entrie are made into the database
    dbMgr.insert3rdPartyPackageInfo("testpackage", "testfilename", "testexternalpackage")
    dbMgr.insertPermissionInfo('testpackage', 'testfilename', 'testpermission', True, 'testdest', 'testexternalpackagename', 'testsrc')
    dbMgr.insertLinkInfo('testpackage', 'testfilename', 'testlink', True, 'testdest', 'testexternalpackagename')
    '''
    # Make a global logging object.
    logObject = logging.getLogger("logfile")
    logObject.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    logFileHandler = logging.FileHandler(OUT + '/exceptions.log')
    logFileHandler.setLevel(logging.DEBUG)
    logFormat = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
    logFileHandler.setFormatter(logFormat)
    logObject.addHandler(logFileHandler)
    

    try:
        apkList = list(dbMgr.androidAppDB.apkInfo.find({'isApkUpdated':True},{"fileDir":1, 'packageName':1}))
        apkList = [(entry, OUT, logObject) for entry in apkList]
        #apkList = [({'packageName': line.rstrip('\n').replace(".apk",''), 'fileDir': '../downloads/'}, OUT) for line in open("apkList").readlines()]
        numberOfProcess = 4
        pool = Pool(numberOfProcess)
        for packageName in pool.imap(analyze, apkList):
            analyzedApkFile.write(packageName + '\n')
            
    except Exception as e:
        packageName = ''
        if len(e.args) > 1:
            packageName = e.args[0]
            
        logObject.error("\n")
        logObject.error("=======================================================================")
        logObject.error("\n")
        logObject.exception("Main : Exception occured for " + packageName)


            
                
               
            
    
    
