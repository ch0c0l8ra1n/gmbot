print('Initializing...')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import socket
import os
from _thread import *
import threading
import subprocess
from socket import error as socket_error

from selenium.webdriver.chrome.options import Options

global gmx,gmail,options

gmx = 'https://registrierung.gmx.net/User-Registration-Application/?is1Reg=true#.pc_page.homepage.index.loginbox_1.registrierung'
gmail = 'https://adwords.google.com/um/Welcome/Home?hl=de&sf=ms&clickid=sn-5r-ms-us-08292017#ma'

options = Options()
options.add_argument('--headless')
options.add_argument('--hide-scrollbars')
options.add_argument('--disable-gpu') 

def warmup(gmail_driver,gmx_driver):
	t1 = time.time()
	print('Warming Uppp')
	for i in range(3):
		try:
			print(i)
			gmail_driver.get(gmail)
			gmail_driver.find_element_by_tag_name('body').click()
			gmx_driver.get(gmx)
		except Exception as e:
			print (e)
			print('warmup failed')
	print('Warmup time: ',time.time()-t1)

def checkgmail(gmail_driver,keyw,clients):
	t1 = time.time()
	try:
		elem=gmail_driver.find_element_by_class_name('umUb-c')
	except:
		clients.send('\n\rgmail site changed')
		print('gmail site changed')
	elem.send_keys('\r'+keyw+'@gmx.de')
	gmail_driver.find_element_by_tag_name('body').click()
	time.sleep(1)
	try:
		t_gmail = gmail_driver.find_element_by_xpath("//*[contains(text(),'Als Nächstes melden Sie sich in Ihrem Google-Konto an, bevor Sie Ihr Verwaltungskonto erstellen.')]")
		#print('can make gmail mail')
		elem.clear()
		print('checkgmail time: ',time.time()-t1)
		return True
	except:
		elem.clear()
		print('checkgmail time: ',time.time()-t1)
		return False

def checkgdx(gmx_driver,keyw,clients):
	t1=time.time()
	gmx_driver.get(gmx)
	try:
		elem = gmx_driver.find_element_by_name('wishnamePanel:wishname:subForm:alias')
	except:
		print('gmx site changed')
		clients.send('\n\rgmx site changed'.encode())
	elem.send_keys(keyw)
	gmx_driver.find_element_by_id('checkAvailabilityBtn').click()
	try:
		t_gmx = gmx_driver.find_element_by_xpath("//*[contains(text(),'Der Wunschname mit der Endung gmx.de ist leider nicht verfügbar')]")
		print('checkgmx time: ',time.time()-t1)
		return False
	except Exception as e:
		print('checkgmx time: ',time.time()-t1)
		return True


def work(csocket):
	working = ''
	csocket.send('If you want to view saved names type 0 and if you want to send new keywords type 1:\n'.encode())
	if csocket.recv(1024).decode().strip('\n').strip('\r') == '0':
		f = open('emails.txt','r+')
		data = [x for x in f.read().split('\n') if x]
		if not data:
			csocket.send('\n\rNo saved emails\n'.encode())
		else:
			for e in data:
				csocket.send(str('\n\r'+e).encode())


	csocket.send('\rEnter your keywords: '.encode())
	stuff = ''
	while True:
		data = csocket.recv(1)
		if data.decode() == '\n' :
			break
		stuff+=data.decode()
	text = stuff
	keys = text.strip('\n').strip('\r').split(' ')
	keys = [key for key in keys if key]
	
	print(keys)

	if not keys:
		csocket.send('No keys provided, exiting...'.encode())
		csocket.close()
	csocket.send(str(keys).encode())

	csocket.send('\r\nEnter upper range: '.encode())
	stuff = ''
	while True:
		data = csocket.recv(1)
		if data.decode() == '\n' :
			break
		stuff+=data.decode()
	try:
		u_range = int(stuff)
	except:
		u_range = 50
		csocket.send('\n\rERROR using default value 50\n'.encode())

	gmx_driver = webdriver.Chrome(chrome_options=options)
	gmx_driver.implicitly_wait(5)
	gmail_driver = webdriver.Chrome(chrome_options=options)
	gmail_driver.implicitly_wait(30)
	gmail_driver.set_page_load_timeout(20)
	gmx_driver.set_page_load_timeout(20)

	csocket.send(str('\n\rInitializing scanner...\n').encode())

	
	try:
		warmup(gmail_driver,gmx_driver)
		gmail_driver.implicitly_wait(2)
		gmx_driver.implicitly_wait(2)
		print('starting scan')
		b=0
		for key in keys:
			print(key,'\n')
			csocket.send(str('\n\n\r'+key+'\n').encode())
			for i in range(u_range):
				try:
					t1=time.time()
					b+=1
					if (b%60)==57:
						csocket.send('\n\rRefreshing page\n'.encode())
						warmup(gmail_driver,gmx_driver)
					t1_key = str(key+str(i))
					if(checkgmail(gmail_driver,t1_key,csocket)):
						t2_key = str(key+str(i))
						if(checkgdx(gmx_driver,t2_key,csocket)):
							print('gmx checked')
							working += key+str(i)+' '
							log = open('emails.txt','a+')
							log.write(key+str(i)+'\n')
							log.close()
							csocket.send(str('\n\r!!!___'+key+str(i)+' can make in both website___!!!\n').encode())
						else:
							csocket.send(str('\n\r'+key+str(i)+' cant make in gdx').encode() )
					else:
						csocket.send(str('\n\r'+key+str(i)+' cant make in gmail').encode() )
					print(str(key+str(i)),time.time()-t1,'\n')
				except socket_error as e:
					print('0\n',e)
					gmail_driver.close()
					gmx_driver.close()
					csocket.close()
					return
				except Exception as e:
					print('1\n',e)
					gmail_driver.get(gmail)
					gmail_driver.find_element_by_tag_name('body').click()
					time.sleep(2)
					print('failes')
		result = subprocess.check_output('echo '+working+' | nc termbin.com 9999',shell=True)
		csocket.send(str('\n\rTask finished\n\r'+result.decode()).encode())
		print(address[0]+':'+str(address[1])+' has disconnected \n')
		gmail_driver.close()
		gmx_driver.close()
		csocket.close()

	except socket_error as e:
		print('2\n',e)
		gmail_driver.close()
		gmx_driver.close()
		csocket.close()
		return

	except Exception as e:
		print ('3\n',e)
		pass

os.system('fuser -k 1234/tcp')

socketServer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '46.101.204.68'
serverPort = 1234
socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
socketServer.bind((host,serverPort))
print("hosting at "+str(host) +":"+str(serverPort))
os.system('killall chrome')
socketServer.listen(5000)


while True:
	try:
		print("Listening...")  
		(csocket , address) = socketServer.accept()
		print(address[0]+':'+str(address[1])+' has connected.')
		threading.Thread(target=work,args=(csocket,)).start()
		#work(csocket)
	except Exception as e:
		print('4\n',e)
		pass




