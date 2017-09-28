"""======================================================

Config file that holds the variables being used.

======================================================"""


class Config:
    apk_selection = ['AddressToGPS',
                     'Acastus',
                     'Calculator',
                     'Camp 2015',
                     'A Photo Map']

    """========================================
    Change variables below to suit your settings
    ========================================"""

    # Sets the device name of emulator
    device_name = 'emulator-5554'

    # Selecting the package and application name for the application to be used
    selection_num = 4

    # Selecting the data where data is being stored at.
    data_store_location = './data/'

    # Set the MongoDB settings
    mongoHost = 'localhost'
    mongoPort = 27017

    # Set the name for widget to number representation
    classwidgetdict = './classWidget.txt'

    """========================================
            End of variable setting
    ========================================"""

    app_name = apk_selection[selection_num]

    def __init__(self):
        pass
