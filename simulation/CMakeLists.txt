build_exec(
  EXECNAME deadline-routing
  SOURCE_FILES main.cc packet-header.cc routing.cc
  LIBRARIES_TO_LINK ${libcore} ${libnetwork} ${libinternet} ${libwifi} ${libmobility}
  EXECUTABLE_DIRECTORY_PATH ${CMAKE_OUTPUT_DIRECTORY}/scratch/deadline-routing
)
