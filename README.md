# partymode
Party Mode code for Raspberry Pi

# Setup
* Install lightshow pi
* sudo nano /etc/crontab  
* Add the following lines
`SYNCHRONIZED_LIGHTS_HOME = /home/pi/lightshowpi`
`@reboot pi python /home/pi/partymode/pm_button.py  > /home/pi/lightshow.log 2>&1 &`
