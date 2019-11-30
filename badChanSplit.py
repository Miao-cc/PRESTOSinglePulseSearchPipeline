import numpy as np


# read file
# get bad channel list
def badChanSplit(filename):
    #filename = 'FRB121102_20190806.fits_badChan.txt'
    data = np.loadtxt(filename,dtype=int)
    
    print "Length of bad chan list: ", len(data)
    
    # get bad channel bands
    # if data[n] - data[n-1] > 5, start a new band
    # if data[n] - data[n-1] < 5, put in same band
    count = 0
    chanList = []
    chanList.append(data[0])
    for num, i in enumerate(data[1:]):
        if(data[num] - data[num-1]) > 5:
            count += 1
            chanList.append(data[num-1])
            chanList.append(data[num])
    chanList.append(data[-1])
    
    # get rfi band list start&end
    
    # out put the band to format in prepsto
    # start:end,start1:end1
    with open(filename+'.new', 'w') as f:
        count = 0
        for i in range(len(chanList)/2 - 1):
            count += 1
            chanBand = str(chanList[2*i])+':'+str(chanList[2*i+1])+','
            print count, chanBand
            f.write(chanBand)
        i += 1
        chanBand = str(chanList[2*i])+':'+str(chanList[2*i+1])
        print count, chanBand
        f.write(chanBand)
    
    
    # plot the rfi
    '''
    import matplotlib.pylab as plt
    y = np.zeros(4096)
    y1 = np.zeros(4096)
    
    x = np.arange(4096)
    y[data] = 1
    y1[chanList] = 1
    
    plt.scatter(x, y)
    for i in range(len(chanList)/2):
        print count, str()+':'+str(chanList[2*i+1])
        plt.plot([chanList[2*i], chanList[2*i+1]], [1,1], 'r')
        plt.scatter(chanList[2*i], 1, c='r')
        plt.scatter(chanList[2*i+1], 1, c='r')
    
    plt.yticks([1, 0], ('RFI', 'no RFI'))
    plt.xlabel('channels')
    
    
    
    plt.show()
    '''
