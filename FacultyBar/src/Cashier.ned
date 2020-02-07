
package facultybar;


simple Cashier
{
    parameters:
        bool constantServiceDistribution = default(false);
        bool exponentialServiceDistribution = default(false);
        double constantServiceMean = default(0);
        double exponentialServiceMean = default(0);
    gates:
        input in[2];
        output out;
}
