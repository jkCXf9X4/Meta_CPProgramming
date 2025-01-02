set(LLVM_LINK_COMPONENTS support)
set(CMAKE_CXX_COMPILER /usr/bin/clang++)  

project(class-analyzer)

cmake_minimum_required(VERSION 3.25)

#add_subdirectory(src/Meta_CPProgramming)
#add_executable(src/Meta_CPProgramming/ClassAnalyzer.cpp)
add_executable(ClassAnalyzer.cpp)

add_clang_executable(class-analyzer
  ClassAnalzyer.cpp
  MyFrontendActionFactory.cpp
  MyFrontendAction.cpp
  MyASTConsumer.cpp
  )
target_link_libraries(class-analyzer
  PRIVATE
  clangAST
  clangFrontend
  clangTooling
  )