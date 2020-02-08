
package facultybar;


simple SeatManager
{
	parameters:
		bool constantEatingDistribution= default(false);
		bool exponentialEatingDistribution= default(false);
		double constantEatingMean @unit(s)= default(10s);
		double exponentialEatingMean @unit(s) = default(5);
		int totalTableNumber = default(50);
	gates:
	    input in;
}