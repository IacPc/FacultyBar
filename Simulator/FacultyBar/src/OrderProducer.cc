
#include "OrderProducer.h"
#include "OrderMessage_m.h"

Define_Module(OrderProducer);

// Constructor.
OrderProducer::OrderProducer()
{
    timerMessage = NULL;
}

// Destructor.
OrderProducer::~OrderProducer()
{
    cancelAndDelete(timerMessage);
}

// Checks if the simulation parameters in the configuration file are valid, namely:
//  1) if a distribution for the production of the messages has been set uniquely;
//  2) if the mean value of the constant/exponential distribution is not negative.
// If the parameters are not valid, a runtime exception is thrown.
void OrderProducer::checkParametersValidity()
{
    bool constantDistributionEnabled = par("constantProductionDistribution").boolValue();
    bool exponentialDistributionEnabled = par("exponentialProductionDistribution").boolValue();

    if (constantDistributionEnabled == exponentialDistributionEnabled ) {
        EV_ERROR << "No distribution or multiple ones selected for the production time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (constantDistributionEnabled && (par("constantProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }

    if (exponentialDistributionEnabled && (par("exponentialProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        throw cRuntimeError("Invalid parameters");
    }
}

// Generates the production time for the next order, according to the configured distribution.
double OrderProducer::generateProductionTime()
{
    double productionTime = 0;

    if (par("constantProductionDistribution").boolValue()) {
        productionTime = par("constantProductionMean").doubleValue();
    } else if (par("exponentialProductionDistribution").boolValue()) {
        productionTime = exponential(par("exponentialProductionMean").doubleValue(), par("rngNumber").intValue());
    }

    EV << "A new order went into production. Production time: " << productionTime << endl;
    return productionTime;
}

// Sends a produced order through the "out" gate and triggers the next production cycle.
void OrderProducer::sendNewOrder()
{
    OrderMessage* newOrder = new OrderMessage("orderMessage");
    newOrder->setVipPriority(par("vipPriority").boolValue());

    if (!newOrder->getVipPriority()) {
        // Normal customers must have lower FES scheduling priority, so that if
        // a normal customer arrives at the cashier at the same simulation time
        // of a VIP customer, the VIP is always served before.
        newOrder->setSchedulingPriority(1);
    }

    send(newOrder, "out");
    EV << "New order sent." << endl;

    scheduleAt(simTime() + generateProductionTime(), timerMessage);
}

// Initialization method: if the simulation parameters are valid,
// the method triggers the first production of an order.
void OrderProducer::initialize()
{
    checkParametersValidity();

    timerMessage = new cMessage("timerMessage");
    scheduleAt(simTime() + generateProductionTime(), timerMessage);
}

// Main handler.
void OrderProducer::handleMessage(cMessage* msg)
{
    if (msg->isSelfMessage()) {
        sendNewOrder();
    }
}
