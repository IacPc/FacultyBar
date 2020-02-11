
#include "Cashier.h"

Define_Module(Cashier);

Cashier::Cashier()
{
    timerMessage = NULL;
    orderUnderService = NULL;
}

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

void Cashier::checkParametersValidity()
{
    bool constantDistributionEnabled = par("constantServiceDistribution").boolValue();
    bool exponentialDistributionEnabled = par("exponentialServiceDistribution").boolValue();

    if (constantDistributionEnabled == exponentialDistributionEnabled ) {
        EV_ERROR << "No distribution or multiple ones selected for the service time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (constantDistributionEnabled && (par("constantServiceMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (exponentialDistributionEnabled && (par("exponentialServiceMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }
}

void Cashier::initializeStatisticSignals()
{
    waitingTimeNormalCustomerCashierQueueSignal = registerSignal("waitingTimeNormalCustomerCashierQueue");
    waitingTimeVipCustomerCashierQueueSignal = registerSignal("waitingTimeVipCustomerCashierQueue");
    responseTimeNormalCustomerCashierNodeSignal = registerSignal("responseTimeNormalCustomerCashierNode");
    responseTimeVipCustomerCashierNodeSignal = registerSignal("responseTimeVipCustomerCashierNode");
    numberOfNormalCustomersCashierQueueSignal = registerSignal("numberOfNormalCustomersCashierQueue");
    numberOfVipCustomersCashierQueueSignal = registerSignal("numberOfVipCustomersCashierQueue");
}

void Cashier::emitWaitingTime(OrderMessage* customerOrder)
{
    simtime_t waitingTime = customerOrder->getCashierQueueExitTime() - customerOrder->getCashierQueueArrivalTime();

    if (customerOrder->getVipPriority()) {
        emit(waitingTimeVipCustomerCashierQueueSignal, waitingTime);
    } else {
        emit(waitingTimeNormalCustomerCashierQueueSignal, waitingTime);
    }
}

void Cashier::emitResponseTime(OrderMessage* customerOrder)
{
    simtime_t responseTime = customerOrder->getCashierNodeDepartureTime() - customerOrder->getCashierQueueArrivalTime();

    if (customerOrder->getVipPriority()) {
        emit(responseTimeVipCustomerCashierNodeSignal, responseTime);
    } else {
        emit(responseTimeNormalCustomerCashierNodeSignal, responseTime);
    }
}

void Cashier::emitCustomerQueueSize(int numberOfCustomers, bool vipQueue)
{
    if (vipQueue) {
        emit(numberOfVipCustomersCashierQueueSignal, numberOfCustomers);
    } else {
        emit(numberOfNormalCustomersCashierQueueSignal, numberOfCustomers);
    }
}

double Cashier::generateServiceTime()
{
    double serviceTime = 0;

    if (par("constantServiceDistribution").boolValue()) {
        serviceTime = par("constantServiceMean").doubleValue();
    } else if (par("exponentialServiceDistribution").boolValue()){
        serviceTime = exponential(par("exponentialServiceMean").doubleValue(), 2);
    }

    EV << "New service time: " << serviceTime << endl;
    return serviceTime;
}

void Cashier::handleOrderArrival(cMessage* msg)
{
    OrderMessage* newOrder = check_and_cast<OrderMessage*>(msg);
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
            EV << "New VIP order queued." << endl;
        }
        else {
            normalCustomerQueue.push(newOrder);
            emitCustomerQueueSize(normalCustomerQueue.size(), false);
            EV << "New normal order queued." << endl;
        }
    }
}

void Cashier::completeOrder()
{
    orderUnderService->setCashierNodeDepartureTime(simTime());
    emitResponseTime(orderUnderService);

    send(orderUnderService, "out");
    EV << "New order completed." << endl;

    if (vipCustomerQueue.empty() && normalCustomerQueue.empty()) {
        // For pure "safety" reason: avoid to delete a message that leaved the node,
        // though Omnet prevents doing it without the message ownership.
        orderUnderService = NULL;

        busy = false;
        return;
    }

    // busy is still true here
    if (!vipCustomerQueue.empty()) {
        orderUnderService = vipCustomerQueue.front();
        vipCustomerQueue.pop();
        emitCustomerQueueSize(vipCustomerQueue.size(), true);
    } else if (!normalCustomerQueue.empty()) {
        orderUnderService = normalCustomerQueue.front();
        normalCustomerQueue.pop();
        emitCustomerQueueSize(normalCustomerQueue.size(), true);
    }

    orderUnderService->setCashierQueueExitTime(simTime());
    emitWaitingTime(orderUnderService);

    scheduleAt(simTime() + generateServiceTime(), timerMessage);
}

void Cashier::initialize()
{
    checkParametersValidity();
    initializeStatisticSignals();

    timerMessage = new cMessage("timerMessage");
    busy = false;

    // At the beginning, both queues are empty
    emitCustomerQueueSize(normalCustomerQueue.size(), false);
    emitCustomerQueueSize(vipCustomerQueue.size(), true);
}

void Cashier::handleMessage(cMessage* msg)
{
    if (msg->isSelfMessage()) {
        completeOrder();
    } else if (strcmp(msg->getName(), "orderMessage") == 0) {
        handleOrderArrival(msg);
    }
}
