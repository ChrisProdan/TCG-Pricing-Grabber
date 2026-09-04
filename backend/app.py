import json
import os
from flask import Flask

app = Flask(__name__)


# Returns set ID from name, -1 if failure
def getSet(setName):
    with open("cache/groups.json") as file:
        file = json.load(file)
        
        for set in file["results"]:
            if set['name'] == setName:
                return set['groupId']
        
    
    return -1


@app.route("/test")
def hello_world():
    return "Hello, World!"


# Returns Card imageUrl and Price given setName and cardName
@app.route("/<path:setName>/<path:cardName>")        
def getCardInfo(setName, cardName):
    groupId = getSet(setName)
    
    if groupId == -1:
        return -1
    
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
        return -1
    
    with open(f"cache/ProductsandPrices/{groupId}_Prices.json") as file:
            file = json.load(file)
            
            for card in file["results"]:
                if card['productId'] == cardId:
                    price = card['marketPrice']
    
    return f"{imageUrl} {str(price)}"
    
                
        
        

    




def main():
    print(getCardInfo("ME05: Pitch Black","Mega Darkrai ex - 116/084"))


if __name__ == "__main__":
    main()