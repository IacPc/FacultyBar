
package FacultyBar.simulations;

import FacultyBar.OrderProducer;
import FacultyBar.Cashier;
import FacultyBar.SeatManager;

network FacultyBar
{
    submodules:
        normalOrderProducer: OrderProducer;
        vipOrderProducer: OrderProducer {vipPriority = true;};
        cashier: Cashier;
        seatManager: SeatManager;
    connections:
        normalOrderProducer.out --> cashier.in[0];
        vipOrderProducer.out --> cashier.in[1];
        cashier.out --> seatManager.in;
}
