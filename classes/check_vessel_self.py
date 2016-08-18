#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2015 by sailoog <https://github.com/sailoog/openplotter>
#
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
import os, subprocess, requests, time
from paths import Paths

paths=Paths()
home=paths.home
file=paths.file
currentpath=paths.currentpath

class checkVesselSelf:

	def __init__(self):

		if not self.util_process_exist('node'):
			print 'Signal K starting'
			if file!='1w_d.py':subprocess.call(['pkill', '-f', '1w_d.py'])
			if file!='i2c_d.py':subprocess.call(['pkill', '-f', 'i2c_d.py'])
			if file!='mqtt_d.py':subprocess.call(['pkill', '-f', 'mqtt_d.py'])
			if file!='SK-base_d.py':subprocess.call(['pkill', '-f', 'SK-base_d.py'])
			if file!='N2K-server_d.py':subprocess.call(['pkill', '-f', 'N2K-server_d.py'])
			subprocess.Popen(home+'/.config/signalk-server-node/bin/openplotter', cwd=home+'/.config/signalk-server-node')
			time.sleep(5)
			if file!='1w_d.py':subprocess.Popen(['python',currentpath+'/1w_d.py'])
			if file!='mqtt_d.py':subprocess.Popen(['python',currentpath+'/mqtt_d.py'])
			if file!='SK-base_d.py':subprocess.Popen(['python',currentpath+'/SK-base_d.py'])
			if file!='i2c_d.py':subprocess.Popen(['python',currentpath+'/i2c_d.py'], cwd=currentpath+'/imu') 
			if file!='N2K-server_d.py':subprocess.Popen(['python',currentpath+'/N2K-server_d.py'])
			subprocess.Popen('keyword')

		response = requests.get('http://localhost:3000/signalk/v1/api/vessels/self')
		data = response.json()
		self.uuid=data['uuid']
		if 'mmsi' in self.uuid:
			sp=self.uuid.split(':')
			self.mmsi=sp[len(sp)-1]
		else:
			try:
				self.mmsi=data['mmsi']
			except:
				self.mmsi='0000'
				print 'Error: No mmsi! mmsi has to be set'

	def util_process_exist(self,process_name):		
		pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]
		exist=False
		for pid in pids:
			try:
				if process_name in open(os.path.join('/proc', pid, 'cmdline'), 'rb').read():
					exist=True
			except IOError: # proc has already terminated
				continue
		return exist
