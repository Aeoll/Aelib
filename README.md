# Aelib

A library of Digital Assets, Presets and Scripts for SideFX Houdini.

## Installation

* Download the repository
* Extract and move into the Houdini config directory
* Append the provided houdini.env file to your own houdini.env

Evironment variables used:
* HOUDINI_OTLSCAN_PATH: the assets
* HOUDINI_GALLERY_PATH: gallery items
* HOUDINI_TOOLBAR_PATH: shelf tools
* HOUDINI_SCRIPT_PATH: scripts
* HOUDINI_VEX_PATH: custom Vex files (required in some assets) 

## Other

The structure of this library is inspired by qLib - a large open source Houdini library - https://github.com/qLab/qLib
Most of the assets found in Aelib will work in isolation. However, a few tools do make use of qLib so it is highly recommended that this is installed alongside Aelib.