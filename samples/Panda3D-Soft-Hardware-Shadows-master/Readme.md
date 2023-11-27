Soft Hardware Shadows in Panda3d
================================

This is a (minimal) example project showing how to use Hardware Shadow Map Filtering to get (slightly) softer shadows in Panda3D.
It is built around shader code originally supplied by "wexu" here: https://discourse.panda3d.org/t/shadows-made-easy/15399

At the time of writing, Panda3D does not seem to initialize the samplerCubeShadow to use Shadow Map Filtering, so the sample includes code which enables this filtering mode 'manually' (see function `toggle_texture_filter_mode`). Note that this function cannot be run right after creating the light source, probably because Panda requires time to set up the shadow buffer before we can retrieve it to change the filter modes.


