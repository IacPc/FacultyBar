
#include "SeatManager.h"

Define_Module(SeatManager);

// Registers the statistic signals.
void SeatManager::initializeStatisticSignals()
{
    waitingTimeNormalCustomerTableQueueSignal = registerSignal("waitingTimeNormalCustomerTableQueue");
    waitingTimeVipCustomerTableQueueSignal = registerSignal("waitingTimeVipCustomerTableQueue");
    responseTimeNormalCustomerTableNodeSignal = registerSignal("responseTimeNormalCustomerTableNode");
    responseTimeVipCustomerTableNodeSignal = registerSignal("responseTimeVipCustomerTableNode");
    numberOfCustomersTableQueueSignal = registerSignal("numberOfCustomersTableQueue");
    customerDropRateTableSignal = registerSignal("customerDropRateTable");
    throughputSignal = registerSignal("throughput");
}

// Initialization method: if the simulation parameters are valid, it ensures that
// the statistic signals are correctly registered and initialized.
void SeatManager::initialize()
{
    checkParametersValidity();
    initializeStatisticSignals();

    // Reserve space for unordered_set to avoid rehashing when the actual size grows.
    customerSeated.reserve(par("numberOfSeats"));

    // At the beginning, the queue is empty.
    emit(numberOfCustomersTableQueueSignal, customerQueue.size());

    numberOfServedCustomers = 0;
}

// Destructor: it frees the allocated memory for
// the customers at the tables and the customers in queue.
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

// Checks if there are available seats in the table area.
bool SeatManager::tablesAreFull()
{
    return (customerSeated.size() == (unsigned long) par("numberOfSeats").intValue());
}

// Generates the eating time for the customer that goes under service, according to the configured distribution.
double SeatManager::assignEatingTime()
{
    double eatingTime;

    if (par("exponentialEatingDistribution").boolValue())
        eatingTime = exponential(par("exponentialEatingMean").doubleValue(), par("rngNumber").intValue());
    else if (par("constantEatingDistribution").boolValue())
        eatingTime = par("constantEatingMean").doubleValue();

    EV << "A new customer took a seat. Eating time: " << eatingTime << endl;
    return eatingTime;
}

// Removes and returns the first customer of the queue.
// Then, the method emits her waiting time and the new size of the queue.
OrderMessage* SeatManager::removeCustomerFromQueue()
{
    OrderMessage* nextCustomer = customerQueue.front();
    customerQueue.pop();
    emit(numberOfCustomersTableQueueSignal, customerQueue.size());

    nextCustomer->setSeatManagerQueueExitTime(simTime());
    emitWaitingTimeSignal(nextCustomer);

    return nextCustomer;
}

// Checks if the simulation parameters in the configuration file are valid, namely:
//  1) if a distribution for the eating time has been set uniquely;
//  2) if the mean value of the constant/exponential distribution is not negative;
//  3) if the number of seats is >= 0;
//  4) if the size of the queue, when finite, is >= 0.
// If the parameters are not valid, a runtime exception is thrown.
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

    if (par("numberOfSeats").intValue() < 0) {
        EV_ERROR << "A negative number of seats is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (par("infiniteCustomerQueue").boolValue() && (par("queueSize").intValue() < 0) ) {
        EV_ERROR << "A negative size of the customer queue is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
}

// Given a customer, the method computes her waiting time and emits it according to the associated priority.
void SeatManager::emitWaitingTimeSignal(OrderMessage* msg)
{
    simtime_t exitTime = msg->getSeatManagerQueueExitTime();
    simtime_t arrivalTime = msg->getSeatManagerQueueArrivalTime();

    if (msg->getVipPriority())
        emit(waitingTimeVipCustomerTableQueueSignal, exitTime - arrivalTime);
    else
        emit(waitingTimeNormalCustomerTableQueueSignal, exitTime - arrivalTime);
}

// Given a customer, the method computes her response time and emits it according to the associated priority.
void SeatManager::emitResponseTimeSignal(OrderMessage* msg)
{
    simtime_t departureTime = msg->getSeatManagerNodeDepartureTime();
    simtime_t arrivalTime = msg->getSeatManagerQueueArrivalTime();

    if (msg->getVipPriority())
        emit(responseTimeVipCustomerTableNodeSignal, departureTime - arrivalTime);
    else
        emit(responseTimeNormalCustomerTableNodeSignal, departureTime - arrivalTime);
}

// Checks if the priority queue related to the arriving customer is full or not.
bool SeatManager::customerQueueIsFull()
{
    bool infiniteCustomerQueueEnabled = par("infiniteCustomerQueue").boolValue();
    unsigned int maxQueueSize = (unsigned int) par("queueSize").intValue();

    // The size check is more complex to avoid the loss of a customer when the size of the queue is 0, but there are available seats.
    // A simple check like "if (!infiniteCustomerQueueEnabled && (maxQueueSize == customerQueue.size()) then Drop" is not sufficient.
    if (infiniteCustomerQueueEnabled || (maxQueueSize > 0 && (customerQueue.size() < maxQueueSize)) || (maxQueueSize == 0 && !tablesAreFull())) {
        emit(customerDropRateTableSignal, 0);
        return false;
    }

    emit(customerDropRateTableSignal, 1);
    EV << "An order has been dropped. The customer queue is full." << endl;
    return true;
}

// Handles the leaving of an customer, so that:
//  1) the first waiting customer occupies the seat;
//  2) the statistics are correctly recorded.
void SeatManager::handleLeavingCustomer(cMessage* msg)
{
    OrderMessage* leavingCustomer = check_and_cast<OrderMessage*>(msg);

    numberOfServedCustomers++;
    leavingCustomer->setSeatManagerNodeDepartureTime(simTime());
    emitResponseTimeSignal(leavingCustomer);
    emit(throughputSignal, numberOfServedCustomers/simTime());

    customerSeated.erase(leavingCustomer);
    delete leavingCustomer;
    EV << "A customer left the bar." << endl;

    if (!customerQueue.empty()) {
        OrderMessage* nextCustomer = removeCustomerFromQueue();
        customerSeated.insert(nextCustomer);
        scheduleAt(simTime() + assignEatingTime(), nextCustomer);
    }
}

// Handles an arriving customer, so that:
//  1) the customer is placed in the queue or dropped, if the queue is full;
//  2) the customer takes a seat, if possible;
//  3) the statistics are correctly recorded.
void SeatManager::handleArrivingCustomer(cMessage* msg)
{
    OrderMessage* arrivingCustomer = check_and_cast<OrderMessage*>(msg);

    if (customerQueueIsFull()) {
        delete arrivingCustomer;
        return;
    }

    arrivingCustomer->setSeatManagerQueueArrivalTime(simTime());

    if (tablesAreFull()) {
        customerQueue.push(arrivingCustomer);
        emit(numberOfCustomersTableQueueSignal, customerQueue.size());
        EV << "A new customer joined the queue." << endl;

    } else {
        customerSeated.insert(arrivingCustomer);
        arrivingCustomer->setSeatManagerQueueExitTime(simTime());
        emitWaitingTimeSignal(arrivingCustomer);

        scheduleAt(simTime() + assignEatingTime(), arrivingCustomer);
    }
}

// Main handler.
void SeatManager::handleMessage(cMessage* msg)
{
    if(msg->isSelfMessage()) {
        handleLeavingCustomer(msg);
    }
    else {
        handleArrivingCustomer(msg);
    }
}
