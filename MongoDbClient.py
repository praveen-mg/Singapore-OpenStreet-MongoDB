from pymongo import MongoClient
import pprint
client = MongoClient('localhost', 27017)



def top_user (count):
    """
    Check for user contribution, if count is zero it returns contribution of all users, otherwise returns contribution of top users in descending order
    """
    if count == 0:
        pipeline = [{"$group":{"_id":"$created.user","count":{"$sum":1}}},{"$sort":{"count":-1}}]
    else:
        pipeline = [{"$group":{"_id":"$created.user","count":{"$sum":1}}},
                    {"$sort":{"count":-1}},{"$limit":count}]
    return pipeline
    
def single_contribution():

    """
    Users who have contrinuted only once
    """
    pipeline = [{"$group":{"_id":"$created.user","count":{"$sum":1}}},
                {"$group":{"_id":"$count","number":{"$sum":1}}},{"$sort":{"_id": 1}},
                {"$limit":1}]
    return pipeline

def top_amenity():
    """
    Check for top 10 amenities
    """
    #pipeline = {$group:{"_id":"$amenity","count":{"$sum":1}}} #[{$group:{"_id":"$amenity","count":{"$sum":1}}},{"$sort":{"count":-1}}]
    pipeline = [{"$match":{"amenity":{"$exists":1}}},
                {"$group":{"_id":"$amenity","count":{"$sum":1}}},
                {"$sort":{"count":-1}},{"$limit":10}]
    return pipeline
def db_query(db,query):
    return db.city.find(query)
    
def db_aggregate(db,pipeline):
    return [doc for doc in db.city.aggregate(pipeline)]
    
def db_top_fastfood():
    """
    return fast food chain count in descending order
    """
    pipeline = [{"$match":{"$and" :[{"amenity":"fast_food"},{"name":{"$exists":1}}]}},
                {"$group":{"_id":"$name","count":{"$sum":1}}},
                {"$sort":{"count":-1}}]
    return pipeline
    
def db_top_cusine():
    """
    return restarunts in descending order based on their cuisine
    """
    pipeline = [{"$match":{"$and" :[{"amenity":"restaurant"},{"cuisine":{"$exists":1}}]}},
                {"$group":{"_id":"$cuisine","count":{"$sum":1}}},
                {"$sort":{"count":-1}}]
    return pipeline
    
def db_top_religion():
    #{"$match":{"$and" :[{"amenity":"place_of_worship"},{"religion":{"$exists":1}}]}},
    """
    Return religion based on number of place of worrship in descending order
    """
    pipeline = [{"$match":{"amenity":"place_of_worship"}},
                {"$group":{"_id":"$religion","count":{"$sum":1}}},
                {"$sort":{"count":-1}}]
    return pipeline
    
def db_cities():

    """
    return different cities present in the data
    """
    
    pipeline = [{"$match":{"address.city":{"$exists":1}}},
                {"$group":{"_id":"$address.city","count":{"$sum":1}}},
                {"$sort":{"count":-1}}]
    return pipeline
    
def find():
    #cities = db.city.find({ "name": "PIE"})
    db = client.work
    
    
        
   
    print "Total Number of Nodes:", db_query(db,{"type":"node"}).count()
    print "Total Number of Way:", db_query(db,{"type":"way"}).count()
    print "Total number of distinct Users:",len(db.city.distinct("created.user"))
    #cities present in database
    
    """
    cities
    """
   
    cities_data = db_aggregate(db,db_cities())
    for city_data in cities_data:
        pprint.pprint(city_data)
  
    #print ""db.city.find({"type":"node"}).count()
   
    #top user contribution
    
    top_users = db_aggregate(db,top_user(1))
    print "Top User"
    pprint.pprint(top_users)
    users = db_aggregate(db,top_user(0))
    print "Total Number of Users",len(users)
    total = 0
    for user in users:
        total = total + user['count']
    print "Total",total
    
    top_user_countribution = (float(users[0]['count'])/float(total)) * 100
    contribution = 0
    for i in range(50):
        contribution = contribution + users[i]['count']
        percent = (float(contribution)/float(total)) * 100
        print "Contribution of top",i+1," User:",percent
    #print "User with top comtribution",top_user_countribution
    single_contributions = db_aggregate(db,single_contribution())
    print "Total number of users with single contribution"
    for user in single_contributions:
        pprint.pprint(user)
       
       
    #Getting top 10 amenities
   
    amenities = db_aggregate(db,top_amenity())
    for aminity in amenities:
        pprint.pprint(aminity)
    
    
    
    
    count = 0
    fast_food = db_aggregate(db,db_top_fastfood())
    
    for operator in fast_food:
        pprint.pprint(operator)
        count = count + 1
        #if count == 5:
            #break
   
   
    
    top_cusine = db_aggregate(db,db_top_cusine())
    for cusine in top_cusine:
        pprint.pprint(cusine)
    
   
    """
    Top religions in SIngapore
    """
   
    religions = db_aggregate(db,db_top_religion())
    
    for religion in religions:
        pprint.pprint(religion)
   
   

if __name__ == '__main__':
    find()
