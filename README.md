# README

This repo contains a script that reads and prints out the contents
of places.sqlite database that Firefox uses to store bookmark and
history data.

Specifically the script only goes through the history and lists them out based
on when the link was visited. (Newer links first)

In the future, I'll be looking to update the script and generalise its
functions so that it can provide more utility. In the mean time do take note
of the limitations stated below and adjust accordingly as per your use case.

## Usage

The project requires **python 3.6+**. There are two ways of installing the
dependencies:

### Using Poetry (Recommended)

[Poetry](https://python-poetry.org/) is the dependency manager used in this project.
To install poetry, follow the instructions at: [link](https://python-poetry.org/)

Once installed, navigate to the project directory and run:

```
poetry install --no-root --no-dev
```
Poetry will create a virtual environment and install the dependencies there.

`--no-root` tells it to not install this project as a package

`--no-dev` prevents it from installing development dependencies.

To enter the virtual environment created, run:
```
poetry shell
```

### Using Pip

A **requirements.txt** file is provided in the case someone is using a different
dependency manager. The requirements.txt file includes the dev dependencies.
This section assumes that the user has created and activated a virtual environment
using their preferred tool.

To use pip to install the dependencies, run:

```
python -m pip install -r requirements.txt
```

### Executing the script

The script expects the path to the places.sqlite file to be passed as a command
line argument as so:

```
python main.py path_to_database_file
```

## Limitations

The script has a hardcoded value for the timestamp based on some analysis
I was carrying out. This means that the links fetched will only be
those after **2020-04-01 00:00GMT**. In the future I'll be looking
to generalise the script and make it more useful for a variety of use cases.

Also, it requires an API key to access the YouTube Data API. This is
used to retrieve the channel name and the video's title. Without, an
API key, the script won't function if it comes across a link to a
YouTube video.