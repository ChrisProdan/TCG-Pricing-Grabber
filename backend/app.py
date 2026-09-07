import os
from flask import Flask
from flask_cors import CORS
from flask import jsonify 
import psycopg

from dotenv import load_dotenv

load_dotenv()
password = os.environ.get("DB_PASSWORD")

app = Flask(__name__)
CORS(app)

# Returns set ID from name, -1 if failure
def getSet(setName):
    
    with psycopg.connect(dbname="Pokemon_Pricing_Information",
                                         user="postgres",
                                         password=password,
                                         port=5432,
                                         host="localhost",
                                         autocommit=True) as conn:
                        
                with conn.cursor() as cur:
                    try:
                        cur.execute(
                            t"SELECT groupid FROM groupdata WHERE setname={setName}"
                        )
                        
                        retval = cur.fetchone()
                        if retval is None:
                            return -1
                        return retval[0]
                        
                    except psycopg.Error as e:
                        return -1

# Returns Card imageUrl and Price given setName and cardName
@app.route("/<path:setName>/<path:cardName>")        
def getCardInfo(setName, cardName):
    groupId = getSet(setName)
    
    if groupId == -1:
        return jsonify({"error": "not found"}), 404
    
    with psycopg.connect(dbname="Pokemon_Pricing_Information",
                                             user="postgres",
                                             password=password,
                                             port=5432,
                                             host="localhost",
                                             autocommit=True) as conn:
                            
                    with conn.cursor() as cur:
                        try:
                            cur.execute(
                                t"SELECT imageurl, price FROM carddata WHERE groupid={groupId} AND cardname={cardName}"
                            )
                            
                            r = cur.fetchone()  
                            if r is None:
                                return jsonify({"error": "not found"}), 404                                                 
                            retval = jsonify({"imageUrl":r[0],"price":r[1]})
                            
                            return retval
                            
                        except psycopg.Error as e:
                            return jsonify({"error": "not found"}), 404
    
    

    


def main():
    return
    print(getCardInfo("ME05: Pitch Black","Mega Darkrai ex - 116/084"))


if __name__ == "__main__":
    main()