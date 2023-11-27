#!/bin/sh

mkdir -p build
cd build
cmake -G "Unix Makefiles" \
    -DCMAKE_INSTALL_PREFIX=/panda3d-kphys/lib/python3.10/site-packages \
    -DBULLET_INCLUDE_DIR=/root/jenkins/workspace/bullet-lynx64/dist/bullet/include \
    -DBULLET_LIBRARY_DIR=/root/jenkins/workspace/bullet-lynx64/dist/bullet/lib \
    -DINSTALL_PY=ON \
    -DPANDA_BINARY_DIR=/root/jenkins/workspace/panda3d-lynx64/dist/panda3d/bin \
    -DPANDA_INCLUDE_DIR=/root/jenkins/workspace/panda3d-lynx64/dist/panda3d/include \
    -DPANDA_LIBRARY_DIR=/root/jenkins/workspace/panda3d-lynx64/dist/panda3d/lib \
    -DPYTHON_INCLUDE_DIR=/root/jenkins/workspace/python-lynx64/dist/python/include/python3.10 \
    -DPYTHON_EXECUTABLE=/root/jenkins/workspace/python-lynx64/dist/python/bin/python3.10 \
    -DPYTHON_LIBRARY=/root/jenkins/workspace/python-lynx64/dist/python/lib/libpython3.10.so.1.0 \
    ..

make
make install DESTDIR=../dist/

cd ..
