Custom Deferred Render Pipeline for Panda3D
===========================================

Deferred Render Pipeline for the Panda3D game engine
originally made for the KITSUNETSUKI project game.

KITSUNETSUKI project: https://k.kitsune.one/

Conda package: https://anaconda.org/kitsune.ONE/panda3d-krender


Features
--------

* rplight compatible lighting and shadowmapping system


Building requirements
---------------------

* CMake
* [Panda3D](https://www.panda3d.org/) (full package with headers, not pip package)


Building python package
-----------------------

```
pip wheel --no-deps .
pip install *.whl
```


Building conda package
----------------------

```
git clone https://github.com/kitsune-ONE-team/panda3d-krender.git
conda build .
conda install panda3d-krender --use-local
```


Installing prebuild conda package
---------------------------------

```
conda config --add channels kitsune.one
conda install panda3d-krender
```
