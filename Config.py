"""======================================================

Config file that holds the variables being used.

======================================================"""


class Config:
    apk_selection = \
        ['Accounts Lite 2.0',
         'Java Programming',
         'Aadhaar Info',
         'ABC 123 for Kids Child Toddler',
         'Time Converter',
         'A League Live',
         'D-Day with Pictures',
         'OBDLink',
         'Mega Tic Tac Toe',
         'Show Me Wales',
         'Macroscop'
         'Bible Trivia Quiz Game',
         'Kolumbus Sanntid',
         'The speech the President of the United States',
         'FOViewer Deluxe Free',
         'Geo-Wiki Pictures',
         'Minesweeper',
         'AddressToGPS',
         'Acastus',
         'Calculator',
         'Camp 2015',
         'A Photo Map',
         'AutomateIt',
         'Agroid',
         'Bacteriología',
         'Dining Table Ideas',
         'Pats Schedule',
         'Chrome']

    """========================================
    Change variables below to suit your settings
    ========================================"""

    # Sets the device name of emulator
    device_name = 'emulator-5554'

    # Selecting the package and application name for the application to be used
    selection_num = 0
    # app_instance = 1

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
