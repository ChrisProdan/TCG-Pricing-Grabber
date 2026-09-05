import json
from flask import Flask
import os
from flask_cors import CORS
from flask import jsonify
import time

import sync

app = Flask(__name__)
CORS(app)

# Returns set ID from name, -1 if failure
def getSet(setName):
    with open("cache/groups.json") as file:
        file = json.load(file)
        
        for set in file["results"]:
            if set['name'] == setName:
                return set['groupId']
        
    
    return -1


# Syncs Daily Pricing Data incase it is outdated
def syncData():
    try:
        timeSinceSync  = time.time() - os.path.getctime("cache/ProductsandPrices/604_Prices.json")
        
        if timeSinceSync >= 86400:
            sync.dataGrab()
    except:
        sync.dataGrab()
    
    return

# Returns Card imageUrl and Price given setName and cardName
@app.route("/<path:setName>/<path:cardName>")        
def getCardInfo(setName, cardName):
    #syncData()
    
    groupId = getSet(setName)
    
    if groupId == -1:
        return jsonify({"error": "not found"}), 404
    
    cardId = -1
    imageUrl = None
    price = -1
    with open(f"cache/ProductsandPrices/{groupId}_Products.json") as file:
        file = json.load(file)
        
        for card in file["results"]:
            if card['name'] == cardName:
                cardId = card['productId']
                imageUrl = card['imageUrl']
        
    if cardId == -1:
        return jsonify({"error": "not found"}), 404
    
    with open(f"cache/ProductsandPrices/{groupId}_Prices.json") as file:
            file = json.load(file)
            
            for card in file["results"]:
                if card['productId'] == cardId:
                    price = card['marketPrice']
    
    return jsonify([imageUrl, str(price)])
    
                
        
        

    




def main():
    return
    print(getCardInfo("ME05: Pitch Black","Mega Darkrai ex - 116/084"))


if __name__ == "__main__":
    main()