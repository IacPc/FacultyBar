
#include "SeatManager.h"

Define_Module(SeatManager);

void SeatManager::initializeStatisticSignals()
{
    waitingTimeNormalCustomerTableQueueSignal = registerSignal("waitingTimeNormalCustomerTableQueue");
    waitingTimeVipCustomerTableQueueSignal = registerSignal("waitingTimeVipCustomerTableQueue");
    responseTimeNormalCustomerTableNodeSignal = registerSignal("responseTimeNormalCustomerTableNode");
    responseTimeVipCustomerTableNodeSignal = registerSignal("responseTimeVipCustomerTableNode");
    numberOfCustomersTableQueueSignal = registerSignal("numberOfCustomersTableQueue");
}

void SeatManager::initialize()
{
    checkParametersValidity();
    initializeStatisticSignals();

    // Reserve space for unordered_set to avoid rehashing when the actual size grows.
    int numberOfSeats = par("numberOfTables").intValue()*par("numberOfSeatsPerTable").intValue();
    customerSeated.reserve(numberOfSeats);

    // At the beginning, the queue is empty
    emit(numberOfCustomersTableQueueSignal, customerQueue.size());
}

SeatManager::~SeatManager()
{
    OrderMessage* customerMessage = NULL;

    while (!customerSeated.empty()) {
        customerMessage = *(customerSeated.begin());
        customerSeated.erase(customerSeated.begin());
        cancelAndDelete(customerMessage);
    }

    while (!customerQueue.empty()) {
        customerMessage = customerQueue.front();
        customerQueue.pop();
        delete customerMessage;
   }
}

bool SeatManager::tablesAreFull()
{
    return (customerSeated.size() == (unsigned long)(par("numberOfTables").intValue()*par("numberOfSeatsPerTable").intValue()));
}

double SeatManager::assignEatingTime()
{
    double eatingTime;

    if (par("exponentialEatingDistribution").boolValue())
        eatingTime = exponential(par("exponentialEatingMean").doubleValue(), 3);
    else if (par("constantEatingDistribution").boolValue())
        eatingTime = par("constantEatingMean").doubleValue();

    EV << "A new customer took a seat. Eating time: " << eatingTime << endl;
    return eatingTime;
}

OrderMessage* SeatManager::removeCustomerFromQueue()
{
    OrderMessage* nextCustomer = customerQueue.front();
    customerQueue.pop();
    emit(numberOfCustomersTableQueueSignal, customerQueue.size());

    nextCustomer->setSeatManagerQueueExitTime(simTime());
    emitWaitingTimeSignal(nextCustomer);

    return nextCustomer;
}

void SeatManager::checkParametersValidity()
{
    if (par("constantEatingDistribution").boolValue() == par("exponentialEatingDistribution").boolValue()) {
        EV_ERROR << "No distribution or multiple ones selected for the eating time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (par("constantEatingDistribution").boolValue() && par("constantEatingMean").doubleValue() < 0) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (par("exponentialEatingDistribution").boolValue() && par("exponentialEatingMean").doubleValue() < 0) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (par("numberOfTables").intValue() < 0 || par("numberOfSeatsPerTable").intValue() < 0) {
        EV_ERROR << "A negative number of tables/seats per table is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
}

void SeatManager::emitWaitingTimeSignal(OrderMessage* msg)
{
    simtime_t exitTime = msg->getSeatManagerQueueExitTime();
    simtime_t arrivalTime = msg->getSeatManagerQueueArrivalTime();

    if (msg->getVipPriority())
        emit(waitingTimeVipCustomerTableQueueSignal, exitTime - arrivalTime);
    else
        emit(waitingTimeNormalCustomerTableQueueSignal, exitTime - arrivalTime);
}

void SeatManager::emitResponseTimeSignal(OrderMessage* msg)
{
    simtime_t departureTime = msg->getSeatManagerNodeDepartureTime();
    simtime_t arrivalTime = msg->getSeatManagerQueueArrivalTime();

    if (msg->getVipPriority())
        emit(responseTimeVipCustomerTableNodeSignal, departureTime - arrivalTime);
    else
        emit(responseTimeNormalCustomerTableNodeSignal, departureTime - arrivalTime);
}

void SeatManager::handleLeavingCustomer(cMessage* msg)
{
    OrderMessage* leavingCustomer = check_and_cast<OrderMessage*>(msg);

    leavingCustomer->setSeatManagerNodeDepartureTime(simTime());
    emitResponseTimeSignal(leavingCustomer);

    customerSeated.erase(leavingCustomer);
    delete leavingCustomer;
    EV << "A customer left the bar." << endl;

    if (!customerQueue.empty()) {
        OrderMessage* nextCustomer = removeCustomerFromQueue();
        customerSeated.insert(nextCustomer);
        scheduleAt(simTime() + assignEatingTime(), nextCustomer);
    }
}

void SeatManager::handleArrivingCustomer(cMessage* msg)
{
    OrderMessage* arrivingCustomer = check_and_cast<OrderMessage*>(msg);
    arrivingCustomer->setSeatManagerQueueArrivalTime(simTime());

    if (tablesAreFull()) {    // All servers are busy and the customer goes in queue
        customerQueue.push(arrivingCustomer);
        emit(numberOfCustomersTableQueueSignal, customerQueue.size());
        EV << "A new customer joined the queue." << endl;

    } else {  // The customer eats
        customerSeated.insert(arrivingCustomer);
        arrivingCustomer->setSeatManagerQueueExitTime(simTime());
        emitWaitingTimeSignal(arrivingCustomer);

        scheduleAt(simTime() + assignEatingTime(), arrivingCustomer);
    }
}

void SeatManager::handleMessage(cMessage* msg)
{
    if(msg->isSelfMessage()) // A customer finishes and leaves his spot
        handleLeavingCustomer(msg);
    else // A customer requests a spot
        handleArrivingCustomer(msg);
}
