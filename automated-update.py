#!/usr/bin/python3

from pathlib import Path
import subprocess
import time


def main():
	
	global counter
	counter = 0
	while True:
		
		# 0 = internet connected
		if check_internet() == 0:
			
			# check if package manager apt-get is installed
			if Path('/usr/bin/apt-get').exists() == True:
										
				# 0 = update completed
				if process_apt_update() + process_apt_upgrade() + process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# if update was not completed, retry after delay	
				else:
					retry_update()
			
			# check if package manager dnf is installed
			elif Path('/usr/bin/dnf').exists() == True:	
				
				# 0 = update completed
				if process_dnf() + process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# if update was not completed, r, retry after delay	
				else:
					retry_update()

			# check if package manager pacman is installed
			elif Path('/usr/bin/pacman').exists() == True:	
				
				# 0 = update completed
				if process_pacman() + process_flatpak() == 0:
					process_fwupdmgr()
					subprocess.call(['echo', '***automated update complete***'])
					exit(0)
			
				# if update was not completed, retry after delay	
				else:
					retry_update()
			
			
		else:
			subprocess.call(['echo', '***not connected to internet, retry after delay***'])
			# retry internet connection after delay
			time.sleep(300)	
				

def check_internet():
	
	# check for a connection to internet, exit code 0 = connected
	if subprocess.call(['/usr/bin/ping', '-c', '1', 'www.google.com']) == 0:  				
		subprocess.call(['echo', '***connected to internet***'])
		return 0
		
	else:
		return 1


def retry_update():
	
	global counter
	if counter > 2:
		subprocess.call(['echo', '***service failed due to server error***'])
		exit(1)
	counter += 1
	subprocess.call(['echo', '***update was not completed, retry after delay***'])
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
	try:
		subprocess.call(['echo', '***dnf check available upgrades***'])
		exit_code = subprocess.call(['/usr/bin/dnf', 'check-upgrade'])	
		#print('exit_code')
		#print(exit_code)
	except Exception as e:
		print(e)
		exit_code = 0
	
	
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
		return 0		


def process_pacman():
	
	# work in progress
	return 0


def process_flatpak():
	
	# check if flatpak is installed
	if Path('/usr/bin/flatpak').exists() == False:
		subprocess.call(['echo', '***flatpak is not installed***'])
		return 0
	
	# get exit code for 'flatpak remote-ls --updates', check if updates are available, 0 = no updates available
	subprocess.call(['echo', '***flatpak remote-ls --updates***'])
	exit_code = subprocess.call(['/usr/bin/flatpak', 'remote-ls', '--updates'])	
	
	# NEED TO FIX exit code always returns zero
	
	if exit_code == 1:
		subprocess.call(['echo', '***flatpak updates are not available at this time***'])
		return 0
		
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
	subprocess.call(['echo', '***fwupdmgr refresh --force***'])
	subprocess.call(['/usr/bin/fwupdmgr', 'refresh', '--force'])
	exit_code = subprocess.call(['/usr/bin/fwupdmgr', 'get-updates', '-y'])
	
	# perform update if update is available, 0 = update available, 2 = no update available
	if exit_code == 2:
		subprocess.call(['echo', '***firmware updates are not available at this time***'])
		return 0
	
	else:
		# send notification that a firmware update is available
		notify_send_msg = [r"XUSERS=($(who|grep -E '\(:[0-9](\.[0-9])*\)' |awk '{print $1$NF}'|sort -u)); for XUSER in ${XUSERS[@]}; do NAME=(${XUSER/(/ }); DISPLAY=${NAME[1]/)/}; DBUS_ADDRESS=unix:path=/run/user/$(id -u ${NAME[0]})/bus; sudo -u ${NAME[0]} DISPLAY=${DISPLAY} DBUS_SESSION_BUS_ADDRESS=${DBUS_ADDRESS} PATH=${PATH} notify-send 'Firmware Update Needed' 'Run terminal commmand to update firmware: \n\n$ fwupdmgr upgrade'; done"]
		notify_send_cmd(notify_send_msg)
		subprocess.call(['echo', '***fwupdmgr update is available***'])
		return 0


def notify_send_cmd(command):
    """
    Executes a shell command and returns its output.
    """
    try:
        # shell=True allows passing the command as a single string
        # capture_output=True captures stdout and stderr
        # text=True decodes stdout and stderr as text using default encoding
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print("Command executed successfully:")
        print("Stdout:", result.stdout)
        if result.stderr:
            print("Stderr:", result.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        print("Stderr:", e.stderr)
        return None



if __name__ == '__main__':
    main()

