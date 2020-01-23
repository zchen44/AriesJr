# AriesJr

A bot that uses computer vision libraries to play the game MapleStory. 
Currently the development environment utilizes a version of Maplestory hosted on a private server called AriesMS.

This project is both a homage to the game that brought me years of joy growing up and also an effort to learn new technical skills.

## Table of contents
* [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Setting Up Virtual Environment](#Setting-Up-Virtual-Environment)
  * [Using and Developing Important Note](#Using-and-Developing-Important-Note)
* [Contributing](#Contributing)
* [Future Plans](#Future-Plans)

## Built With
The project as of its current development state heavily relies on:
* Python ![python shield](https://img.shields.io/pypi/pyversions/pywin32)
* pywin32 ![pywin shield](https://img.shields.io/pypi/v/pywin32)

<a href="https://opencv.org/" target="_blank" rel="noopener noreferrer" />
<img src="https://dataset-academy.com/wp-content/uploads/2018/07/opencv_logo.png" alt="opencvlogo"/>
</a>

<a href="https://numpy.org/" target="_blank" rel="noopener noreferrer" />
<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/NumPy_logo.svg/200px-NumPy_logo.svg.png" alt="numpylogo"/>
</a>

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development purposes. This has yet to be anywhere near fully fleshed out for any production-like use cases.

### Prerequisites
pywin32 is a critical library for this project and only supports Python 2.7 and Python 3.5, 3.6, and 3.7.
As such I recommend downloading [Python 3.6.8](https://www.python.org/downloads/release/python-368/) as an executable from the hyperlink

[Git](https://git-scm.com/downloads) is also required for cloning this repo but also comes with git-bash which I used to set up my virtual environment to develop

MapleStory is obviously needed which can be installed through the [Nexon Launcher](https://games.nexon.net/nexonlauncher). \**AriesMS requires extra steps*

### Setting Up Virtual Environment
It's recommended to set up a virtual environment after you clone this repo so you don't get weird packages and versioning errors.
Here is a good article on [virtual environments](https://medium.com/@dakota.lillie/an-introduction-to-virtual-environments-in-python-ce16cda92853) if you're not too familiar with them.

Assuming you've downloaded Python 3.6.8 already and Git, you can open up Git Bash and move to a directory where you want to clone this repo with and run
```
git clone https://github.com/zchen44/AriesJr.git
```
Go into the directory
```
cd AriesJr/
```
Create a virtual environment (in this case the virtual environment will be called .venv since it plays nice with VSCode which I use as an editor)
```
python -m venv .venv
```

Once the virtual environment has been created you'll need to activate it everytime you want to do things within it (this includes developing) and deactivate it when you're not using it.

To activate the virtual environment use
```
source .venv/Scripts/activate
```
which will then include (.venv) tag after every command

Here we will want to install all the dependencies and packages we need so run
```
pip install -r requirements.txt
```
To deactivate the virtual environment when finished simply just run
```
deactivate
```

### Using and Developing Important Note
This script currently sends scan codes to the kernal as any game that uses the DirectX library (which includes MapleStory) will ignore virtual key presses.
Thus one of the requirements when running the script is to have whatever interactive run the script be **Run as administrator**. 
Only then, does the script have permission to send scan codes to the kernal.

## Contributing
Please read [CONTRIBUTING.md](https://github.com/zchen44/AriesJr/blob/develop/CONTRIBUTING.md) for the branching model, and the process for submitting pull requests.

## Future Plans
* I want to eventually maybe set up a Jira board to keep track of tasks (Also seeing as a lot of companies use this, would be wise to familiarize)
* Expand the bot capabilities to set up start to finish without human interaction
* Possibly run this within docker containers so that it will free up host machine for other purposes
* Set up logging and capture significant amount of images for maybe a machine learning project
