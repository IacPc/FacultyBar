
#ifndef __FACULTYBAR_SEATMANAGER_H_
#define __FACULTYBAR_SEATMANAGER_H_

#include <omnetpp.h>
#include "OrderMessage_m.h"
#include <queue>
using namespace omnetpp;


class SeatManager : public cSimpleModule
{
    std::queue<OrderMessage*> customerQueue;
    unsigned int numberOfOccupiedSeats;
    simsignal_t waitingTimeNormalCustomerTableQueueSignal;
    simsignal_t waitingTimeVipCustomerTableQueueSignal;
    simsignal_t responseTimeNormalCustomerTableNodeSignal;
    simsignal_t responseTimeVipCustomerTableNodeSignal;
    simsignal_t numberOfCustomersTableQueueSignal;

    void checkParameterValidity();
    bool tablesAreFull();
    double assignEatingTime();
    OrderMessage* removeCustomerFromQueue();
    void handleSelfMessage(OrderMessage*);
    void handleOuterMessage(OrderMessage*);
    void emitWaitingTimeSignal(OrderMessage*);
    void emitResponseTimeSignal(OrderMessage*);
  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);

  public:
    SeatManager();
    ~SeatManager();
};

#endif
