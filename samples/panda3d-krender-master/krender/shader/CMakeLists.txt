set(SHADERS
  ${CMAKE_CURRENT_SOURCE_DIR}/base.inc.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/blur.inc.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/defines.inc.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/shading.inc.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/bloom.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/bloom.vert.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/default.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/default.vert.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/dof.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/dof.vert.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/shadow.frag.glsl
  ${CMAKE_CURRENT_SOURCE_DIR}/shadow.vert.glsl
)

install(
  FILES
  ${SHADERS}
  DESTINATION ${CMAKE_INSTALL_PREFIX}/krender/shader
  PERMISSIONS
  OWNER_READ OWNER_WRITE
  GROUP_READ
  WORLD_READ)
