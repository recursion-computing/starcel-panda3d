if(${INSTALL_PY} MATCHES "ON")
  install(
    FILES
    __init__.py
    DESTINATION ${CMAKE_INSTALL_PREFIX}/krender
    PERMISSIONS
    OWNER_READ OWNER_WRITE
    GROUP_READ
    WORLD_READ)
endif()

add_subdirectory(core)
add_subdirectory(shader)
