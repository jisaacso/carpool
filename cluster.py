

from matplotlib import pyplot
from numpy import *
from scipy import cluster,rand,spatial
from geopy import geocoders
from math import radians, cos, sin, asin, sqrt
from pymaps import Map,PyMap,Icon

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km * .621371

if __name__ == '__main__':

    print haversine(70,44,70.1,44.1)

    numclusters = 5
    MAX_CAR_SIZE = 20
    MAX_SEPARATION_MI = 20

    mydata    = genfromtxt('PeopleData.csv',delimiter=",",usecols=(9,10),dtype='float',invalid_raise=True)
    mynames   = genfromtxt('PeopleData.csv',delimiter=",",usecols=(1,),dtype='string',invalid_raise=False)
    myemails  = genfromtxt('PeopleData.csv',delimiter=",",usecols=(3,),dtype='string',invalid_raise=False)
    myaddress = genfromtxt('PeopleData.csv',delimiter=",",usecols=(4,5,6,7),dtype='string',invalid_raise=False)

    nanidx = any(isnan(mydata),1)
    #mycleandata = mydata[~nanidx,:]
    #mycleanemails = myemails[~nanidx]

    mynanaddress=list();
    for row in range(len(mynames)):
        if nanidx[row]:
            mynanaddress.append(', '.join(list([myaddress[row,0],myaddress[row,1],'0'+myaddress[row,2],myaddress[row,3]])))
    print mynanaddress

    f = open('PeopleData-clean.csv','wb')
    g=geocoders.Google()
    
    for row in range(len(mydata)):
        if nanidx[row]:
            try:
                place, (lat,lng)=g.geocode(mynanaddress.pop())
                mydata[row,0]=lng
                mydata[row,1]=lat
                nanidx[row]=False
            except:
#            finally:
#                f.writelines('%s\n' % line for line in t)
                continue
            
    
    mycleandata = mydata[~nanidx,:]
    mycleanemails = myemails[~nanidx,:]
    mycleannames = mynames[~nanidx,:]
    mycleanaddress = myaddress[~nanidx,:]

    numCarpoolers = len(mycleandata)
    
    pyplot.figure()


    dmtx = spatial.distance.pdist(mycleandata,lambda u,v: haversine(u[0],u[1],v[0],v[1]))
    agg_cluster = cluster.hierarchy.complete(dmtx)
    dgram = cluster.hierarchy.dendrogram(agg_cluster,color_threshold=MAX_SEPARATION_MI)
    pyplot.draw()

#    colorbins = unique(dgram['color_list'])
    clusterdict = dict()
   
    color_old = 'z'
    curr_class = 0
    for color in dgram['color_list']:
        if color==color_old and color!='b': #same class
            clusterdict[curr_class].append(dgram['leaves'].pop(0))
            
        else: #new class
            curr_class+=1
            clusterdict[curr_class]=list()
            clusterdict[curr_class].append(dgram['leaves'].pop(0))
            color_old=color

    pyplot.figure()
    MARKER = list(['*k','*c','*g','*b','ok'])
    for key in clusterdict.keys():
        pyplot.plot(mycleandata[clusterdict[key],0],mycleandata[clusterdict[key],1],'*',color = pyplot.get_cmap('jet')(float(key)/(len(clusterdict.keys())-1)),markersize=14)
        print "key is " + str(key)
        print mycleanemails[clusterdict[key]]
        print mycleanaddress[clusterdict[key]]



    pyplot.draw()
    pyplot.show()


