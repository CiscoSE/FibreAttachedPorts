# FibreAttachedPorts

The FibreAttachedPorts application is built for the Cisco NX-OS range of Data Center switches (Nexus 9000).  

## Basic Operation

This simple application will display the SFP connected status of all ports on the switch.  Where an
SFP supports Digital Optical Monitoring, the application will display the received power levels, and
based upon the power level received will report whether fibre is connected to an active device at the 
opposite end of the link.



## Showing Port Status


n9kv1# show FibrePorts ports

INTERFACE        STATE     SFP              FIBRE            POWER         NAME             TYPE             
--------------------------------------------------------------------------------------------------------------
Ethernet1/1      up        present          No Fibre         0             CISCO-METHODE    1000base-T       
Ethernet1/10     down      not present      No Fibre         0             n\a              n\a              
Ethernet1/11     down      not present      No Fibre         0             n\a              n\a              
Ethernet1/12     down      not present      No Fibre         0             n\a              n\a   



## Running the application from BASH

The source code needs to be copied to the NXOS device and can be run from the BASH shell. If the code
is on bootflash:-

n9kv1# run bash

bash-4.2$ pwd

/bootflash/home/

bash-4.2$ cd /bootflash

bash-4.2$ nohup /isan/bin/python FibrePorts.py &

*do not kill the application within BASH.  In order stop the application do so from the command line*

n9kv1#(config)FibrePorts.py stop-event-loop

## Running the application as a Service

The advantages of running as a Service is that the application can be controlled by the operator from the NXOS
command line.  Additionally the application will be persistent and will continue to run after device reload.

The RPM file in this repository's RPM directory needs to be copied to the bootflash of the device.

Details on how to install RPM on NXOS devices can be found at the [NXSDK Github page](https://github.com/ciscodevnet/nx-sdk)
