# UI Testing - Reinforcement Learning

Project is on-going

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
(TODO)

## Deployment

In order to deploy the data collection server, the following are required:
1. Python 3 (Current version Python 3.6.2)

Do note that `sudo` permissions might be needed for running all of the following due to the usage of kvm for the emulator in the case that no screen is provided, so install the following within the `sudo` environment.

After installing python 3, do a `pip3 install -r requirements.txt` to obtain all python modules required for running the crawler.
Do note that depending on your system, it might be a `pip3.6` or `pip` instead of `pip3`.

Also depending on the permissions provided, it might be needed for the command `pip3 install --user -r requirements.txt` to be used instead.

It is up to the user whether he wants to create a `virtualenv` for the project or not.

Do remember to add into environment `PATH` the folders within android sdk such as `$ANDROID_HOME/platform-tools`, `$ANDROID_HOME/tools` and `$ANDROID_HOME/tools/bin`.

## Data collection
Apps are made to run until they finished or they crashed. Data is stored into mongodb via pymongo. The following are apps which have been tested on:

No|Appname|packagename|Acitivty count | Clickable count
---|---|---|---|---
1|Calculator|com.android.calculator2|10|190
2|AdressToGPS|me.danielbarnett.addresstogps|1|6
3|Acastus|me.dbarnett.acastus|8|29
4|Camp 2015|nerd.tuxmobil.fahrplan.camp|14|92
5|A Photo Map|de.k3b.android.androFotoFinder|31|358
6|AutomateIt|AutomateIt.mainPackage|27|274
7|Agroid|B4A.Agroid_software|16|78
8|Bacteriología|BacteriologiaFree.Doctor|5|44
9|Dining Table Ideas|con.dinta.app1|25|65
10|Pats Schedule|DrWebsterApps.New.England.Patriots.Trivia|12|63
11|Minesweeper|Draziw.Button.Mines|1|231
12|Geo-Wiki Pictures|GeoWikiMobile.GeoWikiMobile|11|77
13|FOViewer Deluxe Free|JVC.FOViewerDX|32|593
14|The speech the President of the United States|Js.Usa_Uspa|3|21
15|Kolumbus Sanntid|Kolumbus.Sanntid.Android|22|172
16|Bible Trivia Quiz Game|DrWebsterApps.BibleTriviaGame|10|85
17|Macroscop|-|Unable to get info
18|Show Me Wales|NVG.ShowMeWales|7|32
19|Mega Tic Tac Toe|NoamStudios.Games.MegaTicTacToeFree|5|36
20|OBDLink|OCTech.Mobile.Applications.OBDLink|10|49
21|D-Day with Pictures|View.CountDownToSpecialDay.Admob|15|107
22|A League Live|a.league.live|31|251
23|Time Converter|abcom.com.timeconverter|16|123
24|ABC 123 for Kids Child Toddler|abc123.kids.toddlers|6|25
25|Aadhaar Info|aadhaar.driving.voterid.passport|15|53
26|Java Programming|ab.java.programming|52|553
27|Accounts Lite 2.0|accountslite.n2tech.namespace|25|239
Total| | |416|3865


Unable to test certain APKs like those of other languages, or those like 'Power Me Off' since it might shut down the entire emulator.
Or some which there are no clickables(flash games) Or those that require login and internet like Absolute EMR and AccuManager.

## Examples of such APKs
* at.alladin.rmbt.android_20214.apk - no clickable buttons

-- Will be using system-images;android-25;google_apis;armeabi-v7a
-- and system-images;android-26;google_apis;x86

## Updates
### 2 November 2017
* Taken care of socket timeout error. Restart the entire APK if socket timed out.
* Fixed issue regarding repeated horizontal scrolls
* Reduction of rerolling random click button tries
* Changed state_info for scrolling decision from None to APP_STATE.SCROLLING
* Fixed bug of not adding increment to counter when trying to get another random btn to click

### 30 October 2017
* Added enum states for app crashes
* Fixed issue with APK that does not have androidmanifest.xml
* Added timeout for inactivity and for clicking of a single button
* Solved issue with local variable 'state_info' referenced before assignment

### 28 October 2017
* Fixed issue regarding horizontal panes

### 27 October 2017
* Added timeout function of 400 seconds for overall testing

### 26 October 2017
* Discovered several issues related to why UIautomator stops. They are:
1) crashes
2) d(clickable=‘true’) UIautomator instrumentation fails to return a list
3) no clickable buttons to proceed
4) login page (random string so can’t enter)
5) Page loading, but the UIAutomator doesn't wait. causing Key/index error
* Changed catching of initial error and added logging to information txt
* Changed catching of monkey error and added logigng

### 25 October 2017
* Edited issue with editText
* Added a signal handler in case of being stuck for too long.

### 22 October 2017
* Patched an issue resulting in KeyError

### 18 October 2017
* Added check for ASCII name
* Catch IndexError if no buttons clickable in new state

### 16 October 2017
* Added init file for shell

### 12 October 2017
* Main error now is with KeyError...
* Changed commands to allow for multiple emulators
* Created `preprocessing.py` for selecting of APK filename into separate text files.

### 11 October 2017
* Reason for screenshot being half taken at resolution 480x320 is because the skin is not chosen properly. Prior to this, the command used for creating the avd is: `android create avd -n avd1 -b x86 -k "system-images;android-26;google_apis;x86"` but this defaults to an avd that is skinless, causing error to arise.
```
Available Android Virtual Devices:
    Name: Nexus_5X_API_26
  Device: Nexus 5X (Google)
    Path: /Users/hkoh006/.android/avd/Nexus_5X_API_26.avd
  Target: Google Play (Google Inc.)
          Based on: Android API 26 Tag/ABI: google_apis_playstore/x86
    Skin: nexus_5x
  Sdcard: 100M
---------
    Name: testAVD
    Path: /Users/hkoh006/.android/avd/testAVD.avd
  Target: Google APIs
          Based on: Android API 26 Tag/ABI: google_apis/x86
  Sdcard: 100M

```

* The top AVD is created from Android Studio's AVD Manager and the subsequent one is created using the command.
Thus, we have to add a skin to the testAVD by running the `emulator -avd testAVD -skin 1080x1920` command since `-skin` flag for the `android create avd` is not found/deprecated.


### 10 October 2017
* Fixed bug in 'Issue with clicking back button prematurely' where the app is reopened using the old method instead of monkey method.
* Issue with screenshot being half taken. Suspicion to be because the buttons are clicked without waiting, causing transitioning to happen too fast and screenshots to be half taken.
* Reduced probability for scrolling up and down if scrollable exists in page.

### 9 October 2017
* Fixed subprocess call in Utilty.py.
* Fixed bug in sibs and children args in the case that there are no parents.

### 8 October 2017
* Added function to start emulator and unlock screen (removed).
* Changed subprocess calls to fit in android_home.
* Added logging function into file to prepare for deployment.
* Added force stop at the end of testing to prevent flooding of opened applications.
* Change opening of application method into using `adb monkey` instead.

### 6 October 2017
* Added auto adb install/uninstall and inputting of information into `information-{datetime}.txt` file in preparation for deployment onto server for automatic crawl
* `information-{datetime}.txt` file contains package name and application name of those crawled, including if file can be tested or not.
* Added scrollable for finding of app to start it
* Changed tester to return `-1` if `total_score < 0.5 * len(_scores_arr)` so as to allow for the case that an activity has many clickables and isn't stopping for far too long.
* Added counter limit so as to prevent the testing from happening for far too long on a single apk
* Added `next_transition_state` to point to self if clickable doesn't lead to `new_state`.
* Added probability of scrolling through the activtiy to allow for greater exploration. This is done according to a probability map if widget is scrollable.
* Added dump for xml and screenshot of each states into `/log/{packagename}` folder with each file named according to its state.

### 2 October 2017
* If sum of score is less than 1, press back to prevent repetition of clicks.
* Added option if parent could not be found to change children and siblings to None as well

### 1 October 2017
* Fixed autocomplete bug by adding TextView widget into conditional check as well
* Added time delay when an app first started in view of loading
* If textbox is not empty, don't set the textbox again

### 30 September 2017
* Weird behavior when EditText widget is opened and closed. Two different states as a of `insertion_handler` appearing after closing the keyboard.
* Fixed bug in parent_map storage
* Return None if no parents
* Using bound as key for buttons is bad because the activity might be scrollable, causing changes in bounds as well
* Fixed bug where `str(info['content description]))` actually returns None for `btn_to_key()` and empty string for `xml_btn_to_key()`


### 29 September 2017
* Issue with autocomplete when adding text, causing UItester to crash. Added option to select first option for autocomplete
* Issue with having only a single button present on UI, causing deadlock. Add in a press back button after counting to 5.
* Added hash encoding for key of state and state representation using the button type
* Added in a check to determine if stored button matches with the button being clicked
* Issue with clickable elements increasing and decreasing in the same state. Will be appending to the dict any elements that appear so as to prevent any unforeseen circumstances
* Changed getting parent with bound to getting parent with key since there might be buttons with same bound but different text
* Added mergence of two dicts for parent to key dict since there might be buttons with different keys in same state, causing the issue of `KeyError` when searching for child using parent


### 28 September 2017
* Fixed bug for `rec()` in `click_els = d(clickable='true')`
* Added clickable factor in finding parent
* Added check for change in buttons, removing and adding them accordingly
* Fixed bug for repetition of storage of data


### 27 September 2017
* Added visited dict to determine if widget is visited or not using weighted probability
* Fixed bug of repeated activity in app collection
* Added conditional that if the current activity has different package name, press back

### 25 September 2017
* Added dict representation as an option for reducing abstraction of `get_state()`
* Changed `get_state()` representation by inserting packagename to the front.
* Added activity name to storage
* Increased len of state to last 30 so as to reduce chance of collision.

### 22 September 2017
* Data dump repetition

### 20 September 2017
* Fixed a bug of selecting button even if score is 0
* Added an implementation for app to move back if score array is entirely 0
* Added periodic database storage/

### 18 September 2017
* Implemented database storing system
* Fixed bugs for showing of siblings
* Added get_children(), splitting up siblings

### 17 September 2017
* Redid the entire Main.py to suit datacollection and storage into mongodb
* Redid `get_siblings` and `get_parent` methods using strings so as to reduce time taken for search

### 13 September 2017
* Transferring from local file storage system over to Mongodb so as to optimize storage and search
* Removed clickable hash that optimizes and reduce time interval between clicks since there might be different possible click objects in a single activity
* Fixed bugs for loading of json
* Changed `get_state()` method with compressed=false for dump, allowing greater robustness.


### 11 September 2017
* Optimized improvement for a few seconds
* Removed text in clickable storage since it isn't representative of an unchangeable unique key
* Added parent node to clickable data structure

### 10 September 2017
* Determine which activity page is more useful. == giving scores to activity based on no. of clickables
* Added length parameter into data_activity object for faster matching of length of clickables
* Added score parameter for optimization.


### 6 September 2017
* Added mutation for decision of choosing buttons
* Initialization of scores changed to 1 instead for mutation
* Removed subtraction of -1 to score if no change states

### 4 September 2017
* Added logging into project
* Fixed bugs
* Issue with speed after trying it out with calculator
* New activities are now added to data structure
* activity_transition of buttons added to data structure

### 3 September 2017
* Changed to python3 for latest implementations.
* Changed key structure for node to score dictionary
* Addressed the structure of storage
* Added storing and loading of data structure in json format


### 30 August 2017
* Implemented supervised learning and labeling for the clicks done so as to glean for further information to classify them.
* Word to score ratio is being kept in a dictionary and stored in json format within a file.


### 21 August 2017
* `get_state()` of UI is done with index of xml dump.
* Added some random clicks and clicks with filling of text.
* The analysis of data(descriptions) is to be done, and will most likely be done using a database/RL style


### 17 August 2017
* Changing to python wrapper for UI automator for the dump method
* Using dump method of the current UI in order to `get_state()` of the current representation of the UI
* Will be doing analysis on words crawled from many APKs so as to do learning on the button descriptions

### 15 August 2017
* The UI Testing automation is done using [Appium framework](https://http://appium.io/)
* Currently able to obtain all relevant elements within the Android application using just the APK file to run.
* A basic test is implemented
    * Lacking a good way to `get_state()` of current activity.
    * The current method is to form a list of `resourceID` for all elements present on the activity and compare it with the previous state.

### TODO:
* `get_state()` of activity so that a _Dynamic Activity Transition Graph_ could be formed.
* Attempt using SCanDroid to obtain the _Static Activity Transition Graph_ so that accurate activity coverage could be measured
* Implement activity and method coverage

<!---
### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```



## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).

## Authors

* **Koh Hong Da** - *Initial work* - [PurpleBooth](https://github.com/lunalite)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
--->
