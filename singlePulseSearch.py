import os
import sys
import glob
import yaml
import numpy as np
from get_RFI_rate import getBadchan
from multiprocessing import Pool


def single_pulse_search(filename, dm):
    command = 'single_pulse_search.py -t 7 -b -m 300 -p {filename}_DM*{dm}*.dat'.format(filename=filename,dm=dm)
    print command
    os.system(command)


#rfifind 
def rfifind(fitsFile):
    #rfifind 
    #command = 'rfifind -time 0.5 -o {fitsname} {fitsname}'.format(fitsname=fitsfile)
    #rfifind  with badchan
    command = 'rfifind -time 1.0 -o {fitsname} {fitsname}'.format(fitsname=fitsFile)
    print command
    os.system(command)


#prepdata
def prepdata(dm, fitsFile, rfitime):
    # prepdata
    #prepdata -dm ${DM} -o ${FILENAME}_dat -mask ${Filename}_rfifind.mask ${FILENAME}
    #command = 'prepdata -dm {dm} -o {fitsname}-dm_{dm} -mask {fitsname}_rfifind.mask {fitsname}'.format(fitsname=fitsFile,dm=dm)
    #RFIfind
    badchan = filename+'_badChan.txt.new'
    if os.path.exists(badchan):

        bandChanList = [i.strip('\n') for i in open(badchan, 'r')][0]
        command = 'prepsubband -nobary -nsub 2048 -ignorechan {bandChanList} -lodm {dm} -dmstep 0 -numdms 1 -mask {fitsname}_rfifind.mask -o {fitsname} {fitsname}'.format(fitsname=fitsFile,dm=dm, bandChanList=bandChanList)
        print command
        os.system(command)
    else:
        command = 'prepsubband -nobary -nsub 2048 -lodm {dm} -dmstep 0 -numdms 1 -mask {fitsname}_rfifind.mask -o {fitsname} {fitsname}'.format(fitsname=fitsFile,dm=dm)
        print command
        os.system(command)



if __name__ == '__main__':
    
    #pulsar search 
    #rfifind 
    #multi prepdata
    #multi prepfold

    inparameters = sys.argv[1:]
    if (len(inparameters) != 4):
        print "  Usage:"
        print "     python singlePulseSearch.py filename numout lowDM highDM dDM"
    else: 
        filename     = inparameters[0]
        lowDM        = [float(inparameters[1])]
        highDM       = [float(inparameters[2])]
        dDM          = [float(inparameters[3])]

    ncpus = 70

    # rfifind
    rfifind(filename)

    # get band chan using wavelet
    rfitime = 0.5
    getBadchan(filename, rfiFindTime=rfitime)

    dms = np.array([])
    for i in range(len(lowDM)):
        dms = np.concatenate((dms,np.arange(lowDM[i],highDM[i],dDM[i])), axis=0)

    # prep data
    p = Pool(processes=ncpus)
    for dm in dms:
        print 'Parent process %s.' % os.getpid()
        p.apply_async(prepdata, args=(dm, filename, rfitime))
    p.close()
    p.join()
    
    # search single pulse with no plot
    p = Pool(processes=ncpus)
    for dm in dms:
        print 'Parent process %s.' % os.getpid()
        p.apply_async(single_pulse_search, args=(filename, dm))
    p.close()
    p.join()
    
    # plot result
    command = 'single_pulse_search.py -t 6 -b -m 300 {filename}_DM*.singlepulse'.format(filename=filename)
    print command
    os.system(command)
