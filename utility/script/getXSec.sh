#!/usr/bin/env python

import os,sys
from optparse import OptionParser
import subprocess

def Option_Parser(argv):

    usage='usage: %prog [options] arg\n'
    usage+='This is script which can roughly calculate the Xsec for given MC based on cmssw.\n'
    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--config',
            type='str', dest='config', default='',
            help='Your config file'
            )
    parser.add_option('-d', '--dataset',
            type='str', dest='dataset', default='',
            help='Input your dataset like /ZMM*/*/MINIAOD from DAS'
            )
    parser.add_option('-n', '--nevent',
            type='int', dest='nevent', default=10000,
            help='Number of event needs to be calculated'
            )

    (options, args) = parser.parse_args(argv)
    return options

def genXSec (argv):

    options = Option_Parser(argv)
    filename = options.dataset

    query = 'file dataset=%s ' % filename

    filetype = filename.split('/')[3]
    if filetype == 'USER':
        query += 'instance=prod/phys03'

    s = subprocess.Popen("dasgoclient -query='%s'" % query, shell=True, stdout=subprocess.PIPE)
    stdout, err = s.communicate()
    if err != None:
        print err
        sys.exit()
    output = stdout.split('\n')

    filelist = ''
    for i in range(len(output)-1):
        dummy = ',' if i != len(output)-2 else ''
        file = output[i] + dummy
        filelist += file

    os.system('cmsRun $CMSSW_BASE/src/flashggPlugins/utility/test/getXSec.py inputFiles=%s maxEvents=%d' % (filelist, options.nevent))


if  __name__ == '__main__':
    sys.exit( genXSec(sys.argv[1:]) )
