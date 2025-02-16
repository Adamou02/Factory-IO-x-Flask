#! python3

###########
# IMPORTS #
###########

from pyModbusTCP.client import ModbusClient
from time import sleep
# from flask import Flask, render_template, request, jsonify
import threading

#flask related
# app = Flask(__name__)

# @app.route("/status")
# def status():
# 	strTmpStatus = "Statut de connexion: " + strConStat
# 	return strTmpStatus

# @app.route("/")
# def index():
#     """Affiche la page principale avec les boutons"""
#     return render_template("index.html")
	

#############
# VARIABLES #
#############

slaveAddress='127.0.0.1'
slavePort=502


at_exit=0		#input
vision_sensor=0		#input reg
entry_conveyor=0			#coil
exit_conveyor=2			#coil
bras_blue=3		#coil
roller_blue=4		#coil
bras_green=5		#coil
roller_green=6		#coil
bras_metal=7		#coil
roller_metal=8		#coil
emit=11			#coil
count_blue=0		#holding reg
count_green=1		#holding reg
count_grey=2		#holding reg

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

def webapp():
    if __name__ == "__main__":
	    app.run(debug=False)
	
def roll_on():
	client.write_single_coil(entry_conveyor,1)
	client.write_single_coil(exit_conveyor,1)

def roll_off():
	client.write_single_coil(entry_conveyor,0)
	client.write_single_coil(exit_conveyor,0)
	
def init_state():
    client.write_single_coil(bras_green, 0)
    client.write_single_coil(roller_green, 0)
    client.write_single_coil(bras_blue, 0)
    client.write_single_coil(roller_blue, 0)
    client.write_single_coil(bras_metal, 0)
    client.write_single_coil(roller_metal, 0)
    for i in range(0,3):
        client.write_single_register(i,0)
	
def wait_for_laser():
    while client.read_discrete_inputs(at_exit, 1)[0]:
        pass
    sleep(0.5)
	
def increment_counter(counter_addr):
    current_value = client.read_holding_registers(counter_addr, 1)[0]
    client.write_single_register(counter_addr, current_value + 1)

def metal_on():
	client.write_single_coil(emit,0)
	client.write_single_coil(bras_metal,1)
	client.write_single_coil(roller_metal,1)
	sleep(1)
	client.write_single_coil(entry_conveyor,0)
	increment_counter(count_grey)
	wait_for_laser()
	client.write_single_coil(emit,1)
	client.write_single_coil(entry_conveyor,1)
	client.write_single_coil(bras_metal,0)
	client.write_single_coil(roller_metal,0)

def blue_on():
	client.write_single_coil(emit,0)
	client.write_single_coil(bras_blue,1)
	client.write_single_coil(roller_blue,1)
	sleep(1)
	client.write_single_coil(entry_conveyor,0)
	increment_counter(count_blue)
	wait_for_laser()
	client.write_single_coil(emit,1)
	client.write_single_coil(entry_conveyor,1)
	client.write_single_coil(bras_blue,0)
	client.write_single_coil(roller_blue,0)

def green_on():
	client.write_single_coil(emit,0)
	client.write_single_coil(bras_green,1)
	client.write_single_coil(roller_green,1)
	sleep(1)
	client.write_single_coil(entry_conveyor,0)
	increment_counter(count_green)
	wait_for_laser()
	client.write_single_coil(emit,1)
	client.write_single_coil(entry_conveyor,1)
	client.write_single_coil(bras_green,0)
	client.write_single_coil(roller_green,0)

# @app.route("/command", methods=["POST"])
# def command():
#     """Gère l'action déclenchée par un bouton (sans logique pour l'instant)"""
#     action = request.json.get("action")
#     print(f"Action reçue: {action}")  # Juste pour afficher dans le terminal

#     if action == "blue_on":
#         blue_on()
#     elif action == "green_on":
#         green_on()
#     elif action == "metal_on":
#         metal_on()
#     elif action == "roll_on":
#         roll_on()
#     elif action == "roll_off":
#         roll_off()
#     else:
#         return jsonify({"status": "error", "message": "Action inconnue"}), 400
#     return jsonify({"status": "success", "message": f"Commande '{action}' reçue"})


init_state()
roll_on()

while 1:
	if client.read_input_registers(vision_sensor,1)[0] in range(7,10):
		print("Metal detected.")
		metal_on()
	if client.read_input_registers(vision_sensor,1)[0] in range(1,4):
		print("Blue detected.")
		blue_on()
	if client.read_input_registers(vision_sensor,1)[0] in range(4,7):
		print("Green detected.")
		green_on()


# # Démarrer la boucle Modbus dans un thread
# # modbus_thread = threading.Thread(target=modbus_loop, daemon=True)
# # webapp_thread = threading.Thread(target=webapp, daemon=True)

# # modbus_thread.start()
# # webapp_thread.start()


client.close()