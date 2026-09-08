import os
from flask import Flask , jsonify
from flask_cors import CORS
import psycopg

import dp
import config

app = Flask(__name__)
CORS(app)

# Suggests a List of Sets Based on Partial String
@app.route("/suggest/sets/<path:setName>")
def SuggestSet(setName):
    if setName == "":
        return jsonify({"suggestions":[]})
    else:
        pattern = f"%{setName}%"
        with dp.get_connection(config.load_settings) as conn:

            with conn.cursor() as cur:
                try:
                    cur.execute(
                        t"SELECT setname FROM groupdata WHERE setname ILIKE {pattern} LIMIT 5"
                    )
                    return jsonify({"suggestions":[x[0] for x in cur.fetchall()]})
                except psycopg.Error as e:
                    return jsonify({"suggestions":[]})

    return

# Suggests a List of Cards Based on Partial String
@app.route("/suggest/card/<path:setName>/<path:cardName>")
def SuggestCard(setName,cardName):
    setId = dp.getSet(dp.get_connection(config.load_settings), setName)
    
    if setId == -1:
        return jsonify({"suggestions":[]})
    else:
        pattern = f"%{cardName}%"
        with dp.get_connection(config.load_settings) as conn:

            with conn.cursor() as cur:

                try:
                    cur.execute(
                        t"SELECT cardname FROM carddata WHERE groupid={setId} AND cardname ILIKE {pattern} LIMIT 5"
                    )
                    return jsonify({"suggestions":[x[0] for x in cur.fetchall()]})
                except psycopg.Error as e:
                    return jsonify({"suggestions":[]})


# Returns Card imageUrl and Price given setName and cardName
@app.route("/<path:setName>/<path:cardName>")        
def getCardInfo(setName, cardName):
    groupId = dp.getSet(dp.get_connection(config.load_settings), setName)
    
    if groupId == -1:
        return jsonify({"error": "not found"}), 404
    
    with dp.get_connection(config.load_settings) as conn:
                            
        with conn.cursor() as cur:
            try:
                cur.execute(
                    t"SELECT imageurl, price FROM carddata WHERE groupid={groupId} AND cardname={cardName}"
                )
                
                r = cur.fetchone()  
                if r is None:
                    return jsonify({"error": "not found"}), 404                                                 
                retval = jsonify({"imageUrl":r[0],"price":f"{r[1]:.2f}"})
                
                return retval
                
            except psycopg.Error as e:
                return jsonify({"error": "not found"}), 404
    
    

    


def main():
    return



if __name__ == "__main__":
    # Starts the server instantly when the script is run directly
    app.run(debug=True)