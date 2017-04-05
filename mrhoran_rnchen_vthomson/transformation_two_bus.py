# some kmeans shenanigans

import json
import dml
import prov.model
import datetime
import uuid
import ast
import random
import sodapy
from geopy.distance import vincenty
import time 

# this transformation will check how many comm gardens and food pantries there are for each area
# we want to take (zipcode, #comm gardens) (zipcode, #food pantries) --> (area, #food pantries#comm gardens)
# I think this is a selection and aggregation

class transformation_two_bus(dml.Algorithm):

    contributor = 'mrhoran_rnchen_vthomson'

    reads = ['mrhoran_rnchen_vthomson.schools']

    writes = ['mrhoran_rnchen_vthomson.kmeans_school_hubs']


    @staticmethod
    def execute(trial = False):
        
        startTime = datetime.datetime.now()

        client = dml.pymongo.MongoClient()

        repo = client.repo
        
        repo.authenticate('mrhoran_rnchen_vthomson', 'mrhoran_rnchen_vthomson')

        ## For this transformation we want to focus on using k means to look at the hubs of schools
        ## we are going to focus on the effects of different numbers of k and its effects on the means


        ## getting coordinates of sc
        S = project([x for x in repo.mrhoran_rnchen_vthomson.schools.find({})], get_school_locations)

        
        def k_means(P,M):
            
            OLD = []
        
            while OLD != M:
                
                OLD = M

                MPD = [(m, p, dist(m,p)) for (m, p) in product(M, P)]
                PDs = [(p, dist(m,p)) for (m, p, d) in MPD]
                PD = aggregate(PDs, min)
                MP = [(m, p) for ((m,p,d), (p2,d2)) in product(MPD, PD) if p==p2 and d==d2]
                MT = aggregate(MP, plus)

                M1 = [(m, 1) for ((m,p,d), (p2,d2)) in product(MPD, PD) if p==p2 and d==d2]
                MC = aggregate(M1, sum)

                M = [scale(t,c) for ((m,t),(m2,c)) in product(MT, MC) if m == m2]
                
                return(sorted(M))

        ## calculating the cost now

        ## first we want to go through and see which mean is the closest, and keep that distance
        ## store that in a big array

        def costs(S, M):

            cost_array = [0]*(len(S))
            closest_k = 1000

            #print(vincenty(newport_ri, cleveland_oh).miles)
        
            for j in range(len(S)):
                closest_k = 1000
                for i in range(len(M)):

                    distance = (vincenty(S[j], M[i]).miles)
                
                    if (distance < closest_k):
                        
                        closest_k = distance
                        
                cost_array[j] = closest_k
                    
    
            ## find the cost by adding up all the distances and diving it by the number of distances to get the average
            ## cost value for each point.. ie how close do the means get and is there a drop off in terms of productivity

            ## use this shit for a graph

            overall_cost = 0

            for i in range(len(cost_array)):

                print("distance from each point to the means:")
                print(cost_array[i])

                overall_cost += cost_array[i]

            return((overall_cost/len(cost_array)))

        print("number of school points")
        print(S)

        num_means =44
        

        M = [None]*num_means;

        # the means are picked randomly for the start 
        for i in range(0, num_means):

            x = random.randint(0, len(S)-1)
            val = S[x]
            M[i] = val

        ## trying to split the data to make it better
        print("")
        print("number of means:")
        print(M)

        x = int(len(S)/2)
        
        P1 = [None]*x
        P2 = [None]*x

        for i in range(x):
            
            P1[i] = S[i]
            P2[i] = S[i+x]


        mean = k_means(P1, M)
        mean2 = k_means(P2, M)

        print("new means after kmeans for P1:")
        results_half = print(mean)
        
        print("new means after kmeans for P2:")
        results_half = print(mean2)

        cost_combined = (costs(P1, mean)+costs(P1, mean2))/2
        
        print("costfor one is"+ str(costs(P1, mean)))
        print("costfor two is"+ str(costs(P2, mean2)))
              
        print("costfor two means is" + str(cost_combined))
        
        #repo.dropCollection('mrhoran_rnchen.local_fm')
        #repo.createCollection('mrhoran_rnchen.local_fm')

        #repo.mrhoran_rnchen.local_fm.insert(dict(X))

        repo.logout()

        endTime = datetime.datetime.now()

        return {"start":startTime, "end":endTime}

    
    @staticmethod
    def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
        '''
            Create the provenance document describing everything happening
            in this script. Each run of the script will generate a new
            document describing that invocation event.
            '''

        # Set up the database connection.
##        client = dml.pymongo.MongoClient()
##        repo = client.repo
##        repo.authenticate('mrhoran_rnchen', 'mrhoran_rnchen')
##        
##        doc.add_namespace('alg', 'http://datamechanics.io/algorithm/') # The scripts are in <folder>#<filename> format.
##        doc.add_namespace('dat', 'http://datamechanics.io/data/') # The data sets are in <user>#<collection> format.
##        doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
##        doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
##        doc.add_namespace('bdp', 'https://data.cityofboston.gov/resource/')
##
##        this_script = doc.agent('alg:mrhoran_rnchen#transformation_two', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
##        
##        resource1 = doc.entity('bdp:66t5-f563', {'prov:label':'Farmers Market', prov.model.PROV_TYPE:'ont:DataResource', 'ont:Extension':'json'})
##
##        get_farmers_market = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
##
##        doc.wasAssociatedWith(get_farmers_market, this_script)
##
##        doc.usage(get_farmers_market, resource1, startTime, None,
##                  {prov.model.PROV_TYPE:'ont:Retrieval'
##                  }
##                  )
##        farmers_market = doc.entity('dat:mrhoran_rnchen#farmers_market', {prov.model.PROV_LABEL:'Food Pantries', prov.model.PROV_TYPE:'ont:DataSet','ont:Extension':'json'})
##        doc.wasAttributedTo(farmers_market, this_script)
##        doc.wasGeneratedBy(farmers_market, get_farmers_market, endTime)
##        doc.wasDerivedFrom(farmers_market, resource1, get_farmers_market, get_farmers_market, get_farmers_market)
##        repo.logout()
##                  
##        return doc
        return ""
def dist(p, q):
    (x1,y1) = p
    (x2,y2) = q
    return (x1-x2)**2 + (y1-y2)**2

def plus(args):
    p = [0,0]
    for (x,y) in args:
        p[0] += x
        p[1] += y
    return tuple(p)
def scale(p, c):
    (x,y) = p
    return (x/c, y/c)

def project(R, p):
    return [p(t) for t in R]

def select(R, s):
    return [t for t in R if s(t)]
def product(R, S):
    return [(t,u) for t in R for u in S]
def aggregate(R, f):
    keys = {r[0] for r in R}
    return [(key, f([v for (k,v) in R if k == key])) for key in keys]

def get_school_locations(schools):

    lat = float(schools["Latitude"])
    long = float(schools["Longitude"])
    #name = schools["School Name"]

    x = (schools["Address"].split(','))

    #print("ss" + x[1] ==("02135"))
    
    #if (x[1] == ("02135") or x[1] == '02126'or x[1] == '02129'or x[1] == '02215'or x[1] == '02124' or x[1] == '02129'):
    
    return((lat,long))
        
def get_busyard_locations(bus):

    lat = bus['Bus Yard Latitude']
    long = bus['Bus Yard Longitude']
    name =  bus['Bus Yard']

    return((name, (lat,long)))
    
transformation_two_bus.execute()
#doc = transformation_two_bus.provenance()
#print(doc.get_provn())
#print(json.dumps(json.loads(doc.serialize()), indent=4))

## eof
