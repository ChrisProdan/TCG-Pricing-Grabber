import os
import json
import requests
import time
import psycopg

from dotenv import load_dotenv

load_dotenv()
password = os.environ.get("DB_PASSWORD")

# Update GroupsData to Postgres
def updateGroups():
    
    pokemon_category = '3'
    
    data = -1
    groupData = []
    with requests.Session() as session:    
    
        session.headers.update(({'User-Agent': 'PokemonPriceLookup/1.0.0'}))
        
        try:
            r = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/groups")
            
            if r.status_code == 200:
                data = r.json()
                groupData = data["results"]

        except requests.exceptions.RequestException as e:
            print(f"Groups request failed: {e}")

    
    with psycopg.connect(dbname="Pokemon_Pricing_Information",
                         user="postgres",
                         password=password,
                         port=5432,
                         host="localhost",
                         autocommit=True) as conn:
        
        with conn.cursor() as cur:
            
            for Set in groupData:
                cur.execute(
                     t"INSERT INTO groupdata (groupid, setname, releasedate) VALUES ({Set["groupId"]},{Set["name"]},{Set["publishedOn"]}) ON CONFLICT (groupid) DO NOTHING"
                 )
            
            
    return



# Update Card Data to Postgres
def updateCards():    
    
    pokemon_category = '3'
    
    #Set up Session
    with requests.Session() as session:
    
        session.headers.update(({'User-Agent': 'PokemonPriceLookup/1.0.0'}))
        
        groupIDs = [()]
        # Link to 
        with psycopg.connect(dbname="Pokemon_Pricing_Information",
                                     user="postgres",
                                     password=password,
                                     port=5432,
                                     host="localhost",
                                     autocommit=True) as conn:
                    
            with conn.cursor() as cur:
                        
                   
                cur.execute(
                    "SELECT groupid FROM groupdata"
                )
                groupIDs = cur.fetchall()

                #Parse through all the sets grabbed from Postgres
                for Set in groupIDs:
                    
                    groupId = Set[0]
                    
                    # Grab products Json for this group from TCGCSV.com
                    setProductData = []
                    try:
                        r_Products = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/products")
                        if r_Products.status_code == 200:
                            data = r_Products.json()
                            setProductData = data["results"]
                        
                            #Parse through Products for new set and insert into Postgres
                            for product in setProductData:
                                
                                cur.execute(
                                    t"INSERT INTO carddata (productid, cardname, imageurl, groupid) VALUES ({product["productId"]},{product["name"]},{product["imageUrl"]},{product["groupId"]}) ON CONFLICT (productid) DO NOTHING"
                                )                                

                        else:
                            print(f"{groupId}_Products failed to be created")
                            
                    except requests.exceptions.RequestException as e:
                        print(f"{groupId}_Products request failed: {e}")
                
                
                    
                    # Grab price Json for this group
                    setPriceData = []
                    try:
                        r_Price = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/prices")
                        if r_Price.status_code == 200:
                            data = r_Price.json()
                            setPriceData = data["results"]
                        
                            #Filtered Pricing Data to Remove Duplicates
                            filteredPriceData = dict()
                            for product in setPriceData:
                                if product["productId"] in filteredPriceData:
                                    
                                    if product["marketPrice"] is not None:
                                        if filteredPriceData[product["productId"]] is None or product["marketPrice"] < filteredPriceData[product["productId"]]:
                                            filteredPriceData[product["productId"]] = product["marketPrice"]
                                else:
                                    filteredPriceData[product["productId"]] = product["marketPrice"]

                            
                            #Parse through Pricing Data to update prices
                            for productid, price in filteredPriceData.items():                        
                                cur.execute(
                                    t"UPDATE carddata SET price = {price} WHERE productid = {productid}"
                                )     

                        else:
                            print(f"{groupId}_Prices failed to be created")
                            
                    except requests.exceptions.RequestException as e:
                        print(f"{groupId}_Prices request failed: {e}")
                                    
                    time.sleep(0.5)
             
            
        
    
    return




def main():
    updateCards()
    return


if __name__ == "__main__":
    main()