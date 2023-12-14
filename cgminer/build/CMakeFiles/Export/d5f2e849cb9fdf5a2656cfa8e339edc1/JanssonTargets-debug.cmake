#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "jansson" for configuration "Debug"
set_property(TARGET jansson APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(jansson PROPERTIES
  IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "C"
  IMPORTED_LOCATION_DEBUG "/usr/local/lib/libjansson.a"
  )

list(APPEND _cmake_import_check_targets jansson )
list(APPEND _cmake_import_check_files_for_jansson "/usr/local/lib/libjansson.a" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
