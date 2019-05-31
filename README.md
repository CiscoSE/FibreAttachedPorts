# FibreAttachedPorts



---

## Motivation

I had a client that wished to know whether ports with SFPs had fibre attached to them on NXOS devices.  SFPs with Digital Optical Monitoring can report the received levels of light on the SFP, no or very low light (sub -30db) means that there is no fibre attached.  

So the challenge was to create a **command line interface** command to display whether fibre was attached or not.  The objective was to demonstrate the programmability of NXOS and how to leverage NXSDK to create command line arguments, and run them as a service.



## Technologies & Frameworks Used

This project is using the inbuilt Python 2.7 interpreter that comes shipped with NXOS as well as leveraging [NXSDK](https://github.com/CiscoDevNet/NX-SDK/blob/master/README.md)

**Cisco Products:**

- Nexus 9K running NXOS

## Usage

This simple application will display the SFP connected status of all ports on the switch.  Where an
SFP supports Digital Optical Monitoring, the application will display the received power levels, and
based upon the power level received will report whether fibre is connected to an active device at the 
opposite end of the link.



## Showing Port Status

n9kv1# show FibrePorts ports

```bash
INTERFACE        STATE     SFP              FIBRE            POWER      
 -----------------------------------------------------------------
Ethernet1/1      up        not applicable   No Fibre         N/A                       
Ethernet1/10     down      not applicable   No Fibre         N/A                
```





## Installation

The application can either be run directly from the NXOS Bash Shell or installed as a Service.

The advantage of running as a service is that the application is persistent between reboots as the service is installed as part of the configuration.



### Bash

Copy the file **fibreports.py** to bootflash of the NXOS switch.

```bash
scp ~/FibreAttachedPorts/FibrePorts.py <username>@<9k_address_or_fqdn>:
```

Login to your NXOS switch

```bash
ssh <username>@<9k_address_or_fqdn>
```

Run bash and start up the python program.  Use _nohup_ so that the application continues to run when the bash session closes and use _&_ for the application to run in the background

```bash
n9k# run bash
bash-4.2$ cd /bootflash
bash-4.2$ nohup /isan/bin/python FibrePorts.py &
```



**STOPPING THE APPLICATION**

If you need to stop the application then **do not** kill the process in Bash.  The recommended method of stopping the application is from the NXOS switch command line

```bash
n9k#(config)FibrePorts.py stop-event-loop
```



## Running the application as a Service

The advantages of running as a Service is that the application can be controlled by the operator from the NXOS command line.  Additionally the application will be persistent and will continue to run after device reload.

The **rpm** in order to run the application as a service has been included in this repo.  The rpm will need to be copied to the bootflash of the NXOS switch.

```bash
scp ~/FibreAttachedPorts/RPMs/FibrePorts.py-1.0-1.5.0.x86_64.rpm \<username>@<9k_address_or_fqdn>:
```

Login to your NXOS switch

```bash
ssh <username>@<9k_address_or_fqdn>
```

Check if NXSDK feature is running

```bash
n9k#(config)show feature
```

If NXSDK feature is _disabled_ then enable by issuing the following command

```bash
n9k#(config)feature nxsdk
```

Now install the **rpm** within Bash and exit back NXOS

```bash
n9k# run bash sudo su
bash-4.3# yum install /bootflash/FibrePorts.py-1.0-1.5.0.x86_64.rpm
bash-4.3# exit
exit
n9k#
```

Initiate the service from the command line

```bash
n9k(config)# nxsdk service-name FibrePorts.py
% This could take some time. "show nxsdk internal service" to check if your App is Started & Runnning
```

The service is now running, to check the state of the service "show nxsdk internal service"

**Stopping the service**

To stop the service issue the following command

```bash
n9k(config)# no nxsdk service-name FibrePorts.py
```



### Custom application development with NXSDK

For further details on creating and deploying services with NXSDK please go to [NXSDK Guide](https://github.com/CiscoDevNet/NX-SDK/blob/master/README.md#6-running-custom-application-in-switch)



### Notes on FibrePorts python script

**Timer - Syslog**

The application in it's default state will create a syslog message every 2 minutes to log the that the service is still alive.  The form of the syslog message will be in the format below

```
2019 May 31 14:35:31 n9k nxsdk: Fibreports Timer ticked - 1
```

To stop the messages then comment out the following code (line 255)

```python
timer_thread.start()
```



**Power Levels**

The power level defaults to -30db.  To adjust this value then amend the variable 

```python
POWERLEVEL = -30
```



### To Do

* Create CLI command to turn on/off syslog messages
* Create CLI command to adjust power levels



## Authors & Maintainers

Smart people responsible for the creation and maintenance of this project:

- Simon Hart <sihart@cisco.com>

## License

This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
