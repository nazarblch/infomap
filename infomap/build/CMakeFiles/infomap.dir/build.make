# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 2.8

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canoncical targets will work.
.SUFFIXES:

# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list

# Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# The program to use to edit the cache.
CMAKE_EDIT_COMMAND = /usr/bin/ccmake

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/nazar/projects/infomap

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/nazar/projects/infomap/build

# Include any dependencies generated for this target.
include CMakeFiles/infomap.dir/depend.make

# Include the progress variables for this target.
include CMakeFiles/infomap.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/infomap.dir/flags.make

CMakeFiles/infomap.dir/FuzGreedy.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/FuzGreedy.o: ../FuzGreedy.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_1)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/FuzGreedy.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/FuzGreedy.o -c /home/nazar/projects/infomap/FuzGreedy.cpp

CMakeFiles/infomap.dir/FuzGreedy.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/FuzGreedy.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/FuzGreedy.cpp > CMakeFiles/infomap.dir/FuzGreedy.i

CMakeFiles/infomap.dir/FuzGreedy.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/FuzGreedy.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/FuzGreedy.cpp -o CMakeFiles/infomap.dir/FuzGreedy.s

CMakeFiles/infomap.dir/FuzGreedy.o.requires:
.PHONY : CMakeFiles/infomap.dir/FuzGreedy.o.requires

CMakeFiles/infomap.dir/FuzGreedy.o.provides: CMakeFiles/infomap.dir/FuzGreedy.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/FuzGreedy.o.provides.build
.PHONY : CMakeFiles/infomap.dir/FuzGreedy.o.provides

CMakeFiles/infomap.dir/FuzGreedy.o.provides.build: CMakeFiles/infomap.dir/FuzGreedy.o

CMakeFiles/infomap.dir/infomap.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/infomap.o: ../infomap.cc
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_2)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/infomap.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/infomap.o -c /home/nazar/projects/infomap/infomap.cc

CMakeFiles/infomap.dir/infomap.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/infomap.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/infomap.cc > CMakeFiles/infomap.dir/infomap.i

CMakeFiles/infomap.dir/infomap.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/infomap.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/infomap.cc -o CMakeFiles/infomap.dir/infomap.s

CMakeFiles/infomap.dir/infomap.o.requires:
.PHONY : CMakeFiles/infomap.dir/infomap.o.requires

CMakeFiles/infomap.dir/infomap.o.provides: CMakeFiles/infomap.dir/infomap.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/infomap.o.provides.build
.PHONY : CMakeFiles/infomap.dir/infomap.o.provides

CMakeFiles/infomap.dir/infomap.o.provides.build: CMakeFiles/infomap.dir/infomap.o

CMakeFiles/infomap.dir/GreedyBase.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/GreedyBase.o: ../GreedyBase.cc
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_3)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/GreedyBase.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/GreedyBase.o -c /home/nazar/projects/infomap/GreedyBase.cc

CMakeFiles/infomap.dir/GreedyBase.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/GreedyBase.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/GreedyBase.cc > CMakeFiles/infomap.dir/GreedyBase.i

CMakeFiles/infomap.dir/GreedyBase.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/GreedyBase.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/GreedyBase.cc -o CMakeFiles/infomap.dir/GreedyBase.s

CMakeFiles/infomap.dir/GreedyBase.o.requires:
.PHONY : CMakeFiles/infomap.dir/GreedyBase.o.requires

CMakeFiles/infomap.dir/GreedyBase.o.provides: CMakeFiles/infomap.dir/GreedyBase.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/GreedyBase.o.provides.build
.PHONY : CMakeFiles/infomap.dir/GreedyBase.o.provides

CMakeFiles/infomap.dir/GreedyBase.o.provides.build: CMakeFiles/infomap.dir/GreedyBase.o

CMakeFiles/infomap.dir/Greedy.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/Greedy.o: ../Greedy.cc
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_4)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/Greedy.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/Greedy.o -c /home/nazar/projects/infomap/Greedy.cc

CMakeFiles/infomap.dir/Greedy.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/Greedy.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/Greedy.cc > CMakeFiles/infomap.dir/Greedy.i

CMakeFiles/infomap.dir/Greedy.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/Greedy.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/Greedy.cc -o CMakeFiles/infomap.dir/Greedy.s

CMakeFiles/infomap.dir/Greedy.o.requires:
.PHONY : CMakeFiles/infomap.dir/Greedy.o.requires

CMakeFiles/infomap.dir/Greedy.o.provides: CMakeFiles/infomap.dir/Greedy.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/Greedy.o.provides.build
.PHONY : CMakeFiles/infomap.dir/Greedy.o.provides

CMakeFiles/infomap.dir/Greedy.o.provides.build: CMakeFiles/infomap.dir/Greedy.o

CMakeFiles/infomap.dir/Node.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/Node.o: ../Node.cc
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_5)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/Node.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/Node.o -c /home/nazar/projects/infomap/Node.cc

CMakeFiles/infomap.dir/Node.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/Node.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/Node.cc > CMakeFiles/infomap.dir/Node.i

CMakeFiles/infomap.dir/Node.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/Node.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/Node.cc -o CMakeFiles/infomap.dir/Node.s

CMakeFiles/infomap.dir/Node.o.requires:
.PHONY : CMakeFiles/infomap.dir/Node.o.requires

CMakeFiles/infomap.dir/Node.o.provides: CMakeFiles/infomap.dir/Node.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/Node.o.provides.build
.PHONY : CMakeFiles/infomap.dir/Node.o.provides

CMakeFiles/infomap.dir/Node.o.provides.build: CMakeFiles/infomap.dir/Node.o

CMakeFiles/infomap.dir/GraphLoader.o: CMakeFiles/infomap.dir/flags.make
CMakeFiles/infomap.dir/GraphLoader.o: ../GraphLoader.cpp
	$(CMAKE_COMMAND) -E cmake_progress_report /home/nazar/projects/infomap/build/CMakeFiles $(CMAKE_PROGRESS_6)
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Building CXX object CMakeFiles/infomap.dir/GraphLoader.o"
	/usr/bin/c++   $(CXX_DEFINES) $(CXX_FLAGS) -o CMakeFiles/infomap.dir/GraphLoader.o -c /home/nazar/projects/infomap/GraphLoader.cpp

CMakeFiles/infomap.dir/GraphLoader.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/infomap.dir/GraphLoader.i"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -E /home/nazar/projects/infomap/GraphLoader.cpp > CMakeFiles/infomap.dir/GraphLoader.i

CMakeFiles/infomap.dir/GraphLoader.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/infomap.dir/GraphLoader.s"
	/usr/bin/c++  $(CXX_DEFINES) $(CXX_FLAGS) -S /home/nazar/projects/infomap/GraphLoader.cpp -o CMakeFiles/infomap.dir/GraphLoader.s

CMakeFiles/infomap.dir/GraphLoader.o.requires:
.PHONY : CMakeFiles/infomap.dir/GraphLoader.o.requires

CMakeFiles/infomap.dir/GraphLoader.o.provides: CMakeFiles/infomap.dir/GraphLoader.o.requires
	$(MAKE) -f CMakeFiles/infomap.dir/build.make CMakeFiles/infomap.dir/GraphLoader.o.provides.build
.PHONY : CMakeFiles/infomap.dir/GraphLoader.o.provides

CMakeFiles/infomap.dir/GraphLoader.o.provides.build: CMakeFiles/infomap.dir/GraphLoader.o

# Object files for target infomap
infomap_OBJECTS = \
"CMakeFiles/infomap.dir/FuzGreedy.o" \
"CMakeFiles/infomap.dir/infomap.o" \
"CMakeFiles/infomap.dir/GreedyBase.o" \
"CMakeFiles/infomap.dir/Greedy.o" \
"CMakeFiles/infomap.dir/Node.o" \
"CMakeFiles/infomap.dir/GraphLoader.o"

# External object files for target infomap
infomap_EXTERNAL_OBJECTS =

infomap: CMakeFiles/infomap.dir/FuzGreedy.o
infomap: CMakeFiles/infomap.dir/infomap.o
infomap: CMakeFiles/infomap.dir/GreedyBase.o
infomap: CMakeFiles/infomap.dir/Greedy.o
infomap: CMakeFiles/infomap.dir/Node.o
infomap: CMakeFiles/infomap.dir/GraphLoader.o
infomap: CMakeFiles/infomap.dir/build.make
infomap: CMakeFiles/infomap.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --red --bold "Linking CXX executable infomap"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/infomap.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/infomap.dir/build: infomap
.PHONY : CMakeFiles/infomap.dir/build

CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/FuzGreedy.o.requires
CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/infomap.o.requires
CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/GreedyBase.o.requires
CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/Greedy.o.requires
CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/Node.o.requires
CMakeFiles/infomap.dir/requires: CMakeFiles/infomap.dir/GraphLoader.o.requires
.PHONY : CMakeFiles/infomap.dir/requires

CMakeFiles/infomap.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/infomap.dir/cmake_clean.cmake
.PHONY : CMakeFiles/infomap.dir/clean

CMakeFiles/infomap.dir/depend:
	cd /home/nazar/projects/infomap/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/nazar/projects/infomap /home/nazar/projects/infomap /home/nazar/projects/infomap/build /home/nazar/projects/infomap/build /home/nazar/projects/infomap/build/CMakeFiles/infomap.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/infomap.dir/depend

