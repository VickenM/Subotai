# Subotai

*Subotai* is a tool for automating tasks. The intended use is to let people automate or batch process 'every day repetitive tasks' without having to know how to code. 

Some example uses are:
* Batch processing folders with images
* Automatically uploading files from a watch folder
* Executing long running processes (rendering, media conversion, etc) and receiving notifications when complete

*Subotai* uses a node-based interface to represent tasks and data flow. If additional capabilities are required that cannot be handled, it's easy to write a new nodes to add the features. Take a look at the Wiki (coming soon) or [Subota-extras](https://github.com/VickenM/Subotai-extras) for additional examples on creating new nodes.

![alt text](https://github.com/VickenM/Subotai/blob/master/screenshot.png?raw=true)

> **_NOTE:_** The project is under active development with large parts subject to change. 

# Requirements
* Python 3.9 

Note: All dependency packages of *Subotai* are cross platform, however *Subotai*  has only been tested under Windows 10. Compatibility with Linux and OSX currently cannot be guaranteed. 

# Installation
1. python -m virtualenv c:\temp\subotai-env
2. c:\temp\subotai-env\Scripts\activate
3. git clone https://github.com/VickenM/Subotai.git 
4. cd Subotai
5. python -m pip install -r requirements.txt
6. python subotai.py
