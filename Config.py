"""======================================================

Config file that holds the variables being used.

======================================================"""


class Config:
    apk_selection = [
        ['me.danielbarnett.addresstogps', 'AddressToGPS'],
        ['me.dbarnett.acastus', 'Acastus']
    ]

    """========================================
    Change variables below to suit your settings
    ========================================"""

    # Sets the device name of emulator
    device_name = 'emulator-5554'

    # Selecting the package and application name for the application to be used
    selection_num = 0

    # Selecting the data where data is being stored at.
    data_store_location = './data/'

    """========================================
            End of variable setting
    ========================================"""

    edit_widget = 'android.widget.EditText'
    button_widget = 'android.widget.Button'
    image_button_widget = 'android.widget.ImageButton'
    image_view_button_widget = 'android.widget.ImageView'

    app_name = apk_selection[selection_num][1]
    pack_name = apk_selection[selection_num][0]

    def __init__(self):
        pass