// Header file MyFrontendActionFactory.h
#pragma once

#include "clang/Tooling/Tooling.h"


class MyFrontendActionFactory : public clang::tooling::FrontendActionFactory{
    public:
    MyFrontendActionFactory();
    std::unique_ptr<clang::FrontendAction> create() override;
};                                                         
