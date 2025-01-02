                                                     

// Source file MyFrontendActionFactory.cpp

#include "MyFrontendActionFactory.h"
#include "MyFrontendAction.h"

MyFrontendActionFactory::MyFrontendActionFactory() {

}

std::unique_ptr<clang::FrontendAction> MyFrontendActionFactory::create() {
    return std::make_unique<MyFrontendAction>();
}