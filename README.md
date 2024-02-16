# Starcel-Panda3D
A 3D Multiplayer Python IDE and Desktop Environment

![](images/4.png)
![](images/1.png)
![](images/2.png)
![](images/3.png)

### Included Python Libraries
black -> isort -> ssort -> ruff -> pyright-> pytest\
fast-autocomplete, rapidfuzz,\
panda3d, [renderpipeline](https://github.com/tobspr/RenderPipeline),\
xarray, numpy, pandas, h5py, pytensor, cupy(awaiting update), cupy_xarray(awaiting update),\
scipy, opencv, scikit-learn, sympy, mpmath, sagemath-standard, pymc, py4j,\
astropy, pint, unyt, softposit, pendulum, more-itertools, plumbum, cmdix, dill, limeade, hy,\
fastapi, uvicorn[standard],\
datashader, bokeh, matplotlib, seaborn,

### Included CLI Tools
* Everything and ES CLI for quickly searching the Windows file system
* WinPython: Not intended for use with StarcelPy - IDLE, IPython QT Console, Jupyter, Pyzo, QT, Spyder, VS Code

### Notes
Ursina would've been nice to use for the extra functions, improved readability, and new networking library, but I was unable to find a physically-based renderer that would consistently work with it.
There is a bug I had to work around with the M_Relative that should be fixed in Panda3D 11.0. 
The releases section will eventually include Starcel packaged with WinPython. 
This repo is a fork of the RenderPipeline repo because the startup image and environment hdri cannot be changed at runtime. Otherwise you should be able to just copy the Starcel folder if you were planning on trying to build renderpipeline from scratch. I have included every existing usable sample I could find for Panda3D(1/1/2024) and renderpipeline. 
I have not spent the time to find the bounds of the simulation. I know we are much more limited than in the UE5 version of Starcel, so you may run into errors if you make your character too small, speed too high, etc. 
You should be able to launch a dedicated server and port forward Starcel in your router just as you would any other game.
Most of the features you saw in the UE5 version of Starcel are possible in this version of Starcel. With time they will be implemented and improved.
A major refactor is coming soon. I usually write a bunch of code until I get it into a state I consider working and then I prune away all the excess code I commented out during testing, I fix the variable names, and I refactor the code into proper files. 
This project is entirely open source, so maybe you'll get to the refactor before I do. 
Feel free to submit any pull request and I might adopt your changes. 

Panda3D can be installed from https://docs.panda3d.org/1.10/python/introduction/installation-windows and you may want to include a file 

Run the program by running both ```python render_pipeline\samples\Starcel\server.py``` and ```python render_pipeline\samples\Starcel\client.py``` you can run as many clients as you want, but full replication of those clients is currently a WIP. 