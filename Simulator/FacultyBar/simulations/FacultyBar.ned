
package facultybar.simulations;

import facultybar.*;


network FacultyBar
{
    submodules:
        normalOrderProducer: OrderProducer {rngNumber = 0;};
        vipOrderProducer: OrderProducer {rngNumber = 1; vipPriority = true;};
        cashier: Cashier {rngNumber = 2;};
        seatManager: SeatManager {rngNumber = 3;};
    connections:
        normalOrderProducer.out --> cashier.in[0];
        vipOrderProducer.out --> cashier.in[1];
        cashier.out --> seatManager.in;
}
