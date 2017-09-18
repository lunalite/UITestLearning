# UI Testing - Reinforcement Learning

Project is on-going

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
(TODO)

## Updates

<!--
TODO:

2) to collect child nodes as well
discriminiation between what is filled in and what is generated by system
contextual meanings (siblings/parents/children) e.g. 1-away
relationship distance = 1
== Really slow process

3) Optimization of the for loops
4) Use database MongoDB
5) consider english language apps only
    = ASCII - determine if the current app is english or not 
list of data for what will be collectedz

6) Consider subtracting score if button is being pressed simultaneously at the same time

literature review of model for sentimental analysis-like analysis 
twitter-like NN model

Consider using database MongoDB

Why would it stop halfway?
d() keeps to package_name of the application itself
!-->

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

## Deployment

Add additional notes about how to deploy this on a live system

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
