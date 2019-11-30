### This code can get a RFI-rate for each channel in a fits file, it will finally output the RFI rate of each fits file    ###
###      and plot the total RFI for data in a whole day.                                                                   ###                                 ###
### "path" is the lacoation of fits file, and "yemo" is the folder you want to built in your account.                      ###
### A usage can be like " python get_RFI_rate.py /data31/1004/FRB121102/20190830/ RFI_20190830 "                           ###
import numpy as np
import pywt
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


def getBadchan(filename, rfiFindTime=0.5):
    channel_bad=[]
    
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

    # subint num per rfiFindTime
    DownSampNum = int(rfiFindTime / tsubint)

    # create bandpass list
    bandpassList = np.zeros((int(nline/DownSampNum - 1), 4096))

    # get data
    data = hdu1.data['data']

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
        sig,nos = smooth(bandpassList[subint, :],level=5)###level can change
        idxarr = np.arange(bandpassList[subint, :].size)
        y2 = abs((sig-bandpassList[subint, :])/sig)### shreshold for RFI
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
    channel_bad.append(channel_list)
    badchannel = idxarr[idxbad]
    np.savetxt('%s_badChan.txt'%(filename), badchannel, fmt='%d')
    badChanSplit('%s_badChan.txt'%(filename))


