
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initialize()
{
    // TODO - Generated method body
}

SeatManager::SeatManager(){
    //checkParameterValidity();
    //numberOfOccupiedSeats=0;
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
   // if(){}
}
