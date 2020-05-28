
package facultybar;


simple Cashier
{
    parameters:
        int rngNumber = default(0);
        bool constantServiceDistribution = default(false);
        bool exponentialServiceDistribution = default(false);
        double constantServiceMean @unit(s) = default(0s);
        double exponentialServiceMean @unit(s) = default(0s);
        
        bool infiniteNormalCustomerQueue = default(false);
        bool infiniteVipCustomerQueue = default(false);
        int normalQueueSize = default(0);
        int vipQueueSize = default(0);
        
        // Statistics
        @signal[waitingTimeNormalCustomerCashierQueue](type = simtime_t);
        @signal[waitingTimeVipCustomerCashierQueue](type = simtime_t);
        @signal[responseTimeNormalCustomerCashierNode](type = simtime_t);
        @signal[responseTimeVipCustomerCashierNode](type = simtime_t);
        @signal[numberOfNormalCustomersCashierQueue](type = long);
        @signal[numberOfVipCustomersCashierQueue](type = long);        
        @signal[normalCustomerDropRateCashier](type = double);
        @signal[vipCustomerDropRateCashier](type = double);
        @signal[interDepartureTimeCashier](type = simtime_t);
        
        @statistic[waitingTimeNormalCustomerCashierQueueStatistic](source = "waitingTimeNormalCustomerCashierQueue"; record = vector);
      	@statistic[waitingTimeVipCustomerCashierQueueStatistic](source = "waitingTimeVipCustomerCashierQueue"; record = vector);
      	@statistic[responseTimeNormalCustomerCashierNodeStatistic](source = "responseTimeNormalCustomerCashierNode"; record = vector);
      	@statistic[responseTimeVipCustomerCashierNodeStatistic](source = "responseTimeVipCustomerCashierNode"; record = vector);
      	@statistic[numberOfNormalCustomersCashierQueueStatistic](source = "numberOfNormalCustomersCashierQueue"; record = vector, timeavg);
      	@statistic[numberOfVipCustomersCashierQueueStatistic](source = "numberOfVipCustomersCashierQueue"; record = vector, timeavg);
      	@statistic[normalCustomerDropRateCashierStatistic](source = "normalCustomerDropRateCashier"; record = mean);
      	@statistic[vipCustomerDropRateCashierStatistic](source = "vipCustomerDropRateCashier"; record = mean);
      	@statistic[interDepartureTimeCashierStatistic](source = "interDepartureTimeCashier"; record = vector);
      	
    gates:
        input in[2];
        output out;
}
