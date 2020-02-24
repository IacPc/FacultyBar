
package facultybar;


simple SeatManager
{
	parameters:
		bool constantEatingDistribution = default(false);
		bool exponentialEatingDistribution = default(false);
		double constantEatingMean @unit(s) = default(0s);
		double exponentialEatingMean @unit(s) = default(0s);
		bool infiniteCustomerQueue = default(false);
		int queueSize = default(0);
		int numberOfSeats = default(0);
		
		// Signals
		@signal [waitingTimeNormalCustomerTableQueue](type = simtime_t);
		@statistic[waitingTimeNormalCustomerTableQueueStatistic](source = "waitingTimeNormalCustomerTableQueue"; record = vector);
		
		@signal[waitingTimeVipCustomerTableQueue](type = simtime_t);
		@statistic[waitingTimeVipCustomerTableQueueStatistic](source = "waitingTimeVipCustomerTableQueue"; record = vector);
		
		@signal[responseTimeNormalCustomerTableNode](type = simtime_t);
		@statistic[responseTimeNormalCustomerTableNodeStatistic](source = "responseTimeNormalCustomerTableNode"; record = vector);
		
		@signal[responseTimeVipCustomerTableNode](type = simtime_t);
		@statistic[responseTimeVipCustomerTableNodeStatistic](source = "responseTimeVipCustomerTableNode"; record = vector);
		
		@signal[numberOfCustomersTableQueue](type = unsigned long);
		@statistic[numberOfCustomersTableQueueStatistic](source = "numberOfCustomersTableQueue"; record = vector);
						
	gates:
	    input in;
}