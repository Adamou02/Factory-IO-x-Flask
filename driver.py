#! python3

###########
# IMPORTS #
###########

from pyModbusTCP.client import ModbusClient
from time import sleep
from flask import Flask, render_template, request, jsonify
import threading
import os

#flask related
app = Flask(__name__)

#############
# VARIABLES #
#############

slaveAddress='127.0.0.1'
slavePort=502

modbus_lock = threading.Lock()

auto_detection_active = True
auto_detection_lock = threading.Lock()

at_exit=0           #input
vision_sensor=0     #input reg
entry_conveyor=0    #coil
exit_conveyor=2     #coil
bras_blue=3         #coil
roller_blue=4       #coil
bras_green=5        #coil
roller_green=6      #coil
bras_metal=7        #coil
roller_metal=8      #coil
emit=11             #coil
count_blue=0        #holding reg
count_green=1       #holding reg
count_grey=2        #holding reg

########
# CODE #
########

client = ModbusClient(slaveAddress,port=slavePort,unit_id=1)
client.open()

if client.is_open:
    strConStat = "Connecté"
    print("OK")
else:
    strConStat = "Pas Connecté"
    print("KO")

@app.route("/status")
def status():
    return f"Statut de connexion: {strConStat}"

@app.route("/get_counts")
def get_counts():
    with modbus_lock:
        try:
            blue_count = client.read_holding_registers(count_blue, 1)[0]
            green_count = client.read_holding_registers(count_green, 1)[0]
            grey_count = client.read_holding_registers(count_grey, 1)[0]
        except Exception as e:
            print(f"Erreur de lecture des compteurs: {e}")
            blue_count = green_count = grey_count = 0
    
    return jsonify({
        "blue": blue_count,
        "green": green_count,
        "grey": grey_count
    })

@app.route("/api/status")
def api_status():
    with modbus_lock:
        try:
            blue_count = client.read_holding_registers(count_blue, 1)[0]
            green_count = client.read_holding_registers(count_green, 1)[0]
            grey_count = client.read_holding_registers(count_grey, 1)[0]
        except Exception as e:
            print(f"Erreur de lecture des compteurs: {e}")
            blue_count = green_count = grey_count = 0
    
    return jsonify({
        "connection": strConStat,
        "counters": {
            "blue": blue_count,
            "green": green_count,
            "grey": grey_count
        },
        "auto_detection": auto_detection_active
    })

@app.route("/")
def index():
    """Affiche la page principale avec les boutons"""
    return render_template("index.html")

def webapp():
    app.run(debug=False, host='0.0.0.0', port=5000)

def roll_on():
    with modbus_lock:
        client.write_single_coil(entry_conveyor,1)
        client.write_single_coil(exit_conveyor,1)

def roll_off():
    with modbus_lock:
        client.write_single_coil(entry_conveyor,0)
        client.write_single_coil(exit_conveyor,0)

def init_state():
    with modbus_lock:
        client.write_single_coil(bras_green, 0)
        client.write_single_coil(roller_green, 0)
        client.write_single_coil(bras_blue, 0)
        client.write_single_coil(roller_blue, 0)
        client.write_single_coil(bras_metal, 0)
        client.write_single_coil(roller_metal, 0)
        for i in range(0,3):
            client.write_single_register(i,0)

def wait_for_laser():
    while True:
        with modbus_lock:
            if not client.read_discrete_inputs(at_exit, 1)[0]:
                break
        sleep(0.1)
    sleep(0.5)

def increment_counter(counter_addr):
    with modbus_lock:
        current_value = client.read_holding_registers(counter_addr, 1)[0]
        client.write_single_register(counter_addr, current_value + 1)

def metal_on():
    with modbus_lock:
        client.write_single_coil(emit,0)
        client.write_single_coil(bras_metal,1)
        client.write_single_coil(roller_metal,1)
    
    sleep(1)
    
    with modbus_lock:
        client.write_single_coil(entry_conveyor,0)
    
    increment_counter(count_grey)
    wait_for_laser()
    
    with modbus_lock:
        client.write_single_coil(emit,1)
        client.write_single_coil(entry_conveyor,1)
        client.write_single_coil(bras_metal,0)
        client.write_single_coil(roller_metal,0)

def blue_on():
    with modbus_lock:
        client.write_single_coil(emit,0)
        client.write_single_coil(bras_blue,1)
        client.write_single_coil(roller_blue,1)
    
    sleep(1)
    
    with modbus_lock:
        client.write_single_coil(entry_conveyor,0)
    
    increment_counter(count_blue)
    wait_for_laser()
    
    with modbus_lock:
        client.write_single_coil(emit,1)
        client.write_single_coil(entry_conveyor,1)
        client.write_single_coil(bras_blue,0)
        client.write_single_coil(roller_blue,0)

def green_on():
    with modbus_lock:
        client.write_single_coil(emit,0)
        client.write_single_coil(bras_green,1)
        client.write_single_coil(roller_green,1)
    
    sleep(1)
    
    with modbus_lock:
        client.write_single_coil(entry_conveyor,0)
    
    increment_counter(count_green)
    wait_for_laser()
    
    with modbus_lock:
        client.write_single_coil(emit,1)
        client.write_single_coil(entry_conveyor,1)
        client.write_single_coil(bras_green,0)
        client.write_single_coil(roller_green,0)

@app.route("/command", methods=["POST"])
def command():
    """Gère l'action déclenchée par un bouton"""
    global auto_detection_active
    action = request.json.get("action")
    print(f"Action reçue: {action}")

    if action == "toggle_auto":
        with auto_detection_lock:
            auto_detection_active = not auto_detection_active
        return jsonify({
            "status": "success", 
            "message": f"Détection automatique {'activée' if auto_detection_active else 'désactivée'}"
        })
    elif action == "blue_on":
        with auto_detection_lock:
            was_active = auto_detection_active
            auto_detection_active = False
        
        try:
            blue_on()
        finally:
            if was_active:
                with auto_detection_lock:
                    auto_detection_active = True
                    
    elif action == "green_on":
        with auto_detection_lock:
            was_active = auto_detection_active
            auto_detection_active = False
        
        try:
            green_on()
        finally:
            if was_active:
                with auto_detection_lock:
                    auto_detection_active = True
                    
    elif action == "metal_on":
        with auto_detection_lock:
            was_active = auto_detection_active
            auto_detection_active = False
        
        try:
            metal_on()
        finally:
            if was_active:
                with auto_detection_lock:
                    auto_detection_active = True
                    
    elif action == "roll_on":
        roll_on()
    elif action == "roll_off":
        roll_off()
    else:
        return jsonify({"status": "error", "message": "Action inconnue"}), 400
        
    return jsonify({"status": "success", "message": f"Commande '{action}' exécutée"})

def modbus_loop():
    print("Démarrage de la boucle Modbus...")
    init_state()
    roll_on()

    while True:
        with auto_detection_lock:
            is_active = auto_detection_active
            
        if is_active:
            try:
                with modbus_lock:
                    sensor_value = client.read_input_registers(vision_sensor, 1)[0]
                    
                if sensor_value in range(7, 10):
                    print("Metal detected.")
                    metal_on()
                elif sensor_value in range(1, 4):
                    print("Blue detected.")
                    blue_on()
                elif sensor_value in range(4, 7):
                    print("Green detected.")
                    green_on()
            except Exception as e:
                print(f"Erreur dans la boucle Modbus: {e}")
                sleep(1)
                
        sleep(0.1)


if __name__ == "__main__":
    modbus_thread = threading.Thread(target=modbus_loop, daemon=True)
    webapp_thread = threading.Thread(target=webapp)

    modbus_thread.start()
    webapp_thread.start()

    try:
        webapp_thread.join()
    except KeyboardInterrupt:
        print("Arrêt du programme")
    finally:
        print("Fermeture de la connexion Modbus")
        client.close()