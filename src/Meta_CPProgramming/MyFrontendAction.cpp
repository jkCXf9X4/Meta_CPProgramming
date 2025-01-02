

// MyFrontendAction.cpp source file
#include "MyFrontendAction.h"
#include "MyASTConsumer.h"

std::unique_ptr<clang::ASTConsumer> MyFrontendAction::CreateASTConsumer(clang::CompilerInstance &ci, llvm::StringRef file) {
    return std::make_unique<MyASTConsumer>(ci, file);
}