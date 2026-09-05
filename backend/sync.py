import os
import json
import requests
import time


# Update Groups
def updateGroups():
    #os.remove(path= f"backend/cache/groups.json")
    
    pokemon_category = '3'
        
    with requests.Session() as session:    
    
        session.headers.update(({'User-Agent': 'PokemonPriceLookup/1.0.0'}))
        
        try:
            r = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/groups")
            
            if r.status_code == 200:
                data = r.json()
                    
                with open(f"cache/groups.json", 'w') as file:
                    json.dump(data,file)

        except requests.exceptions.RequestException as e:
            print(f"{groupId}_Products request failed: {e}")
    
    return


# Clear Data
def dataClear():
    for name in os.listdir(path=f"cache/ProductsandPrices"):
        os.remove(path= f"cache/ProductsandPrices/{name}")
    return

# Grab Data From TCGCSV.COM
def dataGrab():
    os.makedirs("cache/ProductsandPrices", exist_ok=True)
    
    
    pokemon_category = '3'
    
    #Set up Session
    with requests.Session() as session:
    
        session.headers.update(({'User-Agent': 'PokemonPriceLookup/1.0.0'}))
        
        # Open Groups File to be looked Through
        with open(f"cache/groups.json") as file:
            Groups = json.load(file)
            for Set in Groups["results"]:
                groupId = Set["groupId"]
                
                # Grab products Json for this group
                try:
                    r_Products = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/products")
                    if r_Products.status_code == 200:
                        data = r_Products.json()
                                
                        with open(f"cache/ProductsandPrices/{groupId}_Products.json", 'w') as file:
                            json.dump(data,file)
                    else:
                        print(f"{groupId}_Products failed to be created")
                        
                except requests.exceptions.RequestException as e:
                    print(f"{groupId}_Products request failed: {e}")
                
                # Grab price Json for this group
                try:
                    r_Price = session.get(f"https://tcgcsv.com/tcgplayer/{pokemon_category}/{groupId}/prices")
                    if r_Price.status_code == 200:
                        data = r_Price.json()
                                
                        with open(f"cache/ProductsandPrices/{groupId}_Prices.json", 'w') as file:
                            json.dump(data,file)  
                    else:
                        print(f"{groupId}_Prices failed to be created")
                        
                except requests.exceptions.RequestException as e:
                    print(f"{groupId}_Products request failed: {e}")
                                
                time.sleep(1)
             
            
        
    
    return

def inventoryTest():
    with open(f"cache/groups.json") as file:
        data = json.load(file)
        count = 0
        for x in data["results"]:
            groupId = x["groupId"]
            if not os.path.exists(f"cache/ProductsandPrices/{groupId}_Products.json"):
                print(f"{groupId} Missing")
            else: 
                count += 1
        
        print(count)
    return


def main():
    inventoryTest()


if __name__ == "__main__":
    main()