
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
		
		// Statistics
		@signal [waitingTimeNormalCustomerTableQueue](type = simtime_t);
		@signal[waitingTimeVipCustomerTableQueue](type = simtime_t);		
		@signal[responseTimeNormalCustomerTableNode](type = simtime_t);
		@signal[responseTimeVipCustomerTableNode](type = simtime_t);		
		@signal[numberOfCustomersTableQueue](type = unsigned long);
		@signal[customerDropRateTable](type = double);
		@signal[throughput](type = double);
								
		@statistic[waitingTimeNormalCustomerTableQueueStatistic](source = "waitingTimeNormalCustomerTableQueue"; record = vector);
		@statistic[waitingTimeVipCustomerTableQueueStatistic](source = "waitingTimeVipCustomerTableQueue"; record = vector);
		@statistic[responseTimeNormalCustomerTableNodeStatistic](source = "responseTimeNormalCustomerTableNode"; record = vector);
		@statistic[responseTimeVipCustomerTableNodeStatistic](source = "responseTimeVipCustomerTableNode"; record = vector);
		@statistic[numberOfCustomersTableQueueStatistic](source = "numberOfCustomersTableQueue"; record = vector, timeavg);
		@statistic[customerDropRateTableStatistic](source = "customerDropRateTable"; record = mean);
		@statistic[throughputStatistic](source = "throughput"; record = vector);
						
	gates:
	    input in;
}