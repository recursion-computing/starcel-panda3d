if(${INSTALL_PY} MATCHES "ON")
  install(
    FILES
    __init__.py
    loader.py
    viewer.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}/kphys
    PERMISSIONS
    OWNER_READ OWNER_WRITE
    GROUP_READ
    WORLD_READ)
endif()

add_subdirectory(core)
