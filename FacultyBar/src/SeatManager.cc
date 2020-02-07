
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initialize()
{

}

SeatManager::SeatManager(){
    checkParameterValidity();
    numberOfOccupiedSeats=0;
}

void SeatManager::checkParameterValidity(){

    if((bool)par("constantEatingDistribution")==(bool) par("exponentialEatingDistribution"))
        throw cRuntimeError("Invalid parameters");
    if((int)par("constantInfLimit")<0 || (int)par("constantSupLimit")<0 ||
       (int)par("exponentialEatingMean")<0 ||(int)par("totalTableNumber")<0
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
            if((bool)par("exponentialEatingDistribution"))
                t= exponential((double)par("exponentialEatingMean"));
            else
                t=(double)par("constantEatingMean");
           numberOfOccupiedSeats++;
           scheduleAt(SimTime()+t, odm);
        }
    }else{ // Outer Message
        if(tablesAreFull()){
            customerQueue.push(odm);
        }else{
            double t;
            if((bool)par("exponentialEatingDistribution"))
                t= exponential((double)par("exponentialEatingMean"));
            else
                t=(double)par("constantEatingMean");
            numberOfOccupiedSeats++;
            scheduleAt(SimTime()+t, odm);

        }


    }
}
