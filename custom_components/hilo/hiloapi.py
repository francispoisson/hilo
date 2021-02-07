import requests, time, json, datetime, logging, urllib

_LOGGER = logging.getLogger(__name__)

class Hilo():
    __username = None
    __password = None
    __access_token = None
    __location_id = None
    is_event = None

    access_token_expiration = None
    d = {}

    class Device():
        __name = None
        __identifier = None
        __deviceType = None
        __supportedAttributes = None
        __settableAttributes = None
        __deviceId = None
        __category = None
        OnOff = None
        Intensity = None
        CurrentTemperature = None
        TargetTemperature = None
        Power = None
        Status = None
        Heating = None
        BatteryPercent = None
        BatteryStatus = None
        ActiveAlarm = None
        WaterLeakStatus = None
        MotorTargetPosition = None
        MotorPosition = None
        AlertLowBatt = None
        AlertWaterLeak = None
        AlertLowTemp = None
        MaxTempSetpoint = None
        MinTempSetpoint = None
        StateTemperatures = None
        LoadConnected = None
        Icon = None
        Category = None
        Disconnected = None
        ColorMode = None
        Hue = None
        Saturation = None
        LockKeypad = None
        BackLight = None
        LoadConnectedDB = None
        Humidity = None
        ColorTemperature = None
        DrmsState = None
        Noise = None
        Pressure = None
        Co2 = None
        WifiStatus = None
        GrapState = None
        AttributeRaw = {}

        def __init__(self, name, identifier, deviceType, supportedAttributes, settableAttributes, deviceId, category):
            self.__name = name
            self.__deviceType = deviceType
            self.__supportedAttributes = supportedAttributes
            self.__settableAttributes = settableAttributes
            self.__deviceId = deviceId
            self.__category = category

        @property
        def deviceId(self):
            return self.__deviceId

        @property
        def name(self):
            return self.__name

        @property
        def supportedAttributes(self):
            return self.__supportedAttributes

        @property
        def settableAttributes(self):
            return self.__settableAttributes

        @property
        def deviceType(self):
            return self.__deviceType

        @property
        def deviceId(self):
            return self.__deviceId

        @property
        def category(self):
            return self.__category

    def __init__(self, username, password):
        # the function that is executed when
        # an instance of the class is created
        self.__username = username
        self.__password = urllib.parse.quote(password, safe='')
        suppAttrLowCase = {}

        try:
            self.__access_token = self.getAccessToken()
            if self.__access_token is None:
                raise Exception("Request for access token failed.")
        except Exception as e:
            _LOGGER.warning(e)
        else:
            self.access_token_expiration = time.time() + 3500

            try:
                self.__location_id = self.get_location_id()
                if self.__location_id is None:
                    raise Exception("Request for location_id failed.")
            except Exception as e:
                _LOGGER.warning(e)
            else:
                self.get_devices()
                for i in range(len(self.d)): 
                    suppAttr = self.d[i].supportedAttributes.split(", ")
                    if suppAttr[0] != "None":
                        self.get_device_attributes(i)
                        for x in range(len(suppAttr)):
                            s = "self.d[" + str(i) + "]." + suppAttr[x]
                            suppAttrLowCase[x] =  suppAttr[x][:1].lower() + suppAttr[x][1:]
                            s2 = 'self.d['+ str(i) + "].AttributeRaw['" + suppAttrLowCase[x] + "']['value']"
                            #_LOGGER.warning(s2)
                            try:
                                exec("%s = %s" % (s, s2))
                            except KeyError:
                                exec("%s = None" % (s))

    def getAccessToken(self):
        # the function that is 
        # used to request the JWT
        try:
            url = 'https://hilodirectoryb2c.b2clogin.com/hilodirectoryb2c.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1A_B2C_1_PasswordFlow'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            body = "grant_type=password&scope=openid 9870f087-25f8-43b6-9cad-d4b74ce512e1 offline_access&client_id=9870f087-25f8-43b6-9cad-d4b74ce512e1&response_type=token id_token&username=" + self.__username + "&password=" + self.__password

            req = requests.post(url, headers=headers, data=body)

            # optional: raise exception for status code
            req.raise_for_status()
        except Exception as e:
            print(e)
            return None
        else:
            # assuming the response's structure is
            # {"access_token": ""}
            return req.json()['access_token']


    def refreshToken(self):
            if time.time() > self.access_token_expiration:
                self.access_token_expiration = time.time()+3500
                self.__access_token = self.getAccessToken()
            return True


    def get_location_id(self):
        self.refreshToken()
        url = 'https://apim.hiloenergie.com/Automation/v1/api/Locations'
        headers = {'Ocp-Apim-Subscription-Key': '20eeaedcb86945afa3fe792cea89b8bf', 
            'authorization' : 'Bearer ' + self.__access_token}

        req = requests.get(url, headers=headers)
        req_dictionnary = req.json()

        if '401' in req.text:
            return None
        else:
            return req_dictionnary[0]['id']

    def get_events(self):
        self.refreshToken()
        url_get_events = 'https://apim.hiloenergie.com/Automation/v1/api/Drms/Locations/' + str(self.__location_id) + '/Events'
        headers = {'Ocp-Apim-Subscription-Key': '20eeaedcb86945afa3fe792cea89b8bf', 
            'authorization' : 'Bearer ' + self.__access_token}

        req = requests.get(url_get_events, headers=headers)
        req_dictionnary = req.json()

        event = {}

        now = datetime.datetime.utcnow() - datetime.timedelta(hours=5)

        for i in range(len(req_dictionnary)):
            start_time = datetime.datetime.strptime(req_dictionnary[i]['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(hours=5)
            end_time = datetime.datetime.strptime(req_dictionnary[i]['endTimeUTC'], "%Y-%m-%dT%H:%M:%SZ") - datetime.timedelta(hours=5)

            if((start_time.day == now.day) & (now.hour >= start_time.hour) & (now.hour < (end_time.hour))):
                event[i] = True
            else:
                event[i] = False

        test = 0

        for i in range(len(event)):
            if(event[i] == True):
              test = test+1

        if test == 0:
            self.is_event = False
        else:
            self.is_event = True
        return

    def get_devices(self):
        self.refreshToken()
        url_get_device = 'https://apim.hiloenergie.com/Automation/v1/api/Locations/' + str(self.__location_id) + '/Devices'
        headers = {'Ocp-Apim-Subscription-Key': '20eeaedcb86945afa3fe792cea89b8bf', 
            'authorization' : 'Bearer ' + self.__access_token}

        req = requests.get(url_get_device, headers=headers)
        req_dictionnary = req.json()

       # print(req_dictionnary)

        for i in range(len(req_dictionnary)):
            self.d[i] = self.Device(req_dictionnary[i]['name'], req_dictionnary[i]['identifier'], req_dictionnary[i]['type'], req_dictionnary[i]['supportedAttributes'], req_dictionnary[i]['settableAttributes'], req_dictionnary[i]['id'], req_dictionnary[i]['category'])
        return

    def get_device_attributes(self, index):
        self.refreshToken()
        deviceId = self.d[index].deviceId

        url_get_device_attr = 'https://apim.hiloenergie.com/Automation/v1/api/Locations/' + str(self.__location_id) + '/Devices/' +str(deviceId) + '/Attributes'
        headers = {'Ocp-Apim-Subscription-Key': '20eeaedcb86945afa3fe792cea89b8bf', 
            'authorization' : 'Bearer ' + self.__access_token}

        req = requests.get(url_get_device_attr, headers=headers)

       #print(req.text)

        
        self.d[index].AttributeRaw = req.json()

        return

    def update(self):
        self.refreshToken()
        suppAttrLowCase = {}
        self.get_events()

        try:
            self.__location_id = self.get_location_id()
            if self.__location_id is None:
                raise Exception("Request for location_id failed.")
        except Exception as e:
            print(e)
        else:
            self.get_devices()
            for i in range(len(self.d)): 
                suppAttr = self.d[i].supportedAttributes.split(", ")
                if suppAttr[0] != "None":
                    self.get_device_attributes(i)
                    for x in range(len(suppAttr)):
                        s = "self.d[" + str(i) + "]." + suppAttr[x]
                        suppAttrLowCase[x] =  suppAttr[x][:1].lower() + suppAttr[x][1:]
                        s2 = 'self.d['+ str(i) + "].AttributeRaw['" + suppAttrLowCase[x] + "']['value']"
                        try:
                            exec("%s = %s" % (s, s2))
                        except KeyError:
                            #return
                            exec("%s = None" % (s))
        return

    def update_device(self, index):
        self.refreshToken()
        suppAttr = self.d[index].supportedAttributes.split(", ")
        suppAttrLowCase = {}

        self.get_device_attributes(index)
        for x in range(len(suppAttr)):
            s = "self.d[" + str(index) + "]." + suppAttr[x]
            suppAttrLowCase[x] =  suppAttr[x][:1].lower() + suppAttr[x][1:]
            s2 = 'self.d['+ str(index) + "].AttributeRaw['" + suppAttrLowCase[x] + "']['value']"
            try:
                exec("%s = %s" % (s, s2))
            except KeyError:
                exec("%s = None" % (s))
                #return
        return

    def set_attribute(self, key, value, index):
        self.refreshToken()
        deviceId = self.d[index].deviceId

        timestamp = datetime.datetime.utcnow().isoformat()+'Z'

        url_post_device_attr = 'https://apim.hiloenergie.com/Automation/v1/api/Locations/' + str(self.__location_id) + '/Devices/' + str(deviceId) + '/Attributes'
        headers = {'Ocp-Apim-Subscription-Key': '20eeaedcb86945afa3fe792cea89b8bf', 
            'authorization' : 'Bearer ' + self.__access_token,
            'Content-Type': 'application/json'}

        body = {key: value}

        print(json.dumps(body))

        req = requests.put(url_post_device_attr, data=json.dumps(body), headers=headers)

        print(req)
        return
