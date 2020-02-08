
#ifndef __FACULTYBAR_SEATMANAGER_H_
#define __FACULTYBAR_SEATMANAGER_H_

#include <omnetpp.h>
#include "OrderMessage_m.h"
#include <queue>
using namespace omnetpp;
using namespace std;


class SeatManager : public cSimpleModule
{
    std::queue<OrderMessage*> customerQueue;
    unsigned int numberOfOccupiedSeats;
    void checkParameterValidity();
  protected:
    virtual void initialize();
    virtual void handleMessage(cMessage *msg);
    bool tablesAreFull(){ return (numberOfOccupiedSeats==par("totalTableNumber").intValue());}
    double assignEatingTime();
    OrderMessage* removeCustomerFromQueue();
  public:
    SeatManager();
};

#endif
