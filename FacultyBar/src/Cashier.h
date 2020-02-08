
#ifndef __FACULTYBAR_CASHIER_H_
#define __FACULTYBAR_CASHIER_H_

#include <omnetpp.h>
#include "OrderMessage_m.h"
#include <queue>

using namespace omnetpp;


class Cashier : public cSimpleModule
{
  private:
    cMessage* timerMessage;
    OrderMessage* orderUnderService;
    std::queue<OrderMessage*> vipCustomerQueue;
    std::queue<OrderMessage*> normalCustomerQueue;
    bool busy;

    void checkParametersValidity();
    double generateServiceTime();
    void handleOrderArrival(cMessage* msg);
    void completeOrder();

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage* msg);

  public:
    Cashier();
    virtual ~Cashier();
};

#endif
