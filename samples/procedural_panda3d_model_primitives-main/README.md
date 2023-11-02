# Procedural model primitives for Panda3D

By default, there is little available in the [Panda3D game engine](https://www.panda3d.org/) in terms of 3D geometry, ready for quick prototyping. Your options are pretty much limited to using the `CardMaker` class to generate a flat, rectangular model (a so-called "card"), or loading up one of the pre-made models shipped with the engine (e.g. the "smiley" model if you want a sphere).

Artists may prefer to prototype models in their modeling program of choice, but others might find it more convenient to do away with the hassle of having to export/import model files and instead type a few lines of code to immediately produce simple but effective placeholder geometry.

This project is an attempt to provide Panda3D users with a means to create basic -- but very customizable -- model types (box, sphere, cylinder, cone and torus) at runtime through code.  
To this end, several classes have been implemented that allow the user to generate models of specific types, each with a plethora of options which can dramatically alter their default shape.

## Requirements

The [Panda3D game engine](https://www.panda3d.org/).

## Usage

Simply move the `procedural3d` directory to your project source code.  
The included `main.py` script should give you an idea of how to use the provided model-generation classes.
