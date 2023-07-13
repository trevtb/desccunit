import ConfigParser


class DesecConfigParser:
    config = None

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("/etc/deseccunit/config.ini")

    def getoption(self, section, name):
        option = self.config.get(section, name)
        if option.lower() == 'yes':
            option = True
        elif option.lower() == 'no':
            option = False

        return option

    def getsettings(self):
        settings = {}
        settings['interface'] = self.getoption('HttpSettings', 'interface')
        settings['port'] = int(self.getoption('HttpSettings', 'port'))
        settings['onlylocalhost'] = self.getoption('HttpSettings', 'onlylocalhost')
        settings['useaccessprotection'] = self.getoption('HttpSettings', 'useaccessprotection')
        settings['allowedip'] = self.getoption('HttpSettings', 'allowedip')
        settings['useauthentication'] = self.getoption('HttpSettings', 'useauthentication')
        settings['username'] = self.getoption('HttpSettings', 'username')
        settings['password'] = self.getoption('HttpSettings', 'password')
        settings['portnum'] = int(self.getoption('CameraSettings', 'portnum'))
        settings['resolution'] = self.getoption('CameraSettings', 'resolution')
        settings['saturation'] = float(self.getoption('CameraSettings', 'saturation'))
        settings['enablemd'] = self.getoption('MDSettings', 'enabled')
        settings['movthreshold'] = int(self.getoption('MDSettings', 'threshold'))

        # Correctly set and format the path
        tail = self.getoption('MDSettings', 'directory')
        tail = tail[-1:]
        if tail == '/':
            settings['mddir'] = self.getoption('MDSettings', 'directory')
        else:
            settings['mddir'] = self.getoption('MDSettings', 'directory') + '/'

        return settings