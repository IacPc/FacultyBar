
#ifndef __FACULTYBAR_ORDERPRODUCER_H_
#define __FACULTYBAR_ORDERPRODUCER_H_

#include <omnetpp.h>

using namespace omnetpp;


class OrderProducer : public cSimpleModule
{
  private:
    cMessage* timerMessage;

    void checkParametersValidity();
    double generateProductionTime();
    void sendNewOrder();

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage* msg);

  public:
    OrderProducer();
    virtual ~OrderProducer();
};

#endif
