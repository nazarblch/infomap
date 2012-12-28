project(infomap)

add_executable(infomap FuzGreedy.cpp infomap.cc GreedyBase.cc Greedy.cc Node.cc GraphLoader.cpp)

install(TARGETS infomap RUNTIME DESTINATION bin)
