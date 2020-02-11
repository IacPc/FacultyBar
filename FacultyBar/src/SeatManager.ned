
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
		
		//signals
		@signal [waitingTimeNormalCustomerTableQueue](type=double);
		@statistic[waitingTimeNormalCustomerTableQueueStatistic](source="waitingTimeNormalCustomerTableQueue";record= vector);
		
		@signal[waitingTimeVipCustomerTableQueue](type=double);
		@statistic[waitingTimeVipCustomerTableQueueStatistic](source="waitingTimeVipCustomerTableQueue";record= vector);
		
		@signal[responseTimeNormalCustomerTableNode](type=double);
		@statistic[responseTimeNormalCustomerTableNodeStatistic](source="responseTimeNormalCustomerTableNode";record= vector);
		
		@signal[responseTimeVipCustomerTableNode](type=double);
		@statistic[responseTimeVipCustomerTableNodeStatistic](source="responseTimeVipCustomerTableNode";record= vector);
		
		@signal[numberOfCustomersTableQueue](type=double);
		@statistic[numberOfNormalCustomersTableQueueStatistic](source="numberOfCustomersTableQueue";record= vector);
		
						
	gates:
	    input in;
}