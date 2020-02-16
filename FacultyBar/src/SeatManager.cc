
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initialize()
{
    checkParameterValidity();

    // Reserve space for unordered_set to avoid rehashes when the actual size grows
    int numberOfSeats = par("numberOfTables").intValue()*par("numberOfSeatsPerTable").intValue();
    customerSeated.reserve(numberOfSeats);

    waitingTimeNormalCustomerTableQueueSignal=registerSignal("waitingTimeNormalCustomerTableQueue");
    waitingTimeVipCustomerTableQueueSignal=registerSignal("waitingTimeVipCustomerTableQueue");
    responseTimeNormalCustomerTableNodeSignal=registerSignal("responseTimeNormalCustomerTableNode");
    responseTimeVipCustomerTableNodeSignal=registerSignal("responseTimeVipCustomerTableNode");
    numberOfCustomersTableQueueSignal=registerSignal("numberOfCustomersTableQueue");

    // At the beginning, the queue is empty
    emit(numberOfCustomersTableQueueSignal,customerQueue.size());
}


SeatManager::~SeatManager(){

    OrderMessage* om = NULL;

    while (!customerSeated.empty()) {
        om = *(customerSeated.begin());
        customerSeated.erase(customerSeated.begin());
        cancelAndDelete(om);
    }

    while (!customerQueue.empty()) {
        om = customerQueue.front();
        customerQueue.pop();
        delete om;
   }

}

bool SeatManager::tablesAreFull(){
    return (customerSeated.size()==par("numberOfTables").intValue()*par("numberOfSeatsPerTable").intValue());
}

double SeatManager::assignEatingTime(){
    double t;
    if(par("exponentialEatingDistribution").boolValue())
        t= exponential(par("exponentialEatingMean").doubleValue(), 3); //Exponential Eating time
    else
        t= par("constantEatingMean").doubleValue();
    return t;
}

OrderMessage* SeatManager::removeCustomerFromQueue(){

    OrderMessage* o= customerQueue.front();
    customerQueue.pop();

    o->setSeatManagerQueueExitTime(simTime());
    emitWaitingTimeSignal(o);

    return o;
}


void SeatManager::checkParameterValidity(){

    if(par("constantEatingDistribution").boolValue()==par("exponentialEatingDistribution").boolValue()){
        EV_ERROR << "No distribution or multiple ones selected for the eating time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
    if(par("constantEatingMean").doubleValue()<0 && par("constantEatingDistribution").boolValue() ){
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
    if(par("exponentialEatingMean").doubleValue()<0 && par("exponentialEatingDistribution").boolValue()){
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
    if(par("numberOfTables").intValue()<0 || par("numberOfSeatsPerTable").intValue()<0){
        EV_ERROR << "A negative number of tables/seats per table is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

}

void SeatManager::emitWaitingTimeSignal(OrderMessage* msg){
    simtime_t exit =msg->getSeatManagerQueueExitTime();
    simtime_t arrival = msg->getSeatManagerQueueArrivalTime();
    if(msg->getVipPriority())
        emit(waitingTimeVipCustomerTableQueueSignal,exit-arrival);
    else
        emit(waitingTimeNormalCustomerTableQueueSignal,exit-arrival);

}

void SeatManager::emitResponseTimeSignal(OrderMessage* msg){
    simtime_t dep =msg->getSeatManagerNodeDepartureTime();
    simtime_t arrival = msg->getSeatManagerQueueArrivalTime();
    if(msg->getVipPriority())
        emit(responseTimeVipCustomerTableNodeSignal,dep-arrival);
    else
        emit(responseTimeNormalCustomerTableNodeSignal,dep-arrival);

}

void SeatManager::handleSelfMessage(OrderMessage* msg){

    customerSeated.erase(msg);

    msg->setSeatManagerNodeDepartureTime(simTime());
    emitResponseTimeSignal(msg);
    delete msg;

    if(!customerQueue.empty()){
        msg =removeCustomerFromQueue();
        customerSeated.insert(msg);

        scheduleAt(simTime()+assignEatingTime(), msg);
    }
}


void SeatManager::handleOuterMessage(OrderMessage* msg){

    msg->setSeatManagerQueueArrivalTime(simTime());

    if(tablesAreFull()){    //All servers busy and the customer goes in queue
        customerQueue.push(msg);
        emit(numberOfCustomersTableQueueSignal,customerQueue.size());

    }else{ //the customer eats
        customerSeated.insert(msg);

        msg->setSeatManagerQueueExitTime(simTime());
        emitWaitingTimeSignal(msg);
        scheduleAt(simTime()+assignEatingTime(), msg);
    }
}


void SeatManager::handleMessage(cMessage *msg)
{
    OrderMessage* odm= check_and_cast<OrderMessage*>(msg);

    if(odm->isSelfMessage()) // A customer finishes and leaves his spot
        handleSelfMessage(odm);
    else// A customer requests a spot
        handleOuterMessage(odm);

}
