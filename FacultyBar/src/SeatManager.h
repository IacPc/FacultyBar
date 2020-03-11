
#ifndef __FACULTYBAR_SEATMANAGER_H_
#define __FACULTYBAR_SEATMANAGER_H_

#include <omnetpp.h>
#include "OrderMessage_m.h"
#include <queue>
#include <unordered_set>

using namespace omnetpp;


class SeatManager : public cSimpleModule
{
    std::queue<OrderMessage*> customerQueue;
    std::unordered_set<OrderMessage*> customerSeated;
    int numberOfServedCustomers;

    // Signals
    simsignal_t waitingTimeNormalCustomerTableQueueSignal;
    simsignal_t waitingTimeVipCustomerTableQueueSignal;
    simsignal_t responseTimeNormalCustomerTableNodeSignal;
    simsignal_t responseTimeVipCustomerTableNodeSignal;
    simsignal_t numberOfCustomersTableQueueSignal;
    simsignal_t customerDropRateTableSignal;
    simsignal_t throughputSignal;

    void checkParametersValidity();
    void initializeStatisticSignals();
    void emitWaitingTimeSignal(OrderMessage*);
    void emitResponseTimeSignal(OrderMessage*);
    bool tablesAreFull();
    bool customerQueueIsFull();
    double assignEatingTime();
    OrderMessage* removeCustomerFromQueue();
    void handleLeavingCustomer(cMessage*);
    void handleArrivingCustomer(cMessage*);

  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);

  public:
    ~SeatManager();
};

#endif
