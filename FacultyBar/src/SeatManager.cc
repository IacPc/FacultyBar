
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initialize()
{
    checkParameterValidity();

}

SeatManager::SeatManager(){
    numberOfOccupiedSeats=0;
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
    if(odm->isSelfMessage()){
        cancelAndDelete(odm);
        numberOfOccupiedSeats--;

        if(customerQueue.size()>0){
            odm = customerQueue.front();
            double t;

            customerQueue.pop();
            if(par("exponentialEatingDistribution").boolValue())
                t= exponential(par("exponentialEatingMean").doubleValue());
            else
                t= par("constantEatingMean").doubleValue();
           numberOfOccupiedSeats++;
           scheduleAt(SimTime()+t, odm);
        }
    }else{ // Outer Message
        if(tablesAreFull()){
            customerQueue.push(odm);
        }else{
            double t;
            if((bool)par("exponentialEatingDistribution"))
                t= exponential(par("exponentialEatingMean").doubleValue());
            else
                t=par("constantEatingMean").doubleValue();
            numberOfOccupiedSeats++;
            scheduleAt(SimTime()+t, odm);

        }


    }
}
