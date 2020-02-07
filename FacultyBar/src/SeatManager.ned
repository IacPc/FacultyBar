
package facultybar;


simple SeatManager
{
	parameters:
		bool constantEatingDistribution= default(true);
		bool exponentialEatingDistribution= default(false);
		double constantInfLimit @unit(s)= default(10s);
		double constantSupLimit @unit(s)= default(600s);
		double exponentialEatingMean = default(5);
		int totalTableNumber = default(50);
	gates:
	    input in;
}