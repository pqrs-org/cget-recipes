cmake_minimum_required (VERSION 3.9)

file(GLOB RECIPES RELATIVE ${CMAKE_CURRENT_SOURCE_DIR} recipes/*)

macro(get_directory_base OUTPUT_VAR DIR)
  get_filename_component(${OUTPUT_VAR} ${DIR} DIRECTORY ${ARGN})
endmacro()

foreach(RECIPE ${RECIPES})
  get_directory_base(RECIPE_DIR ${RECIPE})
  install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/${RECIPE} DESTINATION etc/cget/recipes/)
endforeach()
