# [realkey](https://tannermidd.github.io/realkey/)
A Python project devoted to generating 3D models for keys.  

## Purpose
realkey started as a project designed to generate 3D-printable keys for locks without easily available blanks. The first key designed was for the Paclock 90A-PRO, and the library has expanded from there as need demands.
Blanks for keys may be hard to get either due to location or restriction making it hard to key up your favorite lock, and this project hopes to help solve that problem!

## How It Works
The primary idea is contained in the [Key](https://github.com/smgoldade/realkey/blob/main/src/realkey/key.py) class, which defines methods that key types should implement.
Key models are built up using [build123d](https://github.com/gumyr/build123d), outputting build123d Parts for keys.
The entire setup is designed to run locally in a web browser. 
The front end uses [Pyscript](https://pyscript.net) to load defined keys and allow the user to generate models as needed, exporting to the formats build123d supports.

## Current application

The browser app now includes the first three product phases:

- **Trustworthy generation:** worker-enforced follower validation, corrected key-family rules, unique job exports, stale-result protection, recoverable errors, and regression tests.
- **Workspace experience:** an accessible responsive UI, efficient 3D preview, input-time validation, local workspace restore, and privacy-safe fragment sharing. Shared links never auto-run CAD; recipients review them first.
- **Fabrication intelligence:** editable printer/material profiles, build-volume and layer checks, honest reporting when wall or feature measurements are unavailable, and STL, STEP, and 3MF exports.

Fabrication reports are conservative profile comparisons, not a guarantee that a part is safe, printable, durable, or dimensionally correct. Verify the sliced toolpath, material behavior, dimensions, orientation, and fit before use.

## Run locally

Serve the repository root over HTTP; opening `index.html` directly does not provide the browser worker and resource behavior the app expects.

```bash
python -m http.server 8765
```

Then open `http://localhost:8765/`. The first load downloads the pinned PyScript CAD runtime and can take longer than subsequent interactions.

## Test

```bash
python -m pip install "pytest>=8.3,<9"
PYTHONPATH=src python -m pytest -q
```

On PowerShell, use `$env:PYTHONPATH = "src"` before the pytest command. CI runs the same dependency-light regression suite and source checks on every push and pull request.

## Technical Documentation
Explore the [interactive engineering dossier](https://tannermidd.github.io/realkey/architecture/) for the complete system architecture, runtime lifecycle, supported key families, follower engine, resource pipeline, security boundaries, quality assessment, and maintainer reference. A shareable [Word handbook](docs/RealKey_Technical_Documentation.docx) is also included in the repository.

## How It's Organized
The conceptual idea behind the key taxonomy is as follows:
- A singular key is defined by a bitting, keyway, profile, and type.
- **Bitting** is a unique code that links a key to a lock, typically a numeric code specifying the cuts to be made. *E.g. "145762"*
- **Keyway** defines the shape of the portion of the key that enters the lock. Some locks may come with a variety of different keyways. *E.g. C*
- **Profile** defines the shape of the entire key from a profile view. This commonly is different between different pin count versions of the same lock type. *E.g. 6-pin*
- **Type** defines the specific lock or lock family that the key works for. *E.g. Schlage Classic*

## Inspiration
Several other projects served as inspiration:
- [Eric Van Albert's keygen](https://github.com/ervanalb/keygen)
- [Reinder's 3D Printing Keys](https://github.com/reinder-s/3d-printing-keys/tree/main)
- [Christian Holler's AutoKey3D](https://github.com/choller/autokey3d)
