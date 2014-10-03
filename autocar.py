#!/usr/bin/en python

#need to finish accel routines
#need to set up and down states for wing and top so you cant assert down when its already down


import Adafruit_BBIO.GPIO as GPIO
from time import sleep
import time
import smbus
import math
#from threading import Thread

############ --- Global Variables --- ############
top_going_up = 0
top_going_down = 0
wing_going_up = 0
wing_going_down = 0
top_statii = 1 #planning for top to normally be up
wing_statii = 0 #planning for wing to normally be down


short_flag = 0
long_flag = 0
wing_status = 0 #default to down position
accel_wing_up = 0
i = 0
j = 0



############ --- Event Handlers --- ############

def button_functions():
	global top_going_up
	global top_statii
	#while True:
	if(GPIO.input("P8_35") and top_going_up == 0 and top_statii == 1):
		top_down_buttonEventHandler()#can only do this because top_down_eventhandler isnt actually an event handler now
	if(GPIO.input("P8_33")):
		top_up_buttonEventHandler()#using interrupts for these for now
	if(GPIO.input("P8_12")):
		wing_up_buttonEventHandler()
	if(GPIO.input("P8_11")):
		wing_down_buttonEventHandler()


#####################################
def top_down_buttonEventHandler():
	global top_going_down
	global top_statii
	top_statii = 0
	top_going_down = 1 #protect against contention
	print 'putting top down'

	t1 = time.time()
	service_flag = 0
	while(time.time() < t1+15):
		
		if(GPIO.input("P8_35") & (time.time() > t1+0.5) & (time.time() < t1+5)):#second button press for service mode within 5 secs
			#print("entering service mode")
			service_flag = 1
			while(time.time() < t1+7):#enough time to put top to adequate service position
				
				if(GPIO.input("P8_35")):#manual control of top down
					GPIO.output("P8_27", True)
					GPIO.output("P8_43", True) # turn on top down LED
				elif(GPIO.input("P8_33")):#manual control of top up
					GPIO.output("P8_28", True)
					GPIO.output("P8_43", True) # turn on top down LED
				else:
					GPIO.output("P8_27", False)
					GPIO.output("P8_28", False)
					GPIO.output("P8_43", False) # turn on top down LED
			GPIO.output("P8_27", False)#make sure top controls stay un-asserted when exiting the service loop
			GPIO.output("P8_28", False)
			GPIO.output("P8_43", False) # turn on top down LED
			top_statii = 1

		elif(service_flag == 0):
			GPIO.output("P8_27", True)#continue with top auto-down
			GPIO.output("P8_42", True)# turn on top/wing status LED
			GPIO.output("P8_43", True) # turn on top down LED

		else:
			GPIO.output("P8_27", False)
			GPIO.output("P8_27", False)
			GPIO.output("P8_42", False)# turn on top/wing status LED
			GPIO.output("P8_43", False) # turn on top down LED

	GPIO.output("P8_27", False)#un-assert signal after ~15 secs
	GPIO.output("P8_28", False)#just in case
	top_going_down = 0
	GPIO.output("P8_42", False)# turn off top/wing status LED

def top_up_buttonEventHandler():
	global top_statii
	if(top_going_down == 0 and top_statii == 0): #if top is NOT going down, execute top up procedeure
		
		top_statii = 1	
		print("putting top up")
		GPIO.output("P8_42", True)# turn on top/wing status LED

		global top_going_up #protect against contention
		top_going_up = 1


		#assert top up signal
		GPIO.output("P8_28", True)

		sleep(15)

		#unassert top up signal
		GPIO.output("P8_28", False) 
		top_going_up = 0 #protect against contention
		GPIO.output("P8_42", False)# turn off top/wing status LED
		GPIO.output("P8_43", False) # turn off top down LED

######################################

######################################
def wing_up_buttonEventHandler():
	global wing_statii
	if(wing_going_down == 0 and wing_statii == 0): #if wing is NOT going down, execute wing up procedeure
		wing_statii = 1		
		print("putting event wing up")
		global wing_status
		wing_status = 1 # wing is up manually, ignore accel input

		global wing_going_up #protect against contention
		wing_going_up = 1

		GPIO.output("P8_42", True) # turn on wing/top status LED
		GPIO.output("P8_44", True) # turn on wing up LED

			
	
		#assert wing up signal
		GPIO.output("P8_30", True)

		#pause for wing down operation
		sleep(5)

		#unassert wing up signal
		GPIO.output("P8_30", False)
		wing_going_up = 0 #protect against contention
		GPIO.output("P8_42", False) #turn off wing/top status LED

def wing_down_buttonEventHandler():
	global wing_statii
	if(wing_going_up == 0 and wing_statii == 1): #if wing is NOT going up, execute wing down procedeure
		wing_statii = 0		
		print("puting event wing down")
		global wing_status
		global short_flag
		global long_flag
		wing_status = 0 # wing is down manually, able to be put up by accel again
		short_flag = 0 #if wing was accel'd up and I want to manual down, ignore timer flags to put it down
		long_flag = 0 #if wing was accel'd up and I want to manual down, set timer flags low

		global wing_going_down #protect against contention
		wing_going_down = 1

		GPIO.output("P8_42", True) # turn on wing/top status LED		

		

		#assert wing up signal
		GPIO.output("P8_29", True)

		#pause for wing down operation	
		sleep(5)

		#unassert wing up signal
		GPIO.output("P8_29", False)
		wing_going_down = 0 #protect against contention
		GPIO.output("P8_42", False) # turn on wing/top status LED
		GPIO.output("P8_44", False) # turn on wing/top status LED

#######################################
	
############ --- Dumb wing functions bc cant use event handler functions --- ############

def wing_up():
	global wing_status
	if((wing_going_down == 0)): #if wing is NOT going down, execute wing up procedeure
		print("putting wing up")
		global accel_wing_up
		
		accel_wing_up = 1 #wing has been put up as a result of acceleration, useful for wing_down fn
		GPIO.output("P8_42", True) # turn on wing/top status LED
		GPIO.output("P8_44", True) # turn on wing up LED

		#global wing_going_up #protect against contention
		wing_going_up = 1	
	
		#assert wing up signal
		GPIO.output("P8_30", True)

		#pause for wing down operation
		sleep(5)

		#unassert wing up signal
		GPIO.output("P8_30", False)
		wing_going_up = 0 #protect against contention
		GPIO.output("P8_42", False) #turn off wing/top status LED
		

def wing_down():
	global accel_wing_up
	if((wing_going_up == 0) and (accel_wing_up == 1)): #if wing is NOT going up, execute wing down procedeure
		print("puting wing down")
		GPIO.output("P8_42", True) # turn on wing/top status LED
		accel_wing_up = 0

		#global wing_going_down #protect against contention
		wing_going_down = 1

		#assert wing up signal
		GPIO.output("P8_29", True)

		#pause for wing down operation	
		sleep(5)

		#unassert wing up signal
		GPIO.output("P8_29", False)
		wing_going_down = 0 #protect against contention
		GPIO.output("P8_42", False) # turn on wing/top status LED
		GPIO.output("P8_44", False) # turn on wing/top status LED

############ --- Other LED functions --- ############
	
def other_LED():
	if(GPIO.input("P9_14")):#if low speed fan on
		GPIO.output("P9_11", True)#turn on low speed fan LED
	else:
		GPIO.output("P9_11", False)
	

	if(GPIO.input("P9_15")):#if high speed fan on
		GPIO.output("P9_12", True)#turn on high speed fan LED
	else:
		GPIO.output("P9_12", False)


	if(GPIO.input("P9_16")):#if wing speed status is high
		GPIO.output("P9_13", True)#turn on wing_speed status LED
	else:
		GPIO.output("P9_13", False)		
		
############ --- Ultrasonic functions --- ############


def get_dist_left():
	err_flag = 0
	t1 = 0
	t2 = 0

	GPIO.output("P8_8", True)
	time.sleep(0.00001)#10us pulse
	GPIO.output("P8_8", False)
	timer1 = time.time()

	while(GPIO.input("P8_9") == 0): #wait here while sensor isnt sending data back
		if(time.time() < timer1 + 0.0005):				
			t1 = time.time()
		else:
			err_flag = 1			
			break
			

	while(GPIO.input("P8_9") == 1): #wait here while distance response is happening
		if(err_flag == 1):
			break
		else:
			t2 = time.time()

		
	signal_time = t2-t1
	distance_left = abs(signal_time * 17000)#calc object distance
	if(distance_left < 600):
		#print distance_left #debug pring
		dist_leds_left(distance_left)#light up LEDs accordingly
		time.sleep(.005)#so the sensor doesnt brick				
	#else:
		#print 'oh shit L'

def get_dist_right():
	err_flag2 = 0
	t1 = 0
	t2 = 0

	GPIO.output("P8_7", True)
	time.sleep(0.00001)#10us pulse
	GPIO.output("P8_7", False)
	timer2 = time.time()

	while(GPIO.input("P8_10") == 0): #wait here while sensor isnt sending data back
		if(time.time() < timer2 + 0.0005):		
			#print 'dammit stuck'		
			t1 = time.time()
		else:
			err_flag2 = 1
			break
	while(GPIO.input("P8_10") == 1): #wait here while distance response is happening
		if(err_flag2 == 1):
			break
		else:
			t2 = time.time()

	signal_time = t2-t1
	distance_right = abs(signal_time * 17000)#calc object distance
	
	if(distance_right < 600):
		#print distance_right #debug print
		dist_leds_right(distance_right)#light up LEDs accordingly
		time.sleep(.005)#so the sensor doesnt brick				
	#else:
		#print 'oh shit R'


def dist_leds_left(distance):
	global i
	if(distance > 3 and distance < 260):

		GPIO.output("P8_45", True)	

	else:
		i+=1		
		if(i > 10):
			GPIO.output("P8_45", False)
			i = 0

def dist_leds_right(distance):
	global j
	if(distance > 3 and distance < 260):

		GPIO.output("P8_46", True)	

	else:
		j+=1		
		if(j > 10):
			GPIO.output("P8_46", False)
			j = 0
	

############ --- Accel/gyro functions --- ##########


def read_byte(adr):
	return bus.read_byte_data(address, adr)

def read_word(adr):
	high = bus.read_byte_data(address, adr)
	low = bus.read_byte_data(address, adr+1)
	val = (high << 8) + low
	return val

def read_word_2c(adr):
	val = read_word(adr)
	if (val >= 0x8000):
		return -((65535 - val) + 1)
	else:
		return val

def dist(a,b):
	return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
	radians = math.atan2(x, dist(y,z))
	return -math.degrees(radians)

def get_x_rotation(x,y,z):
	radians = math.atan2(y, dist(x,z))
	return math.degrees(radians)



#def tmp():
#	accel_yout = read_word_2c(0x3d)
#	accel_yout_scaled = abs(accel_yout / 16384.0)

#	if(accel_yout_scaled > 0.3):
#		thread = Thread(target = get_accel)
#    		thread.start()	
#		thread.join()

def get_accel():
	global wing_status
	if(wing_status == 0):
		global short_flag, long_flag
		global timer2, timer3
		accel_yout = read_word_2c(0x3d)
		accel_yout_scaled = abs(accel_yout / 16384.0)
		#print "Accel:", accel_yout_scaled #runningAvg

		if (accel_yout_scaled > 0.5):
			timer1 = time.time()
			while (accel_yout_scaled > 0.3):
				if(short_flag):
					if ((time.time() > timer1 + 4)):# and (time.time() < timer1 + 8)):#this, unfortunately, only happens after 0.7 second + wing_up routine time = 4.7 secs
						long_flag = 1
						print 'long flag set'
						timer3 = time.time()
						break
					#else:
					#	continue
				
				elif(not short_flag and not long_flag):
				
				
					if ((time.time() > timer1 + 0.7) and (time.time() < timer1 + 3)):#acceleration has lasted between 0.7 and 3 seconds
						wing_up()#maybe take this out of here to be able to accurately measure long wing up times, put this all on a non blocking thread?
						
						short_flag = 1
						print 'short flag set'
						timer2 = time.time()
						#print timer2
					
				
				accel_yout = read_word_2c(0x3d)
				accel_yout_scaled = abs(accel_yout / 16384.0)
				#GPIO.output("P8_30", False)

			#GPIO.output("P8_30", False)
		elif(short_flag):
		
			if(not long_flag and time.time() > (timer2 + 60)): #if 60 seconds has elapsed since short wing up routine					
				wing_down()
				short_flag = 0
			elif(long_flag and time.time() > (timer3 + 600)):#if 10 minutes have elapsed since long wing up routine
				wing_down()
				short_flag = 0
				long_flag = 0


############ --- Accel/gyro setup--- ############
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c
bus = smbus.SMBus(1)
address = 0x68
# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)



############ --- Main --- ############

def main():


	############ --- GPIO inputs --- ############
	GPIO.setup("P8_35", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #top_down_button
	GPIO.setup("P8_12", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #wing_up_button
	GPIO.setup("P8_33", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #top_up_button 
	GPIO.setup("P8_11", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #wing_down_button
	GPIO.setup("P8_9", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #distance sensor 1 input/echo
	GPIO.setup("P8_10", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #distance sensor 2 input/echo
	GPIO.setup("P9_14", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #low speed fan indicator input
	GPIO.setup("P9_15", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #high speed fan indicator input
	GPIO.setup("P9_16", GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #wing_speed indicator input


	############ --- GPIO Outputs --- ############
	GPIO.setup("P8_30", GPIO.OUT, False) #wing up relay, active high
	GPIO.setup("P8_29", GPIO.OUT, False) #wing down relay, active high
	GPIO.setup("P8_8", GPIO.OUT, False) #distance sensor L trigger
	GPIO.setup("P8_7", GPIO.OUT, False) #distance sensor R trigger
	GPIO.setup("P8_27", GPIO.OUT, False) #top down relay, active high
	GPIO.setup("P8_28", GPIO.OUT, False) #top up relay, active high
	


	#### --- LEDs for display --- ####
	GPIO.setup("P8_45", GPIO.OUT, False)#distance sensor left <10 cm
	GPIO.setup("P8_46", GPIO.OUT, False)#distance sensor right <10 cm
	GPIO.setup("P8_42", GPIO.OUT, False)#top/wing movement indicator
	GPIO.setup("P8_43", GPIO.OUT, False)#top indicator	
	GPIO.setup("P8_44", GPIO.OUT, False)#wing indicator
	GPIO.setup("P9_11", GPIO.OUT, False)#low speed fan LED
	GPIO.setup("P9_12", GPIO.OUT, False)#high speed fan LED
	GPIO.setup("P9_13", GPIO.OUT, False)#wing_speed LED

	#######################################################

	#detect top down button pushed and go to handler
	#GPIO.add_event_detect("P8_35", GPIO.RISING, callback=top_down_buttonEventHandler, bouncetime=500)#cant use callback for this, need while loop for service position and callbacks dont like while loops


	#detect top up button pushed and go to handler
	#GPIO.add_event_detect("P8_33", GPIO.RISING, callback=top_up_buttonEventHandler, bouncetime=300)
	
	#######################################################

	#detect wing up button pushed and go to handler
	#GPIO.add_event_detect("P8_12", GPIO.RISING, callback=wing_up_buttonEventHandler, bouncetime=300)


	#detect wing down button pushed and go to handler
	#GPIO.add_event_detect("P8_11", GPIO.RISING, callback=wing_down_buttonEventHandler, bouncetime=300)

	#######################################################

	#turn off signal assertions
	GPIO.output("P8_27", False)
	GPIO.output("P8_30", False)
	GPIO.output("P8_28", False)
	GPIO.output("P8_29", False)
	GPIO.output("P8_8", False)
	GPIO.output("P8_7", False)




	#######################################################


	############ --- button function thread --- ############

	#mythread = threading.Thread(target=button_functions).start()#start distance gathering on its own thread
	
	while(1):
		button_functions()
		get_accel()
		

        #get_dist_right()
		#get_dist_left()

	GPIO.cleanup()
	

if __name__=="__main__":
	main()
