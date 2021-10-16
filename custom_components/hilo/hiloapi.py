import requests, time, json, logging, urllib
from datetime import datetime, timedelta
from functools import wraps
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

_LOGGER = logging.getLogger(__name__)


def refreshToken(method):
    @wraps(method)
    def _impl(self, *args, **kwargs):
        if self.refreshAccessToken():
            return method(self, *args, **kwargs)
    return _impl

class Hilo():
    __username = None
    __password = None
    __access_token = None
    __location_id = None
    is_event = None

    base_url = "https://apim.hiloenergie.com/Automation/v1/api/"
    subscription_key = '20eeaedcb86945afa3fe792cea89b8bf'
    access_token_expiration = None
    d = {}


    def __init__(self, username, password):
        # the function that is executed when
        # an instance of the class is created
        self.__username = username
        self.__password = urllib.parse.quote(password, safe='')
        self._session = self._create_session()

        if not self.refreshAccessToken(True):
            _LOGGER.warning("Invalid username or password for Hilo integration")
            raise Exception("Unable to get token, check username and password")
        self.update()

    @property
    def location_url(self):
        self.__location_id = self.get_location_id()
        return f"{self.base_url}/Locations/{self.__location_id}"

    @property
    def headers(self):
        return {'Ocp-Apim-Subscription-Key': self.subscription_key, 
                'authorization' : f'Bearer {self.__access_token}'}


    def _create_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _call(self, url, method="get", headers={}, data={}, verify=True):
        try:
            r = self._session.request(method, url, timeout=90, headers=headers, verify=verify, data=data)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            if r.status_code == 401:
                raise InvalidToken('Access token rejected')
        return r

    def _request(self, url, method="get", headers={}, data={}, verify=True):
        if not headers:
            headers = self.headers
        if method == "put":
            headers = {**headers, **{'Content-Type': 'application/json'}}
        try:
            return self._call(url, method, headers, data, verify)
        except InvalidToken:
            self.refreshAccessToken(True)
            return self._call(url, method, headers, data, verify)

    def getAccessToken(self):
        # the function that is 
        # used to request the JWT
        try:
            url = 'https://hilodirectoryb2c.b2clogin.com/hilodirectoryb2c.onmicrosoft.com/oauth2/v2.0/token?p=B2C_1A_B2C_1_PasswordFlow'
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            body = "grant_type=password&scope=openid 9870f087-25f8-43b6-9cad-d4b74ce512e1 offline_access&client_id=9870f087-25f8-43b6-9cad-d4b74ce512e1&response_type=token id_token&username=" + self.__username + "&password=" + self.__password
            req = self._session.post(url, headers=headers, data=body)
            req.raise_for_status()
        except Exception as e:
            _LOGGER.error(e)
            return None
        return req.json().get('access_token', None)

    def refreshAccessToken(self, force=False):
        if force or time.time() > self.access_token_expiration:
            self.access_token_expiration = time.time()+3500
            self.__access_token = self.getAccessToken()
            if not self.__access_token:
                return False
        return True

    @refreshToken
    def get_location_id(self):
        if self.__location_id:
            return self.__location_id
        url = f'{self.base_url}/Locations'
        req = self._request(url).json()
        return req[0]['id']


    @refreshToken
    def get_events(self):
        url_get_events = f'{self.base_url}/Drms/Locations/{self.__location_id}/Events'
        req = self._request(url_get_events).json()

        event = {}

        now = datetime.utcnow() - timedelta(hours=5)

        for i in range(len(req)):
            start_time = datetime.strptime(req[i]['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5)
            end_time = datetime.strptime(req[i]['endTimeUTC'], "%Y-%m-%dT%H:%M:%SZ") - timedelta(hours=5)

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

    @refreshToken
    def get_devices(self):
        url_get_device = f'{self.location_url}/Devices'
        req = self._request(url_get_device).json()
        _LOGGER.debug(f"get_devices: {req}")

        for i, v in enumerate(req):
            _LOGGER.debug(f"Device {i} {v}")
            self.d[i] = Device(v['name'],
                               v['identifier'],
                               v['type'],
                               v['supportedAttributes'],
                               v['settableAttributes'],
                               v['id'],
                               v['category'])


    @refreshToken
    def get_device_attributes(self, index):
        d = self.d[index]
        url_get_device_attr = f'{self.location_url}/Devices/{d.deviceId}/Attributes'
        req = self._request(url_get_device_attr)
        #_LOGGER.debug(f"get_device_attributes: {req.text}")
        self.d[index].AttributeRaw = {k.lower(): v for k, v in req.json().items()}


    def update(self):
        #self.get_events()
        _LOGGER.debug(f"updating all {len(self.d)} devices")
        self.get_devices()
        for i, d in self.d.items():
            self.update_device(i)

    def update_device(self, index):
        self.get_device_attributes(index)
        d = self.d[index]
        suppAttr = d.supportedAttributes.split(", ")
        _LOGGER.debug(f"[Device {index} {d.name} ({d.deviceType})] update_device attributes: {suppAttr}")
        if "None" in suppAttr:
            return
        self.get_device_attributes(index)
        for x in suppAttr:
            value = d.AttributeRaw.get(x.lower(), {}).get('value', None)
            _LOGGER.debug(f"[Device {index} {d.name} ({d.deviceType})] setting local attribute {x} to {value}")
            setattr(d, x, value)

    @refreshToken
    def set_attribute(self, key, value, index):
        d = self.d[index]
        setattr(d, key, value)
        url = f'{self.location_url}/Devices/{d.deviceId}/Attributes'
        _LOGGER.debug(f"[Device {index} {d.name} ({d.deviceType})] setting remote attribute {key} to {value}")
        req = self._request(url, method='put', data=json.dumps({key: str(value)}))

class Device():
    __name = None
    __identifier = None
    __deviceType = None
    __supportedAttributes = None
    __settableAttributes = None
    __deviceId = None
    __category = None
    OnOff = None
    Intensity = 0
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

class InvalidToken(Exception):
    pass
