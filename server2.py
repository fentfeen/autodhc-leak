from flask import Flask, request, jsonify
import requests
import logging
import json
from requests.exceptions import HTTPError
from datetime import datetime, timedelta
import time
# Disabling request prints
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)


def rbx_request(session, method, url, **kwargs):
    method = method.upper()
    response = session.request(method, url, **kwargs)
    if method in {"POST", "PUT", "PATCH", "DELETE"}:
        if "X-CSRF-Token" in response.headers:
            session.headers["X-CSRF-Token"] = response.headers["X-CSRF-Token"]
            if response.status_code == 403:  # Request failed, send it again
                response = session.request(method, url, **kwargs)
    return response

def unfriend():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        Roblox_Cookie = config['Roblox_Cookie']
        user_id = config['user_id']
        config_file.close()
    url = f"https://friends.roblox.com/v1/users/{user_id}/unfriend"
    print(url)
    headers = {
        '.ROBLOSECURITY': Roblox_Cookie,
    }
    try:
        response = requests.post(url, cookies=headers)
        if response.status_code != 403:
            print(f"Failed to accept unfriend. Status code: {response.status_code}")
            print(response.json())
            print(response.headers)
            print(response.request.headers)
            return "False"
    except HTTPError as err:
        print(f"HTTP Error: {err}")
        return "False"
    except Exception as e:
        print(f"Error: {e}")
        raise e
        return "False"
    cookies = {
        "x-csrf-token": response.headers["x-csrf-token"]
    }
    try:
        response = requests.post(url, cookies=headers, headers=cookies)
        if response.status_code != 200:
            print(f"Failed to accept friend request. Status code: {response.status_code}")
            return "False"
        else:
            print("Successfully unfriended")
            return "True"
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return "False"
    except Exception as e:
        print(f"Error: {e}")
        return "False"

def process_user_ids_from_file():
    try:
            unfriend()
            print("User IDs have been processed and removed from the file.")
    except FileNotFoundError:
        print("user_id.txt not found.")
    except Exception as e:
        print("Error processing user IDs:", e)


def ps():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        cookie1 = config["Roblox_Cookie"] 
        ps_id = config["server_id"]       
    
    url = "https://games.roblox.com/v1/vip-servers/{}".format(ps_id)
    print(url)
    headers = {
        '.ROBLOSECURITY': cookie1,
    }
    payload = {
        "newJoinCode": "true",
    }
    try:
        response = requests.patch(url, cookies=headers,json=payload)
        if response.status_code != 403:
            print(f"Failed to reset ps: {response.status_code}")
            print(response.json())
            print(response.headers)
            print(response.request.headers)
            return "False"
    except HTTPError as err:
        print(f"HTTP Error: {err}")
        return "False"
    except Exception as e:
        print(f"Error: {e}")
        raise e
        return "False"
    cookies = {
        "x-csrf-token": response.headers["x-csrf-token"]
    }
    try:
        response = requests.patch(url, cookies=headers, headers=cookies,json=payload)
        if response.status_code != 200:
            print(f"Failed to reset ps. Status code: {response.status_code}")
            return "False"
        else:
            print("Successfully reset ps")
            return "True"
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        return "False"
    except Exception as e:
        print(f"Error: {e}")
        return "False"


@app.route('/write-timer', methods=['POST'])
def write_timer():
    try:
        print('processing the finished order')
        data = request.json
        status = data.get('status')

        # Check if the status is "False"
        if status == "False":
            # Calculate future time (current time + 11 minutes)
            current_time = datetime.now()
            future_time = current_time + timedelta(minutes=6)

            # Convert future time to epoch time
            future_time_epoch = int(future_time.timestamp())

            # Format epoch time as Discord timestamp
            discord_timestamp = f"<t:{future_time_epoch}:R>"

            # Update the config file with the Discord timestamp
            with open('config.json', 'r+') as config_file:
                config = json.load(config_file)
                config["timer"] = discord_timestamp  # Corrected here
                config_file.seek(0)  # Move the file pointer to the beginning
                json.dump(config, config_file, indent=4)
                config_file.truncate()
            return jsonify({"success": True}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/123-123-false', methods=['POST'])
def write_pickingup_false():
    try:
        print('proccessing the finished order')
        data = request.json
        status = data.get('status')

        # Check if the status is "False"
        if status == "False":
            ps()
            process_user_ids_from_file() #unfriend

            with open('config.json', 'r+') as config_file:
                config = json.load(config_file)
                config["order_finished_tracker"] = "True"
                config_file.seek(0)  # Move the file pointer to the beginning
                json.dump(config, config_file, indent=4)
                config_file.truncate() 
                return jsonify({"success": True}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/write-pickingup', methods=['POST'])
def write_pickingup():
    try:
        print('Processing the picking up data')
        data = request.json

        # Check if data is empty
        if not data:
            return jsonify({"success": False, "error": "Received empty data"}), 400

        # Load the existing config
        with open('config.json', 'r+') as config_file:
            config = json.load(config_file)
            config_file.seek(0)

            # Merge new data with existing data
            player_data = config.get('player_data', [])
            
            # Create a dictionary from the list for easy lookup
            existing_data = {item['userId']: item for item in player_data}

            # Update or add new data
            for new_entry in data:
                user_id = new_entry['userId']
                if user_id in existing_data:
                    existing_data[user_id]['endCash'] = new_entry['endCash']
                else:
                    existing_data[user_id] = new_entry

            # Convert the dictionary back to a list
            config['player_data'] = list(existing_data.values())

            # Write the updated config back to the file
            json.dump(config, config_file, indent=4)
            config_file.truncate()

        return jsonify({"success": True}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"success": False, "error": str(e)}), 500




@app.route('/write-cash', methods=['POST'])
def write_amountleft():
    try:
        data = request.json
        cash = data.get('cash')


        with open('config.json', 'r+') as config_file:
            config = json.load(config_file)
            config["Alts_cash"] = "{}".format(cash)
            config_file.seek(0)  # Move the cursor to the beginning of the file
            json.dump(config, config_file, indent=4)  # Dump the updated config dictionary back to the file
            config_file.truncate() 

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route('/write-amountleft', methods=['POST'])
def write_cash():
    try:
        data = request.json
        total = data.get('total')
        limit = data.get('limit')
        alts = data.get('alts')

        with open('config.json', 'r+') as config_file:
            config = json.load(config_file)
            config["Amount_left"] = "{} {} {}".format(total, limit, alts)
            config_file.seek(0)  # Move the cursor to the beginning of the file
            json.dump(config, config_file, indent=4)  # Dump the updated config dictionary back to the file
            config_file.truncate()

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)
