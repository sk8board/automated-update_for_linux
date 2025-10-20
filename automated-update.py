#!/usr/bin/python3

import subprocess
import time


def main():
	
	global counter
	counter = 0
	while True:
		
		# 0 = internet connected
		if check_internet() == 0:
			
			# check if application manager apt-get is present
			subprocess.call(['echo', '***check for apt-get***'])
			if subprocess.call(['/usr/bin/apt-get', '--version'])  == 0:
						
				# 0 = update completed
				if process_apt_update() and process_apt_upgrade() and process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# server error, retry after delay	
				else:
					server_error()
				
			# check if application manager dnf is present
			subprocess.call(['echo', '***check for dnf***'])
			elif subprocess.call(['/usr/bin/dnf', '--version'])  == 0:	
				
				# 0 = update completed
				if process_dnf() and process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# server error, retry after delay	
				else:
					server_error()


			# check if application manager pacman is present
			subprocess.call(['echo', '***check for pacman***'])
			elif subprocess.call(['/usr/bin/pacman', '--version'])  == 0:	
				
				# 0 = update completed
				if process_pacman() and process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# server error, retry after delay	
				else:
					server_error()
			
			
		else:
			subprocess.call(['echo', '***not connected to internet, retry after delay***'])
			# retry internet connection after delay
			time.sleep(300)	
				

def check_internet():
	
	# check for a connection to internet, exit code 0 = connected
	if subprocess.call(['/usr/bin/ping', '-c', '1', 'www.ubuntu.com']) == 0:  				
		subprocess.call(['echo', '***connected to internet***'])
		return 0
		
	else:
		return 1


def server_error():
	
	global counter
	if counter > 2:
		subprocess.call(['echo', '***service failed due to server error***'])
		exit(1)
	counter += 1
	subprocess.call(['echo', '***server error, retry after delay***'])
	time.sleep(600)


def process_apt_update():
	
	# get exit code for 'apt-get update' to check if updates are available, 0 = no updates available
	subprocess.call(['echo', '***apt-get check available update***'])
	exit_code = subprocess.call(['/usr/bin/apt-get', 'update', '--assume-no'])	
	
	if exit_code == 0:
		subprocess.call(['echo', '***apt updates are not available at this time***'])
		return 0
			
	else:	
		# perform apt updates
		subprocess.call(['echo', '***apt-get update***'])
		subprocess.call(['/usr/bin/systemd-inhibit', '--why="Performing automatic updates"', '--who="Update Manager"', '--what=shutdown', '--mode=block', '/usr/bin/apt-get', 'update', '-y'])	# provide the exit code of apt-get update command
		subprocess.call(['echo', '***apt update has completed***'])
		return 1		


def process_apt_upgrade():
	
	# get exit code for 'apt-get dist-upgrade', check if upgrades are available, 0 = no updates available
	subprocess.call(['echo', '***apt-get check available dist-upgrade***'])
	exit_code = subprocess.call(['/usr/bin/apt-get', 'dist-upgrade', '--assume-no'])	
	
	if exit_code == 0:
		subprocess.call(['echo', '***apt dist-upgrades are not available at this time***'])
		return 0
		
	else:
		# remove unused apt apps
		subprocess.call(['echo', '***apt-get autoremove***'])
		subprocess.call(['apt-get', 'autoremove', '-y'])
		
		# perform apt upgrades
		subprocess.call(['echo', '***apt-get dist-upgrade***'])
		subprocess.call(['/usr/bin/systemd-inhibit', '--why="Performing automatic updates"', '--who="Update Manager"', '--what=shutdown', '--mode=block', '/usr/bin/apt-get', 'dist-upgrade', '-y'])	# provide the exit code of apt-get upgrade command
		subprocess.call(['echo', '***apt dist-upgrade has completed***'])
		return 1		


def process_dnf():
	
	# get exit code for 'dnf check-upgrade', check if upgrades are available, 0 = no updates available
	subprocess.call(['echo', '***dnf check available upgrades***'])
	exit_code = subprocess.call(['/usr/bin/dnf', 'check-upgrade'])	
	
	if exit_code == 0:
		subprocess.call(['echo', '***dnf upgrades are not available at this time***'])
		return 0
		
	else:
		# remove unused apt apps
		subprocess.call(['echo', '***dnf autoremove***'])
		subprocess.call(['dnf', 'autoremove', '-y'])
		
		# perform apt upgrades
		subprocess.call(['echo', '***dnf distro-sync***'])
		subprocess.call(['/usr/bin/systemd-inhibit', '--why="Performing automatic updates"', '--who="Update Manager"', '--what=shutdown', '--mode=block', '/usr/bin/dnf', 'distro-sync', '-y'])	# provide the exit code of apt-get upgrade command
		subprocess.call(['echo', '***dnf distro-sync has completed***'])
		return 1		


def process_pacman():
	
	# work in progress
	return 0


def process_flatpak():
	
	# check if flatpak is installed, if not installed, return 0
	if subprocess.call(['/usr/bin/flatpak', '--version']) != 0:
		subprocess.call(['echo', '***flatpak is not installed***'])
		return 0
	
	# get exit code for 'flatpak remote-ls --updates', check if updates are available, 0 = no updates available
	subprocess.call(['echo', '***flatpak remote-ls --updates***'])
	exit_code = subprocess.call(['/usr/bin/flatpak', 'remote-ls', '--updates'])	
	
	# NEED TO FIX exit code always returns zero
	
	if exit_code == 1:
		subprocess.call(['echo', '***flatpak updates are not available at this time***'])
		return 1
		
	else:
		# uninstall unused flatpaks
		subprocess.call(['echo', '***flatpak uninstall --unused***'])
		subprocess.call(['flatpak', 'uninstall', '--unused', '-y'])
		
		# perform flatpak updates
		subprocess.call(['echo', '***flatpak update***'])
		subprocess.call(['/usr/bin/systemd-inhibit', '--why="Performing automatic updates"', '--who="Update Manager"', '--what=shutdown', '--mode=block', '/usr/bin/flatpak', 'update', '-y'])	# provide the exit code of flatpak update command
		subprocess.call(['echo', '***flatpak update has completed***'])
		return 0
				

def process_fwupdmgr():
	
	# check if updates are available
	subprocess.call(['/usr/bin/fwupdmgr', 'refresh', '--force'])
	exit_code = subprocess.call(['/usr/bin/fwupdmgr', 'get-updates'])
	
	# perform update if update is available, 0 = update available, 2 = no update available
	if exit_code == 2:
		subprocess.call(['echo', '***firmware updates are not available at this time***'])
		return 0
	
	else:
		# send notification that a firmware update is available
		# look into fwupd.service, fwupd-refresh.timer, and fwupd-refresh.service as a better alternative
		# subprocess.call(['/usr/bin/timeout', '-f', '-k', '1s', '10m', '/usr/bin/fwupdmgr', 'update', '-y'])
		subprocess.call(['usr/bin/notify-send', '"Firmware Update Needed"', '"$ fwupdmgr get-updates"'])
		subprocess.call(['echo', '***fwupdmgr update is available***'])
		return 0


if __name__ == '__main__':
    main()

