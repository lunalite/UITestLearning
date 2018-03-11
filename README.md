# UI Testing - Deep Learning

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Prerequisites

The following are required for the entire project to be deployed:
* Android SDK (the following shows `sdkmanager --list`)

|Path                                               |Version    |
|---------------------------------------------------|-----------|
|build-tools;26.0.1                                 |26.0.1     |
|emulator                                           |27.1.12    |
|extras;intel;Hardware_Accelerated_Execution_Manager|6.2.1      |
|patcher;v4                                         |1          | 
|platform-tools                                     |27.0.1     |
|system-images;android-26;google_apis;x86           |8          | 
|tools                                              |26.1.1     |
* Python 3.6 (currently Python 3.6.4 is used)
* OS must be able to run virtual machines.

## Deployment of crawler

1. Install android SDK
    You can get android SDK by installing [Android Studio](https://developer.android.com/studio/index.html) or by doing it the [manual way](https://github.com/codepath/android_guides/wiki/Installing-Android-SDK-Tools). 
    
    The manual way of installation is as follow:
        
    ```bash
    wget https://dl.google.com/android/repository/sdk-tools-darwin-3859397.zip -P /tmp/;
    unzip /tmp/sdk-tools-darwin-3859397.zip -d ~/android-sdk;
    cd ~/android-sdk/tools/bin;
    yes | ./sdkmanager --licenses;
    ./sdkmanager --update;
    ./sdkmanager "build-tools;26.0.1";
    ```

2. Setup the environment for adb, emulator
    Add the environment variable ANDROID_HOME by finding out where the android sdk home is located.

    ```bash
    export ANDROID_HOME=~/android-sdk
    ```
    
3. run pip install requirements 
    ```bash
    pip install -r requirements.txt
    ```
4. Create emulators
    Find the sdkmanager within `$ANDROID_HOME/tools/bin`
    ```bash
    $ANDROID_HOME/tools/bin/sdkmanager "system-images;android-26;google_apis;x86"
    ```
    This is done to install the relevant package image which is used to set up the Android emulator. Do note that you can use your own preferred image in this case. To list the available images, just run
     
    ```bash
    $ANDROID_HOME/tools/bin/sdkmanager --list
    ```
    
    The next step is to create an Android Virtual Device (AVD) for the emulator using the preset image.  
    ```bash
    echo no | $ANDROID_HOME/tools/bin/avdmanager create avd -n avd0 -b x86 -k "system-images;android-26;google_apis;x86" --abi google_apis/x86 
    ```
    In our case, we name it `avd0`. Do take note of the name as we will be using it later on.
    
    Try running the emulator to see if it works.
    ```bash
    $ANDROID_HOME/emulator/emulator -avd avd0
    ```
    
    If the following error occurs: `PANIC: Broken AVD system path. Check your ANDROID_SDK_ROOT value`, check that in your android-sdk folder, there contains the following directories: `emulator`, `platforms`, `platform-tools`, `system-images`. If any of the following doesn't exist, just make an empty directory. More information can be found [here](https://stackoverflow.com/questions/39645178/panic-broken-avd-system-path-check-your-android-sdk-root-value). 

5. Running the Python program
    Do note that `sudo` permissions might be needed for running all of the following due to the usage of kvm for the emulator in the case that no screen is provided, so install the following within the `sudo` environment.
    ```bash
    cd crawler && export PYTHONPATH=..; python3 main.py emulator-5554 ../../apk/apk-0 ../../apk2/ avd0 
    ```
## Extracting useful data for learning
Prior to running any learning models, it is vital for the data collected to be parsed into its respective format so that learning can be done. There are several areas where we could parse data from to obtain important information that will be used later during the learning of model.

1. Extracting data from database
    ```bash
    sh dataparsing/extract_db.sh #(number of db) && mv clickable*.json ../data/serverdata
    ``` 
    Due to the nature of work, the data collected which is stored into the database will get exponentially slower over time as the database collection gets filled up. Thus, we have decided to change the database collection every now and then to improve the efficiency of collection. Running the `extract_db.sh` shell file will export and dump the required `clickablen.json` files into the current folder. These files are required to be located in the data/serverdata folder for further parsing.

2. Extracting features from `PlayStore_Full_2016_01_NoDescription_CSV.csv`
    ```bash
    python3 feature_extract.py 
    ```
    This will extract all important features from the .csv file containing the application category into a `category.txt` file within the `data/serverdata` folder. the .csv file must be located within the `data/serverdata` folder as well. This will be used for running classification using a logistic regression or a wide and deep model.
    
3. Extracting image dimension of the screenshots
    ```bash
    python3 img_dimension_extract.py && cp img_dimension_extract.txt ../data/serverdata
    ```
    This extracts all image dimension from the screenshot taken during the testing. The image dimension will be further used in determining the position of the clickable elements and will be used in either the logistic regrssion or wide and deep model.
 
4. Extracting sequences
    ```bash
    find . -name 'seqq*.txt' -exec cp {} folder \; 
    python3 sequence_extract.py folder && cp sequence*.txt ../data/serverdata
    ```
    Copy and extract all the sequence text files into a single folder then use `dataparsing/sequence_extract.py` to extract these sequences into two files, `sequence-combination-wnd.txt` and `sequence-combination.txt`. These sequences will be used for RNN model and wide and deep model, and should be stored in the `data/serverdata` folder.
    
5. Parsing data from database
    ```bash
    export PYTHONPATH=..; python3 parseJson ed
    ```
    All database files will be collected and parsed through using the 'e' argument. It will then be split into positive and negative data based on the user's requirement.
    'n': normal sequence tree where 
    'd': double sequence tree
    'r': relaxed version of double sequence tree  
    The eventual result will be stored into `pdata.txt` and `ndata.txt` which would be used for fastText implementation. 
    

## Running the learning model

There are several options which the user could use in running deep learning:
1. [fastText](https://github.com/facebookresearch/fastText) from Facebook
    We have implemented `parseJson.py` which allows for the data to be parsed into the format required for running text classification or sentiment analysis using the fastText implementation.
      
    ```bash
    python3.6 parseJson.py f
    ```
    
    The required data will be in the `data` folder, containing the files `fastTextTrain.txt` and `fastTextTest.txt`. To run the sentiment analysis:
    
    ```bash
    fasttext supervised -input ./fastTextTrain.txt -output model -lr 0.05 -dim 10 -epoch 10 -minCount 1 && fasttext test model.bin ./fastTextTest.txt 1
    ```
    
2. Recurrent Neural Network (RNN), LSTM using Tensorflow
    The next implementation uses LSTM from Tensorflow. To train the model, we will have to first parse the sequence data.
    
    ```bash
    sh gen_tt.sh 1 9
    ``` 
    
    This will run generate_traintest.py in parallel for n-grams stemming from 1-gram to 9-gram.
    
## Limitations

The crawler is unable to test certain APKs like those of other languages which contain characters that are non-ASCII, or those like the application 'Power Me Off' since it might shut down the entire emulator.
There are also cases of flash games which do not contain any element with the variable `clickable:True`, and applications requiring login and registration before one could proceed crawling the application.

Examples of such APKs
* at.alladin.rmbt.android_20214.apk - no clickable buttons


## Updates
*** 11 March 2018
* Updated README.md to make it look neater.
* Removed irrelevant files.
* Added run_wnd.sh to facilitate running of training_model
* Changed epoch to 5

### 9 March 2018
* Edited gen_tt.sh to run concurrently

### 8 March 2018
* Randomized selection of train data and increased training epochs.
* Added wide and deep implementation to widenrnn.py to find out reason for low accuracy rate
* Fixed issue with low accuracy rate (due to double softmax)

### 7 March 2018
* Added NA for btnclasses that aren't within the field.
* Fixed learning for wide n deep model.
* Edited max seq length to be grams if not using iw
* Fixing little bugs for wide n deep model to run proper. 

### 6 March 2018
* Changes to the way idslabel are being formulated to improve accuracy.
* Added function to save and load np so as to reduce debugging time 

### 5 March 2018
* Minor updates

### 1 March 2018
* Fixed issue with gen_embedding.py
* Fixed issue on the training batch

### 28 February 2018
* Solved the issue of wide and RNN model. Now tweaking to find the best possible accuracy.

### 7 February 2018
* Improved generation of data set for wide model to match with deep model.
* Started on doing wide logistic regression model using lower level method.  
* Changed positioning to 3:5 or 5:3 depending on whether it is 480:800 or 800:480. Also, if image size is any different, consider the old method of 3:3.

### 6 February 2018
* Added implementation to gather button state from sequences as well.
* Dataset 12
* Changed implemenetion for newline in sequence extraction to \_NEWLINE\_ for easier parsing
* Changed name for wnd-test.txt in the usage of wide model to just w-test.txt and w-train.txt, saving the naming for wnd-train.txt for wide and deep model instead.  

### 1 February 2018
* Logistic regression trained.
* Added sys arg support for easier usage. 
* Added testing of model for RNN and returning the accuracy onto a file 
* Added implementation for RAND_BUTTON, BACK, SCROLL UP, SCROLL DOWN, FLING HORIZONTAL in the case of gen_embedding
* Added function for turning all null sequence to invalid

### 30 January 2018
* Added positional conversion.
* Added RNN split as individual words using space as delimiter without taking into account punctuations

### 29 January 2018
* Reorganized the directory into respective packages.
* Added a ./run.sh file to make things simpler
* dataset11
* added img dimension extract file

### 24 January 2018
* Used Gensim to create word embedding of the dataset 

### 22 January 2018
* Minor changes to sequence_extract.py 

### 17 January 2018
* Added method to prepare sequence data for forming of word embeddings

### 16 January 2018
* Prep data for wide and deep model

### 14 January 2018
* Changed directory for screenshot files
* Changed directory for seqq files
* Changed to database 8
* Check if screenshot/dump is present, if present, dont re-dump again

### 12 January 2018
* Added in a RELAXED version for DST
* Added in categoristic addition of feature
* Added script for finding max F1 in fasttext classification

### 11 January 2018
* Edited parsing method for double NST and single NST

### 4 January 2018
* Changed data collection method, include sequential 
* Initialize score to -1 instead of 1 since we are not using score for exploration
* Using dataset6 now for database
* Changed to dataset7 b/c of mistake in appending 1/-1 to initial score

### 14 December 2017
* Using totally random decision of clicking buttons for exploration
* Increased the iterations to make deeper exploration

### 13 December 2017
* Realized there's a lot of None in next_transition_state. Might have to retweak the code a bit 

### 11 December 2017
* Tweaked the parseJson.py for text.

### 16 November 2017
* added storing of data for text. The method of getting state remains unchanged.
* Stopped closing the android keyboard for it is causing a different state everytime and is non-deterministic.
* added discriminator for buttons leading to outside the apk  

### 15 November 2017
* emulator is restarted after 50 counts instead.
* Started data parsing of JSON format from mongodump

### 10 November 2017
* Added functionalities to restart emulator after 5 counts of app testing. 

### 4 November 2017
* Socket timeout issue persists. Changed TimeoutError back to BaseException, added signal alarm at btn_to_info method and set it to 5 seconds. 

### 3 November 2017
* Added catch error for fail to click

### 2 November 2017
* Taken care of socket timeout error. Restart the entire APK if socket timed out.
* Fixed issue regarding repeated horizontal scrolls
* Reduction of rerolling random click button tries
* Changed state_info for scrolling decision from None to APP_STATE.SCROLLING
* Fixed bug of not adding increment to counter when trying to get another random btn to click
* Fixed issue with NoneType error

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
