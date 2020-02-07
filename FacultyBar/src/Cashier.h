
#ifndef __FACULTYBAR_CASHIER_H_
#define __FACULTYBAR_CASHIER_H_

#include <omnetpp.h>

using namespace omnetpp;


class Cashier : public cSimpleModule
{
  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);
};

#endif
