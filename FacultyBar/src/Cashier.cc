
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

void Cashier::emitDropRate(int numberOfLostCustomers, bool vipCustomer)
{
    if (vipCustomer) {
        emit(vipCustomerDropRateCashierSignal, numberOfLostCustomers);
    } else {
        emit(normalCustomerDropRateCashierSignal, numberOfLostCustomers);
    }
}

bool Cashier::customerQueueIsFull(OrderMessage* newOrder)
{
    bool infiniteNormalCustomerQueueEnabled = par("infiniteNormalCustomerQueue").boolValue();
    bool infiniteVipCustomerQueueEnabled = par("infiniteVipCustomerQueue").boolValue();
    unsigned int maxVipQueueSize = (unsigned int) par("vipQueueSize").intValue();
    unsigned int maxNormalQueueSize = (unsigned int) par("normalQueueSize").intValue();

    bool fullQueue = false;
    bool vipCustomer = newOrder->getVipPriority();
    int numberOfLostCustomers = 0;

    if (vipCustomer) {
        if (!infiniteVipCustomerQueueEnabled && (maxVipQueueSize == vipCustomerQueue.size())) {
            fullQueue = true;
            numberOfLostCustomers = 1;
            EV << "A VIP order has been dropped. The VIP customer queue is full." << endl;
        }
    } else {
        if (!infiniteNormalCustomerQueueEnabled && (maxNormalQueueSize == normalCustomerQueue.size())) {
            fullQueue = true;
            numberOfLostCustomers = 1;
            EV << "A normal order has been dropped. The normal customer queue is full." << endl;
        }
    }

    emitDropRate(numberOfLostCustomers, vipCustomer);
    return fullQueue;
}

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

void Cashier::completeOrder()
{
    orderUnderService->setCashierNodeDepartureTime(simTime());
    emitResponseTime(orderUnderService);

    send(orderUnderService, "out");
    EV << "Order completed." << endl;

    if (vipCustomerQueue.empty() && normalCustomerQueue.empty()) {
        // For pure "safety" reason: avoid to delete a message that left the node
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
        emitCustomerQueueSize(normalCustomerQueue.size(), false);
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
    } else if (msg->isName("orderMessage")) {
        handleOrderArrival(msg);
    }
}
