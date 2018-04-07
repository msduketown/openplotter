#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
# 					  e-sailing <https://github.com/e-sailing/openplotter>
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys
import time
import fileinput
import string 
from classes.conf import Conf

if not os.path.isfile('/etc/hostapd/hostapd.conf'):
#if os.path.isfile('/etc/hostapd/hostapd.conf'):
	print 'no hostapd installed'
elif len(sys.argv) > 1:

	conf = Conf()

	change = False

	wifi_server = sys.argv[1]
	wlan = conf.get('WIFI', 'device')
	passw = conf.get('WIFI', 'password')
	ip = conf.get('WIFI', 'ip')
	ip_split = ip.split('.')
	if len(ip_split) == 4:
		ip3 = ip_split[0] + '.' + ip_split[1] + '.' + ip_split[2]
	else:
		print('wrong ip format in openplotter.conf switch to standard')
		ip = '10.10.10.1'
		ip3 = '10.10.10'

	ssid = conf.get('WIFI', 'ssid')
	hw_mode = conf.get('WIFI', 'hw_mode')
	channel = conf.get('WIFI', 'channel')
	wpa = conf.get('WIFI', 'wpa')
	share = conf.get('WIFI', 'share')
	bridge = conf.get('WIFI', 'bridge')


	driver = 'nl80211'
	error = 0

	if wifi_server == '1':
		wififile = open('/etc/default/hostapd', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		data = 'DAEMON_CONF="/etc/hostapd/hostapd.conf"'
		if bak != data:
			change = True
			wififile = open('/etc/default/hostapd', 'w')
			wififile.write(data)
			wififile.close()

		data = 'interface=' + wlan + '\n'
		if bridge == '1' and wifi_server == '1':    data += 'bridge=br0\n'
		data += 'hw_mode=' + hw_mode + '\n'
		data += 'channel=' + channel + '\n'
		data += 'ieee80211n=1\n'
		data += 'ht_capab=[HT40][SHORT-GI-20][DSSS_CCK-40]\n'
		data += 'macaddr_acl=0\n'
		data += 'wmm_enabled=1\n'
		data += 'ssid=' + ssid + '\n'
		data += 'auth_algs=1\n'
		data += 'wpa=' + wpa + '\n'
		data += 'wpa_key_mgmt=WPA-PSK\n'
		data += 'rsn_pairwise=CCMP\n'
		data += 'wpa_passphrase=' + passw + '\n'

		wififile = open('/etc/hostapd/hostapd.conf', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		if bak != data:
			change = True
			wififile = open('/etc/hostapd/hostapd.conf', 'w')
			wififile.write(data)
			wififile.close()

	lan = wlan
	if bridge == '1': lan = 'br0'

	data = ''
	if wifi_server == '1':
		if bridge == '0':
			data += '# generated by openplotter\n'
			data += 'source /etc/network/interfaces.d/*\n'
			data += 'auto lo\n'
			data += 'iface lo inet loopback\n'
			data += 'allow-hotplug eth0\n'
			data += 'iface eth0 inet dhcp\n'
			data += 'allow-hotplug usb0\n'
			data += 'iface usb0 inet static\n'
			data += 'address 192.168.42.100\n'
			data += 'netmask 255.255.255.0\n'

			data += 'allow-hotplug ' + wlan + '\n'
			data += 'auto ' + wlan + '\n'
			data += 'iface ' + wlan + ' inet static\n'
			data += 'address ' + ip + '\n'
			data += 'netmask 255.255.255.0\n'
			data += 'network ' + ip3 + '.0\n'
			data += 'broadcast ' + ip3 + '.255\n'
			if share != '0':
				data += 'post-up iptables -t nat -A POSTROUTING -o ' + share + ' -j MASQUERADE\n'
				data += 'post-up iptables -A FORWARD -i ' + share + ' -o ' + lan + ' -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
				data += 'post-up iptables -A FORWARD -i ' + lan + ' -o ' + share + ' -j ACCEPT\n'
			data += 'post-up systemctl daemon-reload\n'

		else:
			data += '# generated by openplotter\n'	
			data += 'source /etc/network/interfaces.d/*\n'
			data += 'auto lo\n'
			data += 'iface lo inet loopback\n'

			data += 'allow-hotplug usb0\n'
			data += 'iface usb0 inet static\n'
			data += 'address 192.168.42.100\n'

			data += 'auto eth0\n'
			data += 'iface eth0 inet manual\n'

			data += 'auto ' + wlan + '\n'
			data += 'iface ' + wlan + ' inet manual\n'
			
			data += 'auto br0\n'
			data += 'iface br0 inet static\n'
			data += 'bridge_ports eth0\n'
			#data += 'bridge_ports eth0 ' + wlan + '\n'
			data += 'address ' + ip + '\n'
			data += 'broadcast ' + ip3 + '.255\n'
			data += 'netmask 255.255.255.0\n'
			data += 'network ' + ip3 + '.0\n'
			data += 'bridge_maxwait 1\n'

			if share != '0':
				data += 'post-up iptables -t nat -A POSTROUTING -o ' + share + ' -j MASQUERADE\n'
				data += 'post-up iptables -A FORWARD -i ' + share + ' -o ' + lan + ' -m state --state RELATED,ESTABLISHED -j ACCEPT\n'
				data += 'post-up iptables -A FORWARD -i ' + lan + ' -o ' + share + ' -j ACCEPT\n'
			data += 'post-up systemctl daemon-reload\n'

		wififile = open('/etc/network/interfaces', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		if bak != data:
			change = True
			wififile = open('/etc/network/interfaces', 'w')
			wififile.write(data)
			wififile.close()
			
		dhcpcd='denyinterfaces '+ wlan
		if bridge == '1': dhcpcd+= ' eth0'
		dhcpcd_info = '  '
		try:
			dhcpcd_info = subprocess.check_output(('grep denyinterfaces /etc/dhcpcd.conf').split())
		except: pass
		
		if dhcpcd == dhcpcd_info[-1]:
			print dhcpcd,dhcpcd_info[-1]
			pass
		else:
			if 'denyinterfaces' in dhcpcd_info:
				for line in fileinput.input('/etc/dhcpcd.conf',inplace=1):
					lineno = 0
					lineno = string.find(line,'denyinterfaces')
					if lineno >= 0:
						if dhcpcd != line:
							line = dhcpcd
					sys.stdout.write(line)
			else:
				dhcpcdfile = open('/etc/dhcpcd.conf', 'r', 2000)
				bak = dhcpcdfile.read()
				dhcpcdfile.close()
				dhcpcdfile = open('/etc/dhcpcd.conf', 'w')
				dhcpcdfile.write(bak+dhcpcd)
				dhcpcdfile.close()		
			
		if bridge == '0':
			wlanx = 'wlan0'
			if wlan[-1:] == '0': wlanx = 'wlan1'
			data = 'no-dhcp-interface=lo,eth0,' + wlanx + ',usb0,ppp0\n'
			data += 'interface=' + wlan + '\n'
			data += 'dhcp-range=' + ip3 + '.20,' + ip3 + '.254,255.255.255.0,12h\n'
		else:
			data = 'no-dhcp-interface=lo,eth0,wlan0,wlan1,usb0,ppp0,wwan0\n'
			data += 'interface=br0\n'
			data += 'dhcp-range=' + ip3 + '.100,' + ip3 + '.200,255.255.255.0,12h\n'

		wififile = open('/etc/dnsmasq.conf', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		if bak != data:
			change = True
			wififile = open('/etc/dnsmasq.conf', 'w')
			wififile.write(data)
			wififile.close()

		data = 'ddns-update-style none;\n'
		data += 'default-lease-time 600;\n'
		data += 'max-lease-time 7200;\n'
		data += 'authoritative;\n'
		data += 'log-facility local7;\n'
		data += 'subnet ' + ip3 + '.0 netmask 255.255.255.0 {\n'
		data += 'range ' + ip3 + '.100 ' + ip3 + '.200;\n'
		data += 'option broadcast-address ' + ip3 + '.255;\n'
		data += 'option routers ' + ip3 + '.1;\n'
		data += 'option domain-name "local";\n'
		data += 'option domain-name-servers 8.8.8.8, 8.8.4.4;\n'

		if bridge == '0':
			data += 'interface ' + wlan + ';\n'
			data += '}\n'
		else:
			data += 'interface br0;\n'
			data += '}\n'

		wififile = open('/etc/dhcp/dhcpd.conf', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		if bak != data:
			change = True
			wififile = open('/etc/dhcp/dhcpd.conf', 'w')
			wififile.write(data)
			wififile.close()
		if change:
			output = subprocess.Popen('systemctl enable hostapd'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('systemctl enable dnsmasq'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
		
			output = subprocess.Popen('systemctl daemon-reload'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('service networking restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('service dnsmasq restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('service hostapd restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			i=0
			erg = ''
			while 'br0' not in erg and i<40:
				time.sleep(1)
				try:
					erg_ = subprocess.Popen('ifconfig',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
					erg = erg_.communicate()[0]
				except:
					pass
				i += 1
			time.sleep(1)
			output = subprocess.Popen('ifconfig eth0 down'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			i=0
			erg = 'eth0'
			while 'eth0' in erg and i<40:
				time.sleep(1)
				try:
					erg_ = subprocess.Popen('ifconfig',stdout=subprocess.PIPE,stderr=subprocess.PIPE)
					erg = erg_.communicate()[0]
				except:
					pass
				i += 1
			
			output = subprocess.Popen(('ifconfig '+wlan+' up').split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('ifconfig eth0 up'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			if bridge == '0':
				output = subprocess.Popen('service networking restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
				output.wait()
		msg1 = ''
		network_info = ''
		try:
			network_info = subprocess.check_output('service dnsmasq status'.split())
		except:
			pass
		if 'running' not in network_info:
			print 'failed service dnsmasq'
			error = 10

		msg1 = ''
		network_info = ''
		try:
			network_info = subprocess.check_output('service hostapd status'.split())
		except:
			pass
		if 'active' not in network_info: 
			print 'failed service hostapd'
			error = 11
			
		msg1 = ''
		network_info = ''
		try:
			network_info = subprocess.check_output('service networking status'.split())
		except:
			pass
		if 'active (' not in network_info: 
			print 'failed service networking'
			error = 12

		if error > 0:
			print "WiFi access point failed."
			print error
		else:
			print "WiFi access point started.\n"
			print "SSID: " + ssid
			print 'Address: ' + ip3 + '.1'
			if change:
				print 'It is recommended to restart the computer'

	else:
		wififile = open('/etc/network/interfaces', 'r', 2000)
		bak = wififile.read()
		wififile.close()
		if '# generated by openplotter\n' in bak:

			dhcpcd_info = subprocess.check_output(('grep denyinterfaces /etc/dhcpcd.conf').split())

			if 'denyinterfaces' in dhcpcd_info:
				for line in fileinput.input('/etc/dhcpcd.conf',inplace=1):
					lineno = 0
					lineno = string.find(line,'denyinterfaces')
					if lineno >= 0:
						pass
					else:
						sys.stdout.write(line)

			data = ''
			data += 'source /etc/network/interfaces.d/*\n'
			data += 'allow-hotplug usb0\n'
			data += 'iface usb0 inet static\n'
			data += 'address 192.168.42.100\n'
			data += 'netmask 255.255.255.0\n'
			wififile = open('/etc/network/interfaces', 'w')
			wififile.write(data)
			wififile.close()

			if 'br0' in subprocess.check_output('ifconfig'):
				output = subprocess.Popen('brctl delif br0 eth0'.split())
				output.wait()
				output = subprocess.Popen('ifconfig br0 down'.split())
				output.wait()
				output = subprocess.Popen('brctl delbr br0'.split())
				output.wait()

			output = subprocess.Popen('systemctl disable hostapd'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('systemctl disable dnsmasq'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()				
				
			output = subprocess.Popen('systemctl daemon-reload'.split())
			output.wait()
			output = subprocess.Popen('service dnsmasq stop'.split())
			output.wait()
			output = subprocess.Popen('service hostapd stop'.split())
			output.wait()
			output = subprocess.Popen('iptables -F'.split())
			output.wait()
			output = subprocess.Popen('service network-manager restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('service dhcpcd restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			output = subprocess.Popen('service networking restart'.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			output.wait()
			
			print "\nWiFi access point stopped."
			print 'It is recommended to restart the computer'

	data = ''

	wififile = open('/boot/config.txt', 'r')
	wififile.seek(0)
	for line in wififile:
		data0 = ''
		if '#' in line:
			data0 = line
		else:
			if 'device' in line:
				data0 = 'device=' + wlan + '\n'
			elif 'ssid' in line:
				data0 = 'ssid=' + ssid + '\n'
			elif 'pass' in line:
				data0 = 'pass=' + passw + '\n'
			elif 'hw_mode' in line:
				data0 = 'hw_mode=' + hw_mode + '\n'
			elif 'channel' in line:
				data0 = 'channel=' + channel + '\n'
			elif 'wpa' in line:
				data0 = 'wpa=' + wpa + '\n'
			elif 'share' in line:
				data0 = 'share=' + share + '\n'
			elif 'bridge' in line:
				data0 = 'bridge=' + bridge + '\n'
			elif 'ip' in line:
				data0 = 'ip=' + ip + '\n'

		if not data0: data0 = line
		data += data0
	wififile.close()

	wififile = open('/boot/config.txt', 'r', 2000)
	bak = wififile.read()
	wififile.close()

	if bak != data:
		wififile = open('/boot/config.txt', 'w')
		wififile.write(data)
		wififile.close()

else:
	print 'cmd parameter missing (for activate 1 for deactivating 0)'
