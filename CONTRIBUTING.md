# How to Contribute

## Basic Function
A foreground UI python script starts with [main.py](https://github.com/smgoldade/realkey/blob/main/main.py). build123d is mocked out in this environment to keep load times to a minimum.
A background worker script starts with [worker.py](https://github.com/smgoldade/realkey/blob/main/worker.py), which receives requests from the foreground UI to do the heavy lifting. This background worker takes quite a bit of time to load as it needs to fetch build123d and other packages needed by build123d.

Classes that extend [Key](https://github.com/smgoldade/realkey/blob/main/src/realkey/key.py) register themselves with the internal list.
This internal list is used to show available keys to generate on the interface which exists at [tab_key.py](https://github.com/smgoldade/realkey/blob/main/src/realkey/tab_key.py).

## Adding a Key
### Initial File Creation
Follow existing directory structure.

For each key type, add a class that extends [Key](https://github.com/smgoldade/realkey/blob/main/src/realkey/key.py)

All methods besides blank and key should NOT USE build123d or any other heavy library.

Implement each method:
- **tag** - this defines an internal, non-user seen name used to tag the key family. Make it unique for your key, in snake_case. An example would be "miwa_sr" or "schlage_classic" and not "miwa" or "SchlageClassic".
- **display_name** - this is the display name for the key type, shown to the user. E.g. "ASSA Desmo"
- **profiles** - returns a dictionary of key profiles. The outer dictionary is profile groupings to an inner dictionary. A blank group displays no group. The inner dictionary keys are unique and used by your code to figure out which profile is requested, the value for the key is the display name for that profile. E.g. ```python {"Group Name" : {"6pin" : "6-Pin", "7pin" : "7-Pin"}} ```
- **keyways** - returns a dictionary of keyways. The outer dictionary is keyway groupings to an inner dictionary. A blank group displays no group. The inner dictionary keys are unique and used by your code to figure out which keyway is selected, the value is the display name for that profile. ```python {"Group Name": {"c" : "C", "e" : "E"}} ```
- **basic_bitting_definition** - returns a string that describes the rules for the bitting string. It's helpful to provide the range of cuts and amount necessary to generate a working key. HTML can be used to help spice up the information displayed.
- **advanced_bitting_definition** - if a string is returned, it becomes the HTML that lives inside an popover, designed to provide as much information as may be necessary to define the bitting of the key. See the MIWA SR for a good example.
- **validate_bitting** - validates if the bitting will generate an allowable key. Raise an exception (ValueError or similar) if an invalid bitting is specified, with a reason as the error message to provide the user.
- **blank** - generate a blank for the given profile and keyway. This can be done by loading a model file from resources, extruding SVGs, or even entirely in code, entirely up to the developer.
- **key** - generates a key for a given profile, keyway, and bitting. Typically calls validate_bitting and blank right away, and then beforms boolean geometric operations on the blank to generate the final key model

### Making the Key Show Up
Make sure the python package is imported in both [tab_key.py](https://github.com/smgoldade/realkey/blob/main/src/realkey/tab_key.py) and [worker.py](https://github.com/smgoldade/realkey/blob/main/worker.py)

### Config!
Make sure your python files are in [config.json](https://github.com/smgoldade/realkey/blob/main/config.json).

Use lazy resource fetching utilizing [resource_fethcer.py](https://github.com/smgoldade/realkey/blob/main/src/realkey/resource_fetcher.py)

### Development Tips
Use vscode with ocp_vscode to help develop new keys! You will see a main execution at the bottom of most key python files that uses ocp_vscode, which allows you to quickly run a key file and view the generated output from within vscode without having to spin-up the whole web setup, allowing for quicker prototyping and development.