import os
import requests
import time
import psycopg
import dp
import config

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

    
    with dp.get_connection(config.load_settings) as conn:
        
        with conn.cursor() as cur:
            
            for Set in groupData:
                cur.execute(
                     t"INSERT INTO groupdata (groupid, setname, releasedate) VALUES ({Set["groupId"]},{Set["name"]},{Set["publishedOn"]}) ON CONFLICT (groupid) DO NOTHING"
                 )
            
            
    return

# Returns a list of all Sets
def getAllSets(conn: psycopg.Connection):
    with conn.cursor() as cur:
                            
        try:               
            cur.execute(
                "SELECT groupid FROM groupdata"
            )
            return cur.fetchall()
        except psycopg.Error as e:
            print(f"Error: {e}")

def getProductData(session, groupId):
    pokemon_category = '3'
    try:
        r_Products = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/products")
        if r_Products.status_code == 200:
            data = r_Products.json()
            return data["results"]
        else:
            print(f"{groupId}_Products failed to be created")
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"{groupId}_Products request failed: {e}")

def getPriceData(session,groupId):
    pokemon_category = '3'
    try:
        r_Prices = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/prices")
        if r_Prices.status_code == 200:
            data = r_Prices.json()
            return data["results"]
        else:
            print(f"{groupId}_Prices failed to be created")
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"{groupId}_Products request failed: {e}")    
        
        
def filterPriceData(setPriceData):
    filteredPriceData = dict()
    for product in setPriceData:
        if product["productId"] in filteredPriceData:
            
            if product["marketPrice"] is not None:
                if filteredPriceData[product["productId"]] is None or product["marketPrice"] < filteredPriceData[product["productId"]]:
                    filteredPriceData[product["productId"]] = product["marketPrice"]
        else:
            filteredPriceData[product["productId"]] = product["marketPrice"]
    
    return filteredPriceData

def updateProduct(conn,product):
    with conn.cursor as cur:
        
        cur.execute(
            t"INSERT INTO carddata (productid, cardname, imageurl, groupid) VALUES ({product["productId"]},{product["name"]},{product["imageUrl"]},{product["groupId"]}) ON CONFLICT (productid) DO NOTHING"
        )
        
        #Update Rarity If it exists
        for extendedData in product.get("extendedData", []):
            if extendedData["name"] == "Rarity":
                cur.execute(
                    t"UPDATE carddata SET rarity = {extendedData["value"]} WHERE productid = {product["productId"]}"
                ) 
                break  


# Update Card Data to Postgres
def updateCards():    
    
    pokemon_category = '3'
    
    #Set up Session
    with requests.Session() as session:
    
        session.headers.update(({'User-Agent': 'PokemonPriceLookup/1.0.0'}))
        
        groupIDs = [()]
        # Link to 
        with dp.get_connection(config.load_settings) as conn:
                    
            with conn.cursor() as cur:
                        
                groupIDs = getAllSets(conn)

                #Parse through all the sets grabbed from Postgres
                for Set in groupIDs:
                    
                    groupId = Set[0]
                    
                    # Grab products Json for this group from TCGCSV.com
                    setProductData = []
                    try:
                        setProductData = getProductData(session,groupId)
                        
                        #Parse through Products for new set and insert into Postgres
                        for product in setProductData:
                            
                            updateProduct(conn,product)                            

                            
                    except requests.exceptions.RequestException as e:
                        print(f"{groupId}_Products request failed: {e}")
                                
                    
                    # Grab price Json for this group
                    setPriceData = []
                    try:
                        setPriceData = getPriceData(session,groupId)
                        

                        filteredPriceData = filteredPriceData(setPriceData)
                        
                        #Parse through Pricing Data to update prices
                        for productid, price in filteredPriceData.items():                        
                            cur.execute(
                                t"UPDATE carddata SET price = {price} WHERE productid = {productid}"
                            )     
                            
                    except requests.exceptions.RequestException as e:
                        print(f"{groupId}_Prices request failed: {e}")
                                    
                    time.sleep(0.5)
             
            
        
    
    return




def main():
    updateCards()
    return


if __name__ == "__main__":
    main()