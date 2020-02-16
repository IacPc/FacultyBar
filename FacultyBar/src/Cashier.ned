
package facultybar;


simple Cashier
{
    parameters:
        bool constantServiceDistribution = default(false);
        bool exponentialServiceDistribution = default(false);
        double constantServiceMean @unit(s) = default(0s);
        double exponentialServiceMean @unit(s) = default(0s);
        
        // Statistics
        @signal[waitingTimeNormalCustomerCashierQueue](type = simtime_t);
        @signal[waitingTimeVipCustomerCashierQueue](type = simtime_t);
        @signal[responseTimeNormalCustomerCashierNode](type = simtime_t);
        @signal[responseTimeVipCustomerCashierNode](type = simtime_t);
        @signal[numberOfNormalCustomersCashierQueue](type = long);
        @signal[numberOfVipCustomersCashierQueue](type = long);
        
        @statistic[waitingTimeNormalCustomerCashierQueueStatistic](source = waitingTimeNormalCustomerCashierQueue; record = vector);
      	@statistic[waitingTimeVipCustomerCashierQueueStatistic](source = waitingTimeVipCustomerCashierQueue; record = vector);
      	@statistic[responseTimeNormalCustomerCashierNodeStatistic](source = responseTimeNormalCustomerCashierNode; record = vector);
      	@statistic[responseTimeVipCustomerCashierNodeStatistic](source = responseTimeVipCustomerCashierNode; record = vector);
      	@statistic[numberOfNormalCustomersCashierQueueStatistic](source = numberOfNormalCustomersCashierQueue; record = vector);
      	@statistic[numberOfVipCustomersCashierQueueStatistic](source = numberOfVipCustomersCashierQueue; record = vector);
      
    gates:
        input in[2];
        output out;
}
