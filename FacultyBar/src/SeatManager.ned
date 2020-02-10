
package facultybar;


simple SeatManager
{
	parameters:
		bool constantEatingDistribution= default(false);
		bool exponentialEatingDistribution= default(false);
		double constantEatingMean @unit(s)= default(0s);
		double exponentialEatingMean @unit(s) = default(0s);
		int numberOfTables = default(0);
		int numberOfSeatsPerTable = default(0);
	gates:
	    input in;
}