"""
Input / Output example
Written by Sandy Barbour - 29/02/2004
Ported to Python by Sandy Barbour - 01/05/2005

This examples shows how to get input data from Xplane.
It also shows how to control Xplane by sending output data to it.

In this case it controls N1 depending on the throttle value.

It also shows the use of Menus and Widgets.
"""

from XPPython3 import xp
import grequests
import requests
import datetime
import re

class PythonInterface:
    def XPluginStart(self):
        self.url = "https://flight-data-server.azurewebsites.net/api/FlightData"  
        self.Name = "InputOutput1 v1.0"
        self.Sig = "SandyBarbour.Python.InputOutput1"
        self.Desc = "A plug-in that handles data Input/Output."
        self.flightActivated = False
        self.cnt = 0
        self.flightCode = ""
        
        self.myObj = {}

        self.MAX_NUMBER_ENGINES = 14
        self.MAX_INPUT_DATA_ITEMS = 2
        self.MAX_OUTPUT_DATA_ITEMS = 1

        # Use lists for the datarefs, makes it easier to add extra datarefs
        InputDataRefDescriptions = ["sim/flightmodel/engine/ENGN_thro", "sim/aircraft/engine/acf_num_engines"]
        OutputDataRefDescriptions = ["sim/flightmodel/engine/ENGN_N1_"]
        self.DataRefDesc = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14"]

        # Create our menu
        Item = xp.appendMenuItem(xp.findPluginsMenu(), "Python - Input/Output 1", 0)
        self.InputOutputMenuHandlerCB = self.InputOutputMenuHandler
        self.Id = xp.createMenu("Input/Output 1", xp.findPluginsMenu(), Item, self.InputOutputMenuHandlerCB, 0)
        xp.appendMenuItem(self.Id, "Data", 1)

        # Flag to tell us if the widget is being displayed.
        self.MenuItem1 = 0

        # Get our dataref handles here
        self.InputDataRef = []
        for Item in range(self.MAX_INPUT_DATA_ITEMS):
            self.InputDataRef.append(xp.findDataRef(InputDataRefDescriptions[Item]))

        self.OutputDataRef = []
        for Item in range(self.MAX_OUTPUT_DATA_ITEMS):
            self.OutputDataRef.append(xp.findDataRef(OutputDataRefDescriptions[Item]))

        # Register our FL callbadk with initial callback freq of 1 second
        self.InputOutputLoopCB = self.InputOutputLoopCallback
        xp.registerFlightLoopCallback(self.InputOutputLoopCB, 1.0, 0)

        return self.Name, self.Sig, self.Desc

    def XPluginStop(self):
        # Unregister the callback
        xp.unregisterFlightLoopCallback(self.InputOutputLoopCB, 0)

        if self.MenuItem1 == 1:
            xp.destroyWidget(self.InputOutputWidget, 1)
            self.MenuItem1 = 0

        xp.destroyMenu(self.Id)

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    def XPluginReceiveMessage(self, inFromWho, inMessage, inParam):
        pass

    def InputOutputLoopCallback(self, elapsedMe, elapsedSim, counter, refcon):
        if self.MenuItem1 == 0:  # Don't process if widget not visible
            return 1.0
        
                # Only deal with the actual engines that we have
        self.NumberOfEngines = xp.getDatai(self.InputDataRef[1])
        
        
        #fmc data
        description = []
        xp.getDatab(xp.findDataRef("sim/cockpit2/radios/indicators/fms_cdu1_text_line6"), description)
        bytearray(description)
        flightCode = bytearray([x for x in description if x]).decode('utf-8')
        flightCode = str(flightCode).replace(' ', '')
        self.flightCode = flightCode
        urlActivate = 'https://flight-data-server.azurewebsites.net/api/FlightData/startFlightCycle'
        urlDeActivate = 'https://flight-data-server.azurewebsites.net/api/endFlightCycle'

        payload = {
        "flightCode": flightCode,
        "airliner": 2,
        "isActive": True,
        "departedDate": "2023-03-27",
        "arivalDateHour": "2023-03-20T02:48:05.494Z",
        "arivalAirportCode": "LTFA",
        "departureAirportCode": "KSEA",
        "airplaneModel": "737-800",
        "tailNumber": "N3753",
        "pilotID": 5
        }

        headers = {
            'Content-Type': 'application/json'
        }

        if re.match("^[A-Z]{2,}", flightCode) and self.cnt == 0 :        
            requests.post(urlActivate, json=payload, headers=headers, verify=False)
            self.flightActivated = True
            self.flightCode= flightCode
            self.cnt +=1
        if flightCode =='.':
            self.flightActivated = False
            self.cnt = 0
            requests.post(urlDeActivate, headers=headers, verify=False)
   

        # Get our throttle positions for each engine
        self.Throttle = []
        count = xp.getDatavf(self.InputDataRef[0], self.Throttle, 0, self.NumberOfEngines)

        # Get our current N1 for each engine
        self.CurrentN1 = []
        count = xp.getDatavf(self.OutputDataRef[0], self.CurrentN1, 0, self.NumberOfEngines)

        # Process each engine
        self.NewN1 = []
        for Item in range(self.NumberOfEngines):
            # Default to New = Current
            self.NewN1.append(self.CurrentN1[Item])

        # Set the new N1 values for each engine
        xp.setDatavf(self.OutputDataRef[0], self.NewN1, 0, self.NumberOfEngines)


        altitudeRef = xp.findDataRef("sim/flightmodel/position/elevation")
        altitude= xp.getDatad(altitudeRef)
        xp.setWidgetDescriptor(self.InputEdit[0], str("Altitude"))
        xp.setWidgetDescriptor(self.OutputEdit[0], str(altitude))

        trueAirSpeedRef = xp.findDataRef("sim/flightmodel/position/true_airspeed")
        trueAirSpeed= xp.getDataf(trueAirSpeedRef)
        xp.setWidgetDescriptor(self.InputEdit[1], str("True Air Speed"))
        xp.setWidgetDescriptor(self.OutputEdit[1], str(trueAirSpeed))
                    
        latitudeDataRef = xp.findDataRef("sim/flightmodel/position/latitude")
        latitude= xp.getDataf(latitudeDataRef)
        xp.setWidgetDescriptor(self.InputEdit[2], str("Latitude"))
        xp.setWidgetDescriptor(self.OutputEdit[2], str(latitude))        
                     
        longitudeDataRef = xp.findDataRef("sim/flightmodel/position/longitude")
        longitude= xp.getDataf(longitudeDataRef)
        xp.setWidgetDescriptor(self.InputEdit[3], str("Longitude"))
        xp.setWidgetDescriptor(self.OutputEdit[3], str(longitude))        
        
        headingRef = xp.findDataRef('sim/cockpit/misc/compass_indicated')
        heading = xp.getDataf(headingRef)
        xp.setWidgetDescriptor(self.InputEdit[4], str("Heading"))
        xp.setWidgetDescriptor(self.OutputEdit[4], str(heading))
        
        xp.setWidgetDescriptor(self.InputEdit[5], str("Throttle 1"))
        xp.setWidgetDescriptor(self.OutputEdit[5], str(self.Throttle[0]))
        
        xp.setWidgetDescriptor(self.InputEdit[6], str("Throttle 2"))
        xp.setWidgetDescriptor(self.OutputEdit[6], str(self.Throttle[1]))     
                      
        aoaRef = xp.findDataRef('sim/flightmodel/position/alpha')
        aoa = xp.getDataf(aoaRef)
        xp.setWidgetDescriptor(self.InputEdit[7], str("Angle of attack"))
        xp.setWidgetDescriptor(self.OutputEdit[7], str(aoa))
      
        groundSpeedRef = xp.findDataRef('sim/flightmodel2/position/groundspeed')
        groundSpeed = xp.getDataf(groundSpeedRef)
        xp.setWidgetDescriptor(self.InputEdit[8], str("Ground Speed"))
        xp.setWidgetDescriptor(self.OutputEdit[8], str(groundSpeed))
        
        totalFuelRef= xp.findDataRef('sim/flightmodel/weight/m_fuel_total')
        totalFuel = xp.getDataf(totalFuelRef)
        xp.setWidgetDescriptor(self.InputEdit[9], str("Total Fuel kg"))
        xp.setWidgetDescriptor(self.OutputEdit[9], str(totalFuel))
                    
        outsideTempRef= xp.findDataRef('sim/cockpit2/temperature/outside_air_temp_deg')
        outsideTemp = xp.getDataf(outsideTempRef)
        xp.setWidgetDescriptor(self.InputEdit[10], str("Outside Temperatue"))
        xp.setWidgetDescriptor(self.OutputEdit[10], str(outsideTempRef))
      
        landingGearRef= xp.findDataRef('sim/cockpit/switches/gear_handle_status')
        landingGear = xp.getDatai(landingGearRef)
        xp.setWidgetDescriptor(self.InputEdit[11], str("Landing Gear"))
        xp.setWidgetDescriptor(self.OutputEdit[11], str(landingGear))
        

      
        current_time = datetime.datetime.utcnow()
        formatted_time = current_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        url = "https://flight-data-server.azurewebsites.net/api/FlightData"

        myobj = {
        "id": 0,
        "loggingTime": formatted_time,
        "trueAirSpeed": float(trueAirSpeed),
        "groundSpeed": float(groundSpeed),
        "latitude": float(latitude),
        "longitude": float(longitude),
        "altitude": float(altitude),
        "throttle": 0,
        "heading": float(heading),
        "throttle1": float(self.Throttle[0]),
        "throttle2": float(self.Throttle[1]),
        "AOA": float(aoa),
        "totalFuel": float(totalFuel),
        "outsideTemperature": float(outsideTemp),
        "landingGear": int(landingGear),
        "flightCode" : self.flightCode         
        }
    
        xp.setWidgetDescriptor(self.InputEdit[12], str("Flight Code"))
        xp.setWidgetDescriptor(self.OutputEdit[12], str(flightCode))
        
        xp.setWidgetDescriptor(self.InputEdit[13], str("Flight Activated"))
        xp.setWidgetDescriptor(self.OutputEdit[13], str(self.flightActivated))
        
        if self.flightActivated == True: 
            req = grequests.post(url, json = myobj  , verify = False )
            req.send()


        # This means call us ever 10ms.
        return 20

    def InputOutputMenuHandler(self, inMenuRef, inItemRef):
        # If menu selected create our widget dialog
        if inItemRef == 1:
            if self.MenuItem1 == 0:
                self.CreateInputOutputWidget(300, 700, 400, 700)
                self.MenuItem1 = 1
            else:
                if not xp.isWidgetVisible(self.InputOutputWidget):
                    xp.showWidget(self.InputOutputWidget)

    """
    This will create our widget dialog.
    I have made all child widgets relative to the input paramter.
    This makes it easy to position the dialog
    """
    def CreateInputOutputWidget(self, x, y, w, h):
        x2 = x + w
        y2 = y - h

        # Create the Main Widget window
        self.InputOutputWidget = xp.createWidget(x, y, x2, y2, 1, "Flight Deck X-Plane Plugin",
                                                 1, 0, xp.WidgetClass_MainWindow)

        # Add Close Box decorations to the Main Widget
        xp.setWidgetProperty(self.InputOutputWidget, xp.Property_MainWindowHasCloseBoxes, 1)

        # Create the Sub Widget window
        InputOutputWindow = xp.createWidget(x + 50, y - 50, x2 - 50, y2 + 50, 1, "",
                                            0, self.InputOutputWidget, xp.WidgetClass_SubWindow)

        # Set the style to sub window
        xp.setWidgetProperty(InputOutputWindow, xp.Property_SubWindowType, xp.SubWindowStyle_SubWindow)

        # For each engine
        InputText = []
        self.InputEdit = []
        self.OutputEdit = []
        for Item in range(self.MAX_NUMBER_ENGINES):
            # Create a text widget
            InputText.append(xp.createWidget(x + 60, y - (60 + (Item * 30)), x + 90, y - (82 + (Item * 30)), 1,
                                             self.DataRefDesc[Item], 0, self.InputOutputWidget, xp.WidgetClass_Caption))

            # Create an edit widget for the throttle value
            self.InputEdit.append(xp.createWidget(x + 100, y - (60 + (Item * 30)), x + 180, y - (82 + (Item * 30)), 1,
                                                  "", 0, self.InputOutputWidget, xp.WidgetClass_TextField))

            # Set it to be text entry
            xp.setWidgetProperty(self.InputEdit[Item], xp.Property_TextFieldType, xp.TextEntryField)

            # Create an edit widget for the N1 value
            self.OutputEdit.append(xp.createWidget(x + 190, y - (60 + (Item * 30)), x + 270, y - (82 + (Item * 30)), 1,
                                                   "", 0, self.InputOutputWidget, xp.WidgetClass_TextField))

            # Set it to be text entry
            xp.setWidgetProperty(self.OutputEdit[Item], xp.Property_TextFieldType, xp.TextEntryField)

        # Register our widget handler
        self.InputOutputHandlerCB = self.InputOutputHandler
        xp.addWidgetCallback(self.InputOutputWidget, self.InputOutputHandlerCB)

    def InputOutputHandler(self, inMessage, inWidget, inParam1, inParam2):
        if inMessage == xp.Message_CloseButtonPushed:
            if self.MenuItem1 == 1:
                xp.hideWidget(self.InputOutputWidget)
            return 1

        return 0
