# Aelib

A library of Digital Assets, Tools and Scripts for SideFX Houdini.

The /otls folder contains approximately 100 SOP level HDAs which are available from the 'aelib' Tab submenu. These are categorised into the following sections:

* Creators: Geometry creation SOPs, usually not requiring input geometry
* Deformer: Modify geometry positions
* Modify: Involve creating or destroying points/primitives and require input geometry
* Curves: A variety of tools acting on polyline curves
* IO: Operations for reading or writing files to disk
* Solvers: Simulations and feedback loops
* Utility: General purpose tools and miscellaneous items
* Extensions: Similar to existing Houdini or 3rd-Party SOPs but with extra functionality

As well as the HDA collection, Aelib includes:
* A shelf containing macros and useful python scripts
* Several VEX include files adding a range of new functions
* A VEXpressions.txt file which adds presets to wrangles
* Bundled python2.7 libraries required for a small number of SOP nodes

## Usage

The /examples directory contains hip files demonstrating usage of many of the Aelib SOPs. Each node also includes a help card detailing its inputs, parameters and behaviour. Many parameters include a rollover tooltip.

There are plans to add a github wiki to this repository, but it has not yet been implemented!

## Installation (Houdini 17.5+)

* Download and extract the repository and move it to any location
* Create a folder called 'packages' in your Houdini home directory (e.g C:/Users/MY_USER/Documents/houdini18.0) if it does not exist already
* Copy the Aelib.json file into the packages folder
* Edit the json file to point to the Aelib parent directory (edit the "AELIB" line)
* For more information on how package files work, see [HERE](https://www.sidefx.com/docs/houdini/ref/plugins.html)

## Other

HDAs are periodically removed from the main library due to being superceded by new Aelib nodes or new Houdini nodes. These are kept in /otls/archive

If you would like to support the development of Aelib you can subscribe on [Patreon](https://www.patreon.com/aeoll) Feedback and bug reports are always welcome!

This library is been heavily inspired by [qLib](https://github.com/qLab/qLib)
qLib is an incredible resource and I would highly recommended installing and exploring it.