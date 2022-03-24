import threading
import time
import re
import requests
import xmltodict, json
import urllib
import mysql.connector
from mysql.connector import Error
import random
import time
from pygame import mixer

def play(soundfile, duration_secs):

    mixer.init()
    mixer.music.load(soundfile)
    mixer.music.play()
    time.sleep(duration_secs)
    mixer.music.stop()
    mixer.quit()

def receivemessage():
        
	while True:
		#ReceiveMsgRequest
		try:
                        
			URL = "http://192.168.2.1:81/recvmsg?user=admin&passwd=admin&count=1"
			r = requests.get(url = URL)
			obj = xmltodict.parse(r.content)
			data = json.dumps(obj)

                        
			print(data)
			print("Unread_Available: " + obj["Response"]["Unread_Available"])
			
			if obj["Response"]["Unread_Available"] != "0" :
				print("SenderNumber: " + obj["Response"]["MessageNotification"]["SenderNumber"])
				msg = obj["Response"]["MessageNotification"]["Message"].encode("ISO-8859-1").decode()
				val = str(msg.replace('%2C',','))
				val1 = val.replace("%40","@")
				print(val1)
				res = re.split('@',val1)
				coords =("["+res[1]+"]")
				emergency_type = (res[2])
				user_id = (res[3])
				print(coords)
				print(emergency_type)
				submit_report = "http://vigilante.londonfoster.org/submit_report.php?emergency_type="+emergency_type+"&coords="+coords+"&user_id="+user_id+"&connection_type=1"
				submit = requests.post(url = submit_report)

				sender = obj["Response"]["MessageNotification"]["SenderNumber"]
				num = sender.replace("+63","0") #Sender number
				sendUrl = "http://192.168.2.1:81/sendmsg?user=admin&passwd=admin&cat=1&to="+num+"&text=Your report has been successfully reported, wait for further instructions and stay calm. You can also call us at 09488340370."
				s = requests.get(url = sendUrl)
				play('asd.mp3', 5)
				print("--------------------------")
				
                                
		except:
			print("An exception occurred")
		

		time.sleep(5)
def validationsend():
	while True:
		try:
			connection = mysql.connector.connect(host='18.139.15.242',
												 database='vigilante',
												 user='',
												 password='')
			if connection.is_connected():
				db_Info = connection.get_server_info()
				print("Connected to MySQL Server version ", db_Info)
				cursor = connection.cursor()
				cursor.execute("select database();")
				record = cursor.fetchone()
				print("You're connected to database: ", record)

				Select_Query = "SELECT * FROM user where verified=0 and verificationCode is null;"
				
				result = cursor.execute(Select_Query)
				records = cursor.fetchall()
				
				for r in records:
					id = r[0]
					phone= r[9]
					otp = random.randint(1111,9999)
					sendUrl = "http://192.168.2.1:81/sendmsg?user=admin&passwd=admin&cat=1&to="+(phone)+"&text=Vigilante Verification Code: "+str(otp)+". Use this code to verify your Vigilante Account."
					s = requests.get(url = sendUrl)
					cursor = connection.cursor()
					Update_Query = " UPDATE user SET verificationCode = '"+str(otp)+ "' WHERE id="+str(id)
					
					cursor.execute(Update_Query)
					connection.commit()
					time.sleep(5)
					
		except Error as e:
			print("Error while connecting to MySQL", e)
		finally:
			if connection.is_connected():
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
				print("--------------------------")
		time.sleep(5)

def checkonline():
	while True:
		try:
			connection = mysql.connector.connect(host='18.139.15.242',
												 database='vigilante',
												 user='',
												 password='')
			if connection.is_connected():
				db_Info = connection.get_server_info()
				cursor = connection.cursor()
				cursor.execute("select database();")
				record = cursor.fetchone()

				Select_Query = "SELECT id,contactNumber FROM report LEFT JOIN user ON user.id = report.userId WHERE report.status = 0 AND report.texted is null"
				
				result = cursor.execute(Select_Query)
				records = cursor.fetchall()
				
				for r in records:
					id = r[0]
					phone= r[1]
					sendUrl = "http://192.168.2.1:81/sendmsg?user=admin&passwd=admin&cat=1&to="+(phone)+"&text=Your report has been successfully reported, wait for further instructions and stay calm. You can also call us at 09488340370."
					s = requests.get(url = sendUrl)
					cursor = connection.cursor()
					Update_Query = " UPDATE report SET texted = 1 WHERE userId="+str(id)
					
					cursor.execute(Update_Query)
					connection.commit()
					time.sleep(5)
					play('asd.mp3', 5)
					
		except Error as e:
			print("Error while connecting to MySQL", e)
		finally:
			if connection.is_connected():
				cursor.close()
				connection.close()
				print("MySQL connection is closed")
				print("--------------------------")
		time.sleep(5)
			
if __name__ == "__main__":
    # creating thread
    t1 = threading.Thread(target=receivemessage, args=())
    t2 = threading.Thread(target=validationsend, args=())
    t3 = threading.Thread(target=checkonline,args=())
  
    # starting thread 1
    t1.start()
    #starting thread 2
    t2.start()
     #starting thread 3
    t3.start()
	
	 # wait until all threads finish
    t1.join()
    t2.join()
    t3.join()
