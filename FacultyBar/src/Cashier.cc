
#include "Cashier.h"

Define_Module(Cashier);

// Constructor.
Cashier::Cashier()
{
    timerMessage = NULL;
    orderUnderService = NULL;
}

// Destructor: it frees the allocated memory for
// the order under service and the orders in both queues.
Cashier::~Cashier()
{
    cancelAndDelete(timerMessage);

    if (orderUnderService != NULL)
        delete orderUnderService;

    OrderMessage* customerMessage = NULL;

    while (!vipCustomerQueue.empty()) {
        customerMessage = vipCustomerQueue.front();
        vipCustomerQueue.pop();
        delete customerMessage;
    }

    while (!normalCustomerQueue.empty()) {
        customerMessage = normalCustomerQueue.front();
        normalCustomerQueue.pop();
        delete customerMessage;
    }
}

// Checks if the simulation parameters in the configuration file are valid, namely:
//  1) if a distribution for the service time has been set uniquely;
//  2) if the mean value of the constant/exponential distribution is not negative;
//  3) if the size of both queues, when finite, is >= 0.
// If the parameters are not valid, a runtime exception is thrown.
void Cashier::checkParametersValidity()
{
    bool constantDistributionEnabled = par("constantServiceDistribution").boolValue();
    bool exponentialDistributionEnabled = par("exponentialServiceDistribution").boolValue();
    bool infiniteNormalCustomerQueueEnabled = par("infiniteNormalCustomerQueue").boolValue();
    bool infiniteVipCustomerQueueEnabled = par("infiniteVipCustomerQueue").boolValue();

    if (constantDistributionEnabled == exponentialDistributionEnabled ) {
        EV_ERROR << "No distribution or multiple ones selected for the service time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (constantDistributionEnabled && (par("constantServiceMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (exponentialDistributionEnabled && (par("exponentialServiceMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (!infiniteNormalCustomerQueueEnabled && (par("normalQueueSize").intValue() < 0) ) {
        EV_ERROR << "A negative size of the normal customer queue is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (!infiniteVipCustomerQueueEnabled && (par("vipQueueSize").intValue() < 0) ) {
        EV_ERROR << "A negative size of the VIP customer queue is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
}

// Registers the statistic signals.
void Cashier::initializeStatisticSignals()
{
    waitingTimeNormalCustomerCashierQueueSignal = registerSignal("waitingTimeNormalCustomerCashierQueue");
    waitingTimeVipCustomerCashierQueueSignal = registerSignal("waitingTimeVipCustomerCashierQueue");
    responseTimeNormalCustomerCashierNodeSignal = registerSignal("responseTimeNormalCustomerCashierNode");
    responseTimeVipCustomerCashierNodeSignal = registerSignal("responseTimeVipCustomerCashierNode");
    numberOfNormalCustomersCashierQueueSignal = registerSignal("numberOfNormalCustomersCashierQueue");
    numberOfVipCustomersCashierQueueSignal = registerSignal("numberOfVipCustomersCashierQueue");
    normalCustomerDropRateCashierSignal = registerSignal("normalCustomerDropRateCashier");
    vipCustomerDropRateCashierSignal = registerSignal("vipCustomerDropRateCashier");
    interDepartureTimeCashierSignal = registerSignal("interDepartureTimeCashier");
}

// Given an order, the method computes the waiting time of the customer and
// emits it according to the associated priority.
void Cashier::emitWaitingTime(OrderMessage* customerOrder)
{
    simtime_t waitingTime = customerOrder->getCashierQueueExitTime() - customerOrder->getCashierQueueArrivalTime();

    if (customerOrder->getVipPriority()) {
        emit(waitingTimeVipCustomerCashierQueueSignal, waitingTime);
    } else {
        emit(waitingTimeNormalCustomerCashierQueueSignal, waitingTime);
    }
}

// Given an order, the method computes the response time of the customer and
// emits it according to the associated priority.
void Cashier::emitResponseTime(OrderMessage* customerOrder)
{
    simtime_t responseTime = customerOrder->getCashierNodeDepartureTime() - customerOrder->getCashierQueueArrivalTime();

    if (customerOrder->getVipPriority()) {
        emit(responseTimeVipCustomerCashierNodeSignal, responseTime);
    } else {
        emit(responseTimeNormalCustomerCashierNodeSignal, responseTime);
    }
}

// Emits the size of a queue, identified by the parameter numberOfCustomers,
// according to its priority (vipQueue).
void Cashier::emitCustomerQueueSize(int numberOfCustomers, bool vipQueue)
{
    if (vipQueue) {
        emit(numberOfVipCustomersCashierQueueSignal, numberOfCustomers);
    } else {
        emit(numberOfNormalCustomersCashierQueueSignal, numberOfCustomers);
    }
}

// Emits the number of lost customers, according to their priority class.
void Cashier::emitDropRate(int numberOfLostCustomers, bool vipCustomer)
{
    if (vipCustomer) {
        emit(vipCustomerDropRateCashierSignal, numberOfLostCustomers);
    } else {
        emit(normalCustomerDropRateCashierSignal, numberOfLostCustomers);
    }
}

// Checks if the priority queue related to the arriving customer is full or not.
bool Cashier::customerQueueIsFull(OrderMessage* newOrder)
{
    bool infiniteNormalCustomerQueueEnabled = par("infiniteNormalCustomerQueue").boolValue();
    bool infiniteVipCustomerQueueEnabled = par("infiniteVipCustomerQueue").boolValue();
    unsigned int maxVipQueueSize = (unsigned int) par("vipQueueSize").intValue();
    unsigned int maxNormalQueueSize = (unsigned int) par("normalQueueSize").intValue();

    // The size check is more complex to avoid the loss of a customer when the size of a queue is 0, but the cashier is not occupied.
    // A simple check like "if (!infiniteCustomerQueueEnabled && (maxQueueSize == customerQueue.size()) then Drop" is not sufficient.
    if (newOrder->getVipPriority()) {
        if (infiniteVipCustomerQueueEnabled || (maxVipQueueSize > 0 && (vipCustomerQueue.size() < maxVipQueueSize)) || (maxVipQueueSize == 0 && !busy)) {
            emitDropRate(0, true);
            return false;
        } else {
            EV << "A VIP order has been dropped. The VIP customer queue is full." << endl;
            emitDropRate(1, true);
            return true;
	    }
    } else {
        if (infiniteNormalCustomerQueueEnabled || (maxNormalQueueSize > 0 && (normalCustomerQueue.size() < maxNormalQueueSize)) || (maxNormalQueueSize == 0 && !busy)) {
            emitDropRate(0, false);
            return false;
        } else {
            EV << "A normal order has been dropped. The normal customer queue is full." << endl;
            emitDropRate(1, false);
            return true;
        }
    }
}

// Generates the service time for the order that goes under service, according to the configured distribution.
double Cashier::generateServiceTime()
{
    double serviceTime = 0;

    if (par("constantServiceDistribution").boolValue()) {
        serviceTime = par("constantServiceMean").doubleValue();
    } else if (par("exponentialServiceDistribution").boolValue()) {
        serviceTime = exponential(par("exponentialServiceMean").doubleValue(), 2);
    }

    EV << "A new order went under service. Service time: " << serviceTime << endl;
    return serviceTime;
}

// Handles an arriving order, so that:
//  1) the customer is placed in a queue or dropped, if the queue is full;
//  2) the order goes under service if the cashier is not occupied;
//  3) the statistics are correctly recorded.
void Cashier::handleOrderArrival(cMessage* msg)
{
    OrderMessage* newOrder = check_and_cast<OrderMessage*>(msg);

    if (customerQueueIsFull(newOrder)) {
        delete newOrder;
        return;
    }

    newOrder->setCashierQueueArrivalTime(simTime());

    if(!busy) {
        newOrder->setCashierQueueExitTime(simTime());
        emitWaitingTime(newOrder);

        orderUnderService = newOrder;
        busy = true;
        scheduleAt(simTime() + generateServiceTime(), timerMessage);
    } else {
        if (newOrder->getVipPriority()) {
            vipCustomerQueue.push(newOrder);
            emitCustomerQueueSize(vipCustomerQueue.size(), true);
            EV << "A new VIP customer joined the queue. ";
            EV << "Number of customers in the queue: " << vipCustomerQueue.size() << endl;
        }
        else {
            normalCustomerQueue.push(newOrder);
            emitCustomerQueueSize(normalCustomerQueue.size(), false);
            EV << "A new normal customer joined the queue. ";
            EV << "Number of customers in the queue: " << normalCustomerQueue.size() << endl;
        }
    }
}

// Handles the completion of an order, so that:
//  1) the order corresponding to a served customer is sent through the "out" gate;
//  2) the next customer goes under service, according to the priority policy;
//  3) the statistics are correctly recorded.
void Cashier::completeOrder()
{
    orderUnderService->setCashierNodeDepartureTime(simTime());
    emitResponseTime(orderUnderService);

    emit(interDepartureTimeCashierSignal, simTime()-lastDepartureTime);
    lastDepartureTime = simTime();

    send(orderUnderService, "out");
    EV << "Order completed." << endl;

    if (vipCustomerQueue.empty() && normalCustomerQueue.empty()) {
        // For pure "safety" reason: avoid to delete a message that left the node.
        orderUnderService = NULL;

        busy = false;
        return;
    }

    // "busy" is still true here.
    if (!vipCustomerQueue.empty()) {
        orderUnderService = vipCustomerQueue.front();
        vipCustomerQueue.pop();
        emitCustomerQueueSize(vipCustomerQueue.size(), true);
    } else if (!normalCustomerQueue.empty()) {
        orderUnderService = normalCustomerQueue.front();
        normalCustomerQueue.pop();
        emitCustomerQueueSize(normalCustomerQueue.size(), false);
    }

    orderUnderService->setCashierQueueExitTime(simTime());
    emitWaitingTime(orderUnderService);

    scheduleAt(simTime() + generateServiceTime(), timerMessage);
}

// Initialization method: if the simulation parameters are valid, it ensures that
// the statistic signals are correctly registered and initialized.
void Cashier::initialize()
{
    checkParametersValidity();
    initializeStatisticSignals();

    timerMessage = new cMessage("timerMessage");
    busy = false;
    lastDepartureTime = simTime();

    // At the beginning, both queues are empty.
    emitCustomerQueueSize(normalCustomerQueue.size(), false);
    emitCustomerQueueSize(vipCustomerQueue.size(), true);
}

// Main handler.
void Cashier::handleMessage(cMessage* msg)
{
    if (msg->isSelfMessage()) {
        completeOrder();
    } else if (msg->isName("orderMessage")) {
        handleOrderArrival(msg);
    }
}
