#!/isan/bin/nxpython

# -*- coding: utf-8 -*-

"""
Copyright (c) 2018  Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.0 (the "License"). You may obtain a copy of the
License at

https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""


__author__ = "Simon Hart <sihart@cisco.com>"




################################################################
# File:   FibrePorts.py
#
# Description:
#    Application will look at recieved power levels on sfp's
#    that have Digital Optical Monitoring, and will report back
#    if power is being received, and thus whether fibre is connected
##################################################################


import time
import threading
import sys
import json
import re
from collections import OrderedDict

### Imports NX-OS SDK package
import nx_sdk_py


###
# Timer thread to showcase that native python threads can also
# run along with sdkThread which is also listening for NX-OS
# specific events. tmsg.event is just generating a log every 2 minutes
# to report that the application is running.  Could turn this off if required
###
def timerThread(name, val):
    global cliP, sdk, tmsg
    count = 0
    while True:
        count += 1
        if sdk and cliP:
            print "timer kicked - sdk"


        else:
            print "timer ticked - not sdk"
        if tmsg:
            ### Logs a event log everytime timer is kicked once tmsg
            ### is initialized.
            tmsg.event("Netsuite Timer ticked - %d" % count)

        time.sleep(120)


# RegEx search string to eliminate vlan, portchannel interfaces etc.
ethernet = re.compile(r'Ethernet\d.\d*')

# Configurable global variable for received power levels in db.
POWERLEVEL = -30


###
# Inherit from the NxCmdHandler class, define the application
# callback in 'postCliCb'. Handler Callback for Custom Cli execution.
# Returns True if the action was successful. False incase of failure.
###

class pyCmdHandler(nx_sdk_py.NxCmdHandler):
    def postCliCb(self, clicmd):

        ### To access the global Cli Parser Obj
        global cliP, ethernet, POWERLEVEL



        if "show_fibre" in clicmd.getCmdName():

            resp_str1 = cliP.execShowCmd("show interface brief", nx_sdk_py.R_JSON)
            resp_str2 = cliP.execShowCmd("show interface transceiver details", nx_sdk_py.R_JSON)
            intbriefJs = json.loads(resp_str1)
            inttransJs = json.loads(resp_str2)

            intdict = {}

            #Search for only ethernet interafaces, add state to new dictionary
            # intdict

            for i in intbriefJs["TABLE_interface"]["ROW_interface"]:

                mo = (ethernet.search(i["interface"]))
                try:
                    if mo.group() == i["interface"]:
                        intdict[i["interface"]] = {"state": i["state"]}
                except AttributeError:
                    pass

            #Add sfp, name, and power levels to dictionary intdict
            for i in inttransJs["TABLE_interface"]["ROW_interface"]:
                intdict[i["interface"]].update({"sfp": i["sfp"]})
                try:
                    intdict[i["interface"]].update({"name": i["name"]})
                    intdict[i["interface"]].update({"type": i["type"]})
                except KeyError:
                    #pass
                    intdict[i["interface"]].update({"name": "n\\a"})
                    intdict[i["interface"]].update({"type": "n\\a"})
                # try:
                #     intdict[i["interface"]].update({"name": i["name"]})
                # except KeyError:
                #     pass
                try:
                    if i["rx_pwr"]:
                        if float(i["rx_pwr"]) > POWERLEVEL:
                            print i["rx_pwr"]
                            intdict[i["interface"]].update({"fibre": "FIBRE PRESENT"})
                            intdict[i["interface"]].update({"rx_pwr": i["rx_pwr"]})
                        else:
                            intdict[i["interface"]].update({"fibre": "No Fibre"})
                            intdict[i["interface"]].update({"rx_pwr": i["rx_pwr"]})

                except KeyError:
                    intdict[i["interface"]].update({"fibre": "No Fibre"})
                    intdict[i["interface"]].update({"rx_pwr": 'N/A'})

            #Print out titles
            clicmd.printConsole('{:17}{:10}{:17}{:17}{:14}{:17}{:17}'.format('INTERFACE', 'STATE', 'SFP', 'FIBRE', 'POWER', 'NAME', 'TYPE\n'))
            #clicmd.printConsole('{:17}{:10}{:17}{:17}{:14}'.format('INTERFACE', 'STATE', 'SFP', 'FIBRE', 'POWER\n'))

            clicmd.printConsole('-' * 110)
            clicmd.printConsole('\n')

            #Order dictionary
            ordintdict = OrderedDict(sorted(intdict.items()))

            #Print out each of
            for k, v in ordintdict.items():
                clicmd.printConsole("{:17}{:10}{:17}{:17}{:14}{:17}{:17}\n".format(k, v["state"], v["sfp"], v["fibre"], v["rx_pwr"], v["name"],v["type"]))
                #clicmd.printConsole("{:17}{:10}{:17}{:17}{:14}\n".format(k, v["state"], v["sfp"], v["fibre"], v["rx_pwr"]))

        return True


### Perform all SDK related initializations in one thread.
### All SDK related activities happen here, while the main thread
### may continue to do other work.  The call to startEventLoop will
### block until we break out of it by calling stopEventLoop.
def sdkThread(name, val):
    global cliP, sdk, event_hdlr, tmsg, int_attr

    ###
    # getSdkInst is the first step for any custom Application
    # wanting to gain access to NXOS Infra. Without this
    # NXOS infra cannot be used.
    #
    # NOTE:
    #   Perform all SDK related initializations and startEventLoop in one
    #   thread. The call to startEventLoop will block the thread until we
    #   break out of it by calling stopEventLoop.
    #
    #   Perform other actions in a different thread.
    ###
    sdk = nx_sdk_py.NxSdk.getSdkInst(len(sys.argv), sys.argv)
    if not sdk:
        return

    ### Set a short Application description.
    sdk.setAppDesc('FibrePorts Python App')

    ###
    # To Create & Manage Custom syslogs one must do
    # getTracer() which loads the plugin to NXOS Syslog
    # Infra Functionalities.
    ###
    tmsg = sdk.getTracer()

    ### To log some Trace events
    tmsg.event("[%s] Started service" % sdk.getAppName())

    ###
    # To Create & Manage Custom CLI commands one must do
    # getCliParser() which loads the plugin to NXOS CLI
    # Infra Functionalities.
    ###
    cliP = sdk.getCliParser()

    ### Construct Custom show For Fibre ports
    nxcmd = cliP.newShowCmd("show_fibre", "ports")
    nxcmd.updateKeyword("ports", "fibre or not")

    ###
    # Add the command callback Handler.
    # When the respective CLI commands gets configured
    # the overloaded postCliCb callback will be instantiated.
    ###
    mycmd = pyCmdHandler()
    cliP.setCmdHandler(mycmd)

    ###
    # This is important as it Adds the constructed custom configs
    # to NXOS CLI Parse tree.
    ###
    cliP.addToParseTree()

    ###
    # startEventLoop will block the thread until we break out
    # of it by calling stopEventLoop.
    ###
    sdk.startEventLoop()

    ### Got here either by calling stopEventLoop() or when App
    ### is removed from VSH.
    tmsg.event("Service Quitting...!")

    ### [Required] Needed for graceful exit.
    nx_sdk_py.NxSdk.__swig_destroy__(sdk)


### main thread
### Global Variables
cliP = 0
sdk = 0
tmsg = 0


### create a new sdkThread to setup SDK service and handle events.
sdk_thread = threading.Thread(target=sdkThread, args=("sdkThread", 0))
sdk_thread.start()

timer_thread = threading.Thread(target=timerThread, args=("timerThread", 0))
timer_thread.daemon = True

###
# Starting timer thread. Start it after sdkThread is started so that
# any SDK specific APIs will work without any issues in timerThread.
###
timer_thread.start()

### Main thread is blocked until sdkThread exits. This keeps the
### App running and listening to NX-OS events.
sdk_thread.join()
