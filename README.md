# UI Testing - Reinforcement Learning

Project is on-going

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.
(TODO)

## Updates

### 21 August 2017
* `get_state()` of UI is done with index of xml dump.


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
