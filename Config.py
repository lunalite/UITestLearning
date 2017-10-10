"""======================================================

Config file that holds the variables being used.

======================================================"""
import getpass
import os


class Config:
    # apk_selection = \
    #     ['Accounts Lite 2.0',
    #      'Java Programming',
    #      'Aadhaar Info',
    #      'ABC 123 for Kids Child Toddler',
    #      'Time Converter',
    #      'A League Live',
    #      'D-Day with Pictures',
    #      'OBDLink',
    #      'Mega Tic Tac Toe',
    #      'Show Me Wales',
    #      'Macroscop'
    #      'Bible Trivia Quiz Game',
    #      'Kolumbus Sanntid',
    #      'The speech the President of the United States',
    #      'FOViewer Deluxe Free',
    #      'Geo-Wiki Pictures',
    #      'Minesweeper',
    #      'AddressToGPS',
    #      'Acastus',
    #      'Calculator',
    #      'Camp 2015',
    #      'A Photo Map',
    #      'AutomateIt',
    #      'Agroid',
    #      'Bacteriologaa',
    #      'Dining Table Ideas',
    #      'Pats Schedule',
    #      'Chrome']

    """========================================
    Change variables below to suit your settings
    ========================================"""

    # Sets the device name of emulator
    device_name = 'emulator-5554'

    # Selecting the data where data is being stored at.
    data_store_location = './data/'

    # Set the MongoDB settings
    mongoHost = 'localhost'
    mongoPort = 27017

    # Set the name for widget to number representation
    classwidgetdict = './classWidget.txt'

    # Probability of flinging the screen if scrollable is found
    # not flinging, fling up, fling down
    scroll_probability = [0.8, 0.9, 1.0]

    # base storage location for logs like XML and screenshots
    log_location = './log/'

    # Information location storing number of activities/clickables stored
    info_location = './log/info'

    # Directory where APKs are stored in for enumerating through them
    current_user = getpass.getuser()
    if current_user == 'hkoh006':
        apkdir = '/Users/hkoh006/Desktop/APK/dir_001/'
        android_home = os.environ['ANDROID_HOME'] + '/' or '/Users/hkoh006/Library/Android/sdk/'
    elif current_user == 'hongda':
        apkdir = '/home/hongda/Document/apk/a/dir_001/'
        android_home = os.environ['ANDROID_HOME'] + '/' or '/home/hongda/Document/sdk/'

    """========================================
            End of variable setting
    ========================================"""

    # app_name = apk_selection[selection_num]
    app_name = ''

    def __init__(self):
        pass
