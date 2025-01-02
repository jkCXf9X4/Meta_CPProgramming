
//MyASTConsumer.h header file

#pragma once

#include "clang/AST/ASTConsumer.h"
#include "clang/Frontend/CompilerInstance.h"

class MyASTConsumer : public clang::ASTConsumer {

public:
    MyASTConsumer(clang::CompilerInstance &ci, llvm::StringRef file) {}
    void HandleTranslationUnit(clang::ASTContext &context) override;
};
