
// MyASTConsumer.cpp source file

#include "clang/AST/RecursiveASTVisitor.h"

#include "MyASTConsumer.h"

#include <iostream>

static bool isFirstLetterUpperCase(const std::string &str) {
    return str.size() != 0 && std::isupper(str[0]);
}

class MyASTVisitor : public clang::RecursiveASTVisitor<MyASTVisitor> {
    public:
    bool VisitCXXRecordDecl(const clang::RecordDecl *record) {
        std::string name = record->getNameAsString();

        if (!isFirstLetterUpperCase(name)) {
            std::cout << "Record Decl : " << name
                      <<" doesn't start with uppercase! \n";
        }

        return true;
    }
    bool TraverseDecl(clang::Decl *decl)  {
        return
           clang::RecursiveASTVisitor<MyASTVisitor>::TraverseDecl(decl);
    }
};

void MyASTConsumer::HandleTranslationUnit(clang::ASTContext &ctx) {
    clang::TranslationUnitDecl *tuDecl = ctx.getTranslationUnitDecl();
    MyASTVisitor visitor;
    visitor.TraverseDecl(tuDecl);
}