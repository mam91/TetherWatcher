import smtplib
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
from enum import Enum
import json

class State(Enum):
	BUY = 0
	HOLD = 1
	SELL = 2
	
def loadConfig():
	config = open('cmc-tether.config')
	data = json.load(config)
	return data
	
def getBuyThreshold(maxTetherPrice):
	return maxTetherPrice - 0.035
	
config = loadConfig()
maxTetherPrice = 0
sellThreshold = float(config[0]["sell_threshold"])
buyThreshold = getBuyThreshold(sellThreshold)

def sendEmail(toaddrs, subject, body):
	username = config[0]["email_username"]
	password = config[0]["email_token"]
	fromaddr = config[0]["email_from"]
	msg = MIMEMultipart('alternative')
	msg['From'] = config[0]["email_from"]
	msg['To'] = toaddrs
	msg['Subject'] = subject
	
	text = MIMEText(body, 'plain')
	msg.attach(text)

	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddr, toaddrs, msg.as_string())
	server.quit()
	
def Alert(currentPrice, currentState):
	sendEmail(config[0]["email_to"], 'Coin Marketcap - Tether (USD): ' + str(currentPrice), 'State: ' + currentState.name)
	

def getStateChange(tetherPrice, state):
	global sellThreshold, buyThreshold, maxTetherPrice
	
	if(tetherPrice > sellThreshold and tetherPrice > maxTetherPrice):
		maxTetherPrice = tetherPrice
		buyThreshold = getBuyThreshold(maxTetherPrice)
		
	if(tetherPrice > sellThreshold and state != State.SELL):
		return State.SELL
		
	if(tetherPrice < buyThreshold and state == State.SELL):
		return State.BUY
		
	if(tetherPrice > buyThreshold and tetherPrice < sellThreshold and state == State.BUY):
		buyThreshold = getBuyThreshold(sellThreshold)
		maxTetherPrice = 0
		return State.HOLD
		
	return state
	
def main():
	state = State.HOLD

	while True:
		response = requests.get(config[0]["cmc_tether_endpoint"]).json()
		print(response)
		tetherPrice = float(response[0]["price_usd"])
			
		print("Current tether price: " + str(tetherPrice) + " Current state: " + state.name)
		
		newState = getStateChange(tetherPrice, state)
		
		if(newState != state):
			print("State changed from " + state.name + " to " + newState.name)
			state = newState
			Alert(tetherPrice, state)
		
		print("Sleeping for 60 seconds...")
		time.sleep(60)
main()



