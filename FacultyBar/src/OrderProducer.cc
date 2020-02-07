
#include "OrderProducer.h"

Define_Module(OrderProducer);


void OrderProducer::checkParametersValidity()
{
    bool constantDistributionEnabled = par("constantProductionDistribution").boolValue();
    bool exponentialDistributionEnabled = par("exponentialProductionDistribution").boolValue();

    if (constantDistributionEnabled == exponentialDistributionEnabled ) {
        EV_ERROR << "No distribution or multiple ones selected for the production time.";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (constantDistributionEnabled && (par("constantProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for a constant distribution is not allowed.";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }

    if (exponentialDistributionEnabled && (par("exponentialProductionMean").doubleValue() < 0)) {
        EV_ERROR << "A negative mean value for an exponential distribution is not allowed.";
        EV_ERROR << "Please check the correctness of your configuration file." << endl;
        endSimulation();
    }
}

double OrderProducer::generateProductionTime()
{
    double productionTime = 0;

    if (par("constantProductionDistribution").boolValue()) {
        productionTime = par("constantProductionMean").doubleValue();
    } else if (par("exponentialProductionDistribution").boolValue()){
        productionTime = exponential(par("exponentialProductionDistribution").doubleValue(), 0);
    }

    EV << "New production time: " << productionTime << endl;
    return productionTime;
}

void OrderProducer::sendNewOrder()
{

}

void OrderProducer::initialize()
{
    checkParametersValidity();

    timerMessage = new cMessage("timerMessage");
    scheduleAt(simTime() + generateProductionTime(), timerMessage);
}

void OrderProducer::handleMessage(cMessage *msg)
{
    if (msg->isSelfMessage()) {
        sendNewOrder();
    }

}