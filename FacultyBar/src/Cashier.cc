
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
        orderUnderService = newOrder;
        busy = true;
        scheduleAt(simTime() + generateServiceTime(), timerMessage);
    } else {
        if (newOrder->getVipPriority()) {
            vipCustomerQueue.push(newOrder);
            EV << "New VIP order queued." << endl;
        }
        else {
            normalCustomerQueue.push(newOrder);
            EV << "New normal order queued." << endl;
        }
    }
}

void Cashier::completeOrder()
{
    orderUnderService->setCashierNodeDepartureTime(simTime());
    send(orderUnderService, "out");
    EV << "New order completed." << endl;

    if (vipCustomerQueue.empty() && normalCustomerQueue.empty()) {
        orderUnderService = NULL; // For pure "safety" reason
        busy = false;
        return;
    }

    // busy is still true here
    if (!vipCustomerQueue.empty()) {
        orderUnderService = vipCustomerQueue.front();
        vipCustomerQueue.pop();
    } else if (!normalCustomerQueue.empty()) {
        orderUnderService = normalCustomerQueue.front();
        normalCustomerQueue.pop();
    }

    orderUnderService->setCashierQueueExitTime(simTime());
    scheduleAt(simTime() + generateServiceTime(), timerMessage);
}

void Cashier::initialize()
{
    checkParametersValidity();
    timerMessage = new cMessage("timerMessage");
    busy = false;
}

void Cashier::handleMessage(cMessage* msg)
{
    if (msg->isSelfMessage()) {
        completeOrder();
    } else if (strcmp(msg->getName(), "orderMessage") == 0) {
        handleOrderArrival(msg);
    }
}
