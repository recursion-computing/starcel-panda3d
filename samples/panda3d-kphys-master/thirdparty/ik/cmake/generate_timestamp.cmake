string (TIMESTAMP IK_BUILD_TIME UTC)

# Update build number
file (STRINGS "${IK_SOURCE_DIR}/cmake/build_number.txt" IK_BUILD_NUMBER)
math (EXPR IK_BUILD_NUMBER "${IK_BUILD_NUMBER}+1")
file (WRITE "${IK_SOURCE_DIR}/cmake/build_number.txt" "# If you ever get merge conflicts with this file, figure out how many times you've built the file since the last successful pull and add that to the conflicting branch.\n")
file (APPEND "${IK_SOURCE_DIR}/cmake/build_number.txt" ${IK_BUILD_NUMBER})

file(WRITE ${OUTPUT_FILE}
    "/* build_info_dynamic.h generated by CMake. Changes will be lost! */\n"
    "#define IK_BUILD_TIME \"${IK_BUILD_TIME}\"\n"
    "#define IK_BUILD_NUMBER ${IK_BUILD_NUMBER}\n")