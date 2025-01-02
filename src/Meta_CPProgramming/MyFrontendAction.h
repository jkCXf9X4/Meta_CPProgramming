// MyFrontendAction.h header file
#pragma once

#include "clang/Frontend/FrontendAction.h"

class MyFrontendAction : public clang::ASTFrontendAction {
    protected:
        std::unique_ptr<clang::ASTConsumer> CreateASTConsumer(clang::CompilerInstance &ci, llvm::StringRef file) override;
};    
