
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initialize()
{
    checkParameterValidity();

}

SeatManager::SeatManager(){
    numberOfOccupiedSeats=0;
}


double SeatManager::assignEatingTime(){
    double t;
    if(par("exponentialEatingDistribution").boolValue())
        t= exponential(par("exponentialEatingMean").doubleValue()); //Exponential Eating time
    else
        t= par("constantEatingMean").doubleValue();
    return t;

}
OrderMessage* SeatManager::removeCustomerFromQueue(){

    OrderMessage* o= customerQueue.front();
    customerQueue.pop();
    /*
     EMIT STATISTICS HERE
     */
    return o;
}


void SeatManager::checkParameterValidity(){

    if(par("constantEatingDistribution").boolValue()==par("exponentialEatingDistribution").boolValue())
        throw cRuntimeError("Invalid parameters");
    if(par("constantEatingMean").intValue()<0 || par("exponentialEatingMean").intValue()<0 ||
       par("totalTableNumber").intValue()<0
       )
        throw cRuntimeError("Invalid parameters");

}

void SeatManager::handleMessage(cMessage *msg)
{
    OrderMessage* odm= static_cast<OrderMessage*>(msg);
    if(odm->isSelfMessage()){ // A customer finish and leaves his spot
        numberOfOccupiedSeats--;
        if(!customerQueue.empty()){
           odm =removeCustomerFromQueue();
           numberOfOccupiedSeats++;
           scheduleAt(SimTime()+assignEatingTime(), odm);
        }
    }else{ // A customer requests a spot
        if(tablesAreFull()){    //All servers busy and The customer goes in queue
            customerQueue.push(odm);
        }else{                  //the customer eats
            numberOfOccupiedSeats++;
            scheduleAt(SimTime()+assignEatingTime(), odm);
        }

    }
}
