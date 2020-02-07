
package facultybar;


simple Cashier
{
    parameters:
        bool constantServiceDistribution = default(false);
        bool exponentialServiceDistribution = default(false);
        double constantServiceMean @unit(s) = default(0s);
        double exponentialServiceMean @unit(s) = default(0s);
    gates:
        input in[2];
        output out;
}
