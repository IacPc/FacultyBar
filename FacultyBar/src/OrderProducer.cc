
#include "OrderProducer.h"
#include "OrderMessage_m.h"

Define_Module(OrderProducer);

OrderProducer::OrderProducer()
{
    timerMessage = NULL;
}

OrderProducer::~OrderProducer()
{
    cancelAndDelete(timerMessage);
}

void OrderProducer::checkParametersValidity()
{
    bool constantDistributionEnabled = par("constantProductionDistribution").boolValue();
    bool exponentialDistributionEnabled = par("exponentialProductionDistribution").boolValue();

    if (constantDistributionEnabled == exponentialDistributionEnabled ) {
        EV_ERROR << "No distribution or multiple ones selected for the production time. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (constantDistributionEnabled && (par("constantProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (exponentialDistributionEnabled && (par("exponentialProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed. ";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }
}

double OrderProducer::generateProductionTime()
{
    double productionTime = 0;

    if (par("constantProductionDistribution").boolValue()) {
        productionTime = par("constantProductionMean").doubleValue();
    } else if (par("exponentialProductionDistribution").boolValue()) {
        productionTime = exponential(par("exponentialProductionMean").doubleValue(), par("rngNumber").intValue());
    }

    EV << "New production time: " << productionTime << endl;
    return productionTime;
}

void OrderProducer::sendNewOrder()
{
    OrderMessage* newOrder = new OrderMessage("orderMessage");
    newOrder->setVipPriority(par("vipPriority").boolValue());

    send(newOrder, "out");
    EV << "New order sent." << endl;

    scheduleAt(simTime() + generateProductionTime(), timerMessage);
}

void OrderProducer::initialize()
{
    checkParametersValidity();

    timerMessage = new cMessage("timerMessage");
    scheduleAt(simTime() + generateProductionTime(), timerMessage);
}

void OrderProducer::handleMessage(cMessage* msg)
{
    if (msg->isSelfMessage()) {
        sendNewOrder();
    }
}
