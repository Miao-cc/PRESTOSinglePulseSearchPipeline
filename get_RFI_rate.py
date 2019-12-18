### This code can get a RFI-rate for each channel in a fits file, it will finally output the RFI rate of each fits file    ###
###      and plot the total RFI for data in a whole day.                                                                   ###                                 ###
### "path" is the lacoation of fits file, and "yemo" is the folder you want to built in your account.                      ###
### A usage can be like " python get_RFI_rate.py /data31/1004/FRB121102/20190830/ RFI_20190830 "                           ###
import pywt
import numpy as np
import astropy.io.fits as pyfits
from badChanSplit import badChanSplit

# get bad channel 
def smooth(sig,threshold = 3, level=8, wavelet='db8'):
    sigma = sig.std()
    dwtmatr = pywt.wavedec(data=sig, wavelet=wavelet, level=level)
    denoised = dwtmatr[:]
    denoised[1:] = [pywt.threshold(i, value=threshold*sigma, mode='soft') for i in dwtmatr[1:]]
    smoothed_sig = pywt.waverec(denoised, wavelet, mode='sp1')[:sig.size]
    noises = sig - smoothed_sig
    return smoothed_sig, noises

def badChanRate(bandpass,level=5):
    nchan = len(bandpass)
    sig,nos = smooth(bandpass,level=level)###level can change
    idxarr = np.arange(bandpass.size)
    y2 = abs((sig-bandpass)/sig)### shreshold for RFI
    nan=np.isnan(y2)
    inf=np.isinf(y2)
    y2[nan]=0
    y2[y2==1]=0
    #print y2
    idxgood = idxarr[y2<0.05]### good channel
    idxbad = idxarr[y2>=0.05]
    channel_list=np.arange(nchan)
    channel_list[idxgood]=0
    channel_list[idxbad]=1
    return channel_list

def fileTypeCheck(filename):
    filename = str(filename)
    if filename.endswith('.fits'):
        FileType = 'fits'
    elif filename.endswith('.fil'):
        FileType = 'fil'
    else:
        FileType = 'Unkown-type'

    return FileType


def getBadChanFil(filename, rfiFindTime=0.5):
   
    # check sigpyproc module
    try:
        from sigpyproc.Readers import FilReader as filterbank
    except ImportError:
        print "Import error. No such module: ",sigpyproc, ". SKIP"
        pass
    #else:
        #print "Some errors happened"
        #pass

    fil = filterbank(filename)
    fch1 = fil.header['fch1']
    df = fil.header['foff']
    fmin = fil.header['fbottom']
    fmax = fil.header['ftop']
    nsamp = fil.header['nsamples']
    tsamp = fil.header['tsamp']
    nf = fil.header['nchans']
    tstart = fil.header['tstart']
    nchans = fil.header['nchans']
    hdrlen = fil.header['hdrlen']
    
    print 'fch1: ', fch1, 'df: ', df, 'nsamp: ', nsamp, 'tsamp: ', tsamp, 'nchans: ', nchans
    
    fil._file.seek(hdrlen)
    data = fil._file.cread(nchans*nsamp)
    data = np.array(data.reshape((nsamp, nf)).transpose(), order='C')
    print data.dtype
    l, m = data.shape

    # subint num per rfiFindTime
    DownSampNum = int(rfiFindTime / tsamp)
    # create bandpass list
    bandpassList = np.zeros((int(nsamp/DownSampNum - 1), 4096))
    channel_bad=[]
    # def pol; only one pol

    # get bandpass 
    for samp in range(int(nsamp/DownSampNum - 1)):
        startSamp = samp * DownSampNum
        endSamp = (samp+1) * DownSampNum
        print "reading: ", samp * DownSampNum, " to ", (samp+1) * DownSampNum
        print "reading data now. Pol ", i
        bandpass = data[startSamp:endSamp,:]
        bandpass = np.sum(bandpass,axis=0)
        bandpassList[samp, :] += bandpass

        print "smooth now"
        channel_list = badChanRate(bandpassList[samp, :])

    channel_bad.append(channel_list)
    badchannel = idxarr[idxbad]
    np.savetxt('%s_badChan.txt'%(filename), badchannel, fmt='%d')
    badChanSplit('%s_badChan.txt'%(filename))

def getBadChanFits(filename, rfiFindTime=0.5):
    # open file
    hdulist = pyfits.open(filename)
    hdu0 = hdulist[0]
    hdu1 = hdulist[1]
    header0 = hdu0.header
    header1 = hdu1.header

    #get file info
    nchan=header0['OBSNCHAN']
    nsblk=header1['NSBLK']
    npol=header1['NPOL']
    tbin=header1['TBIN']
    nline=header1['NAXIS2']
    print 'Spectra per subint: ', nsblk, 'Sample time(s): ', tbin, 'channel Num: ', nchan
    tsubint = nsblk * tbin
    print 'Time per subint: ', tsubint
    # get data
    data = hdu1.data['data']

    # subint num per rfiFindTime
    DownSampNum = int(rfiFindTime / tsubint)
    # create bandpass list
    bandpassList = np.zeros((int(nline/DownSampNum - 1), 4096))
    channel_bad=[]
    # def pol; only pol1 and pol2
    if (npol<=2):
        polNum = npol
    else:
        polNum = 2

    # get bandpass 
    for subint in range(int(nline/DownSampNum - 1)):
        startSubint = subint * DownSampNum
        endSubint = (subint+1) * DownSampNum
        print "reading: ", subint * DownSampNum, " to ", (subint+1) * DownSampNum
        for i in range(polNum):
            print "reading data now. Pol ", i
            bandpass = data[startSubint:endSubint,:,i,:,:].squeeze().reshape((-1,nchan))
            bandpass = np.sum(bandpass,axis=0)
            bandpassList[subint, :] += bandpass
        print "smooth now"
        channel_list = badChanRate(bandpassList[subint, :])
    channel_bad.append(channel_list)
    badchannel = idxarr[idxbad]
    np.savetxt('%s_badChan.txt'%(filename), badchannel, fmt='%d')
    badChanSplit('%s_badChan.txt'%(filename))


def getBadchan(filename, rfiFindTime=0.5):
    # get file type
    FileType = fileTypeCheck(filename)
    # diff func for diff file type
    if FileType=='fil':
        getBadChanFil(filename, rfiFindTime=0.5)

    elif FileType=='fits':
        getBadChanFits(filename, rfiFindTime=0.5)
    else :
        print "==================="
        print "Unkown file format. ", FileType
        print "==================="

