# Subotai

*Subotai* is a tool for automating tasks. The intended use is to let people automate or batch process 'every day repetitive tasks' without having to know how to code. 

Some example uses are:
* Batch processing folders with images
* Automatically uploading files from a watch folder
* Executing long running processes (rendering, media conversion, etc) and receiving notifications when complete

*Subotai* uses a node-based interface to represent tasks and data flow. If additional capabilities are required that cannot be handled, it's easy to write a new nodes to add the features. Take a look at the [Wiki](https://github.com/VickenM/Subotai/wiki/Subotai-Wiki) or [Subota-extras](https://github.com/VickenM/Subotai-extras) for additional examples on creating new nodes.

![alt text](https://github.com/VickenM/Subotai/blob/master/resources/screenshot.png?raw=true)

> **_NOTE:_** The project is under active development with large parts subject to change. 

# Requirements
* Python 3.10–3.14 (64-bit)
* PySide6 6.11.2 (Qt 6)

The Qt 6 migration has been tested on Windows with Python 3.12. Linux and macOS have not been verified.

# Installation
Use a supported Python version to create a fresh environment; do not reuse the old Python 3.9/PySide2 environment.

From the project directory in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe subotai.py
```

On Linux/macOS, use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.

The requirements contain the application's runtime dependencies. Development tools such as IPython and PyInstaller are optional and are no longer installed with the application. PySide6 installs its matching Shiboken and Qt packages automatically.

## Updating custom nodes

Existing JSON workflows keep their format. Add-ons loaded through `SUBOTAI_ADDONS` must use `PySide6` imports. Qt actions and undo classes now live in `QtGui` (`QAction`, `QUndoCommand`, `QUndoStack`); custom Qt code may also need Qt 6 API updates. Do not mix PySide2 and PySide6 objects in the same application.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The integration suite uses Qt's offscreen platform. It checks all 44 built-in node types, loading/saving/rendering all six example graphs, hello-world signal execution, undo/redo, boolean parameters, toolbox filtering, zoom, and Pillow-to-Qt images. Example event nodes are disabled during loading so tests do not run file operations, processes, HTTP requests, or email.

Some existing nodes still print diagnostics for image parameters and incomplete math inputs, and asynchronous nodes can report unclosed event loops during teardown. These are outside the Qt API migration; the suite does not validate external services or full automation lifecycle behavior.
