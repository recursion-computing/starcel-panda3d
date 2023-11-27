cmake_minimum_required(VERSION 3.10)
project(panda3d-kphys)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_DISABLE_IN_SOURCE_BUILD ON)
set(CMAKE_INSTALL_RPATH "$ORIGIN/../../..")

if(WIN32)
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS}")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
  add_definitions("/wd4996 /wd4275 /wd4267 /wd4101 /wd4273")
else()
  set(CMAKE_C_FLAGS "${CMAKE_CXX_FLAGS} -fPIC")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fPIC -std=c++11")
endif()

if(EXISTS "${PYTHON_LIBRARY}")
else()
  find_package(PythonInterp 3.2 REQUIRED)
  find_package(PythonLibs 3.2 REQUIRED)
endif()
include_directories(${PYTHON_INCLUDE_DIR})

if(EXISTS "${BULLET_LIBRARY_DIR}")
  set(BULLET_COLLISION_LIBRARY BulletCollision)
  set(BULLET_DYNAMICS_LIBRARY BulletDynamics)
  set(BULLET_MATH_LIBRARY LinearMath)
  set(BULLET_SOFTBODY_LIBRARY BulletSoftBody)
  link_directories(${BULLET_LIBRARY_DIR})
else()
  find_package(Bullet REQUIRED)
endif()
include_directories(${BULLET_INCLUDE_DIR}/bullet)

set(IK_PATH thirdparty/ik)
set(IK_LIB_TYPE "STATIC" CACHE STRING "SHARED or STATIC library" FORCE)
add_subdirectory(${IK_PATH} EXCLUDE_FROM_ALL)
include_directories(${IK_PATH}/include/public)

if(EXISTS "${PANDA_LIBRARY_DIR}")
else()
  find_path(PANDA_INCLUDE_DIR NAMES panda3d/pandaSystem.h)
  find_path(PANDA_BINARY_DIR NAMES interrogate interrogate.exe)
  find_library(PANDAFRAMEWORK_LIBRARY_PATH NAMES libp3framework.so libp3framework.lib p3framework.lib)
  get_filename_component(PANDA_LIBRARY_DIR ${PANDAFRAMEWORK_LIBRARY_PATH} DIRECTORY)
endif()
include_directories(${PANDA_INCLUDE_DIR}/panda3d)
link_directories(${PANDA_LIBRARY_DIR})
if(WIN32)
  set(INTERROGATE ${PANDA_BINARY_DIR}/interrogate.exe)
  set(INTERROGATE_MODULE ${PANDA_BINARY_DIR}/interrogate_module.exe)
else()
  set(INTERROGATE env LD_LIBRARY_PATH=${PANDA_LIBRARY_DIR} ${PANDA_BINARY_DIR}/interrogate)
  set(INTERROGATE_MODULE env LD_LIBRARY_PATH=${PANDA_LIBRARY_DIR} ${PANDA_BINARY_DIR}/interrogate_module)
endif()

if((EXISTS "${PANDA_LIBRARY_DIR}/libpandabullet.so") OR (EXISTS "${PANDA_LIBRARY_DIR}/libpandabullet.lib"))
  # makepanda build
  if(WIN32)
    set(PANDA_PREFIX "lib")
  else()
    set(PANDA_PREFIX "")
  endif()
  set(PANDA_LIBS
    # PRIMARY
    ${PANDA_PREFIX}p3framework
    # COMMON_PANDA_LIBS
    ${PANDA_PREFIX}panda
    ${PANDA_PREFIX}pandaexpress
    # COMMON_DTOOL_LIBS
    ${PANDA_PREFIX}p3dtool
    ${PANDA_PREFIX}p3dtoolconfig
    # EXTRA
    ${PANDA_PREFIX}p3direct
    ${PANDA_PREFIX}p3interrogatedb
    # PANDABULLET
    ${PANDA_PREFIX}pandabullet)

else()
  # cmake build
  set(PANDA_LIBS
    # PRIMARY
    p3framework
    # COMMON_PANDA_LIBS
    panda
    pandaexpress
    # COMMON_DTOOL_LIBS
    p3dtool
    p3dtoolconfig
    # EXTRA
    p3direct
    p3interrogatedb
    # PANDABULLET
    p3bullet)
endif()

include_directories(${CMAKE_SOURCE_DIR})
add_subdirectory(kphys)
