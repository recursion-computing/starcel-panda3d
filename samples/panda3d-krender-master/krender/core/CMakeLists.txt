set(CORE_SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/config.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/helpers.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/lighting_pipeline.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/post_pass.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/progress_bar.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/render_pass.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/render_pipeline.cxx
  ${CMAKE_CURRENT_SOURCE_DIR}/scene_pass.cxx
)

set(CORE_HEADERS
  ${CMAKE_CURRENT_SOURCE_DIR}/config.h
  ${CMAKE_CURRENT_SOURCE_DIR}/helpers.h
  ${CMAKE_CURRENT_SOURCE_DIR}/light.h
  ${CMAKE_CURRENT_SOURCE_DIR}/light_data.h
  ${CMAKE_CURRENT_SOURCE_DIR}/lighting_pipeline.h
  ${CMAKE_CURRENT_SOURCE_DIR}/post_pass.h
  ${CMAKE_CURRENT_SOURCE_DIR}/progress_bar.h
  ${CMAKE_CURRENT_SOURCE_DIR}/render_pass.h
  ${CMAKE_CURRENT_SOURCE_DIR}/render_pipeline.h
  ${CMAKE_CURRENT_SOURCE_DIR}/scene_pass.h
  ${CMAKE_CURRENT_SOURCE_DIR}/shadow_source.h
  ${CMAKE_SOURCE_DIR}/krender/defines.h
)

add_custom_command(
  OUTPUT core.in core_igate.cpp
  COMMAND ${INTERROGATE} -DCPPPARSER -D__STDC__=1 -D__cplusplus=201103L
  -I${CMAKE_SOURCE_DIR}
  -I${PANDA_INCLUDE_DIR}/panda3d
  -S${CMAKE_SOURCE_DIR}
  -S${PANDA_INCLUDE_DIR}/panda3d/parser-inc
  -oc core_igate.cpp
  -od core.in
  -fnames -string -refcount -assert -python-native -nomangle
  -module core -library core
  ${CORE_HEADERS}
  DEPENDS ${CORE_SOURCES} ${CORE_HEADERS})

add_custom_command(
  OUTPUT core_module.cpp
  COMMAND ${INTERROGATE_MODULE}
  -oc core_module.cpp
  -module core -library core
  -python-native
  -import panda3d.core
  -import panda3d._rplight
  core.in
  DEPENDS core.in core_igate.cpp)

add_library(core SHARED
  ${CORE_SOURCES}
  core_igate.cpp
  core_module.cpp)

set_target_properties(core PROPERTIES PREFIX "")
if(WIN32)
  set_target_properties(core PROPERTIES SUFFIX ".pyd")
endif()

target_link_libraries(core
  # PANDA3D
  ${PANDA_LIBS}
  # PYTHON
  ${PYTHON_LIBRARY}
)

install(TARGETS core DESTINATION ${CMAKE_INSTALL_PREFIX}/krender)
