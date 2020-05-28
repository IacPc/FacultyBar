
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
    simtime_t lastDepartureTime;
    bool busy;

    // Signals
    simsignal_t waitingTimeNormalCustomerCashierQueueSignal;
    simsignal_t waitingTimeVipCustomerCashierQueueSignal;
    simsignal_t responseTimeNormalCustomerCashierNodeSignal;
    simsignal_t responseTimeVipCustomerCashierNodeSignal;
    simsignal_t numberOfNormalCustomersCashierQueueSignal;
    simsignal_t numberOfVipCustomersCashierQueueSignal;
    simsignal_t normalCustomerDropRateCashierSignal;
    simsignal_t vipCustomerDropRateCashierSignal;
    simsignal_t interDepartureTimeCashierSignal;

    void checkParametersValidity();
    void initializeStatisticSignals();
    void emitWaitingTime(OrderMessage* customerOrder);
    void emitResponseTime(OrderMessage* customerOrder);
    void emitCustomerQueueSize(int numberOfCustomers, bool vipQueue);
    void emitDropRate(int numberOfLostCustomers, bool vipCustomer);
    bool customerQueueIsFull(OrderMessage* newOrder);
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
