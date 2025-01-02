#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"

#include "MyFrontendActionFactory.h"

#include <memory>

using namespace clang::tooling;
using namespace llvm;

static llvm::cl::OptionCategory toolCategory("class-analyzer <options>");

int main(int argc, const char** argv)
{
    // Use clang's argument parser infrastructure
    // This is used for giving clang tooling the path
    // to the source files passed in to the tool.
    // It also gets the compilation database - a collection
    // of the compiler options used in the invocation of the tool
    auto argsParser = CommonOptionsParser::create(
        argc, argv, toolCategory);
    if (!expectedArgsParser) {
        llvm::errs() << argsParser.takeError();
        return -1;
    }
    CommonOptionsParser& optionsParser
        = argsParser.get();
    ClangTool tool(optionsParser.getCompilations(),
                   optionsParser.getSourcePathList());
    auto myActionFactory
        = std::make_unique<MyFrontendActionFactory>();

    return tool.run(myActionFactory.get());
}