
package facultybar;


simple OrderProducer
{
    parameters:
        bool vipPriority = default(false);
        bool constantProductionDistribution = default(false);
        bool exponentialProductionDistribution = default(false);
        double constantProductionMean = default(0);
        double exponentialProductionMean = default(0);
	gates:
	    output out;
}
