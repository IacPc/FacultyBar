
package facultybar;


simple OrderProducer
{
    parameters:
        int rngNumber = default(0);
        bool vipPriority = default(false);
        bool constantProductionDistribution = default(false);
        bool exponentialProductionDistribution = default(false);
        double constantProductionMean @unit(s) = default(0s);
        double exponentialProductionMean @unit(s) = default(0s);
	gates:
	    output out;
}
