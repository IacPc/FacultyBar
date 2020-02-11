
package facultybar.simulations;

//import facultybar.Cashier;
import facultybar.*;
//import facultybar.OrderProducer;

network FacultyBar
{
    submodules:
        normalOrderProducer: OrderProducer {rngNumber = 0;};
        vipOrderProducer: OrderProducer {rngNumber = 1; vipPriority = true;};
        cashier: Cashier;
        seatManager: SeatManager;
    connections:
        normalOrderProducer.out --> cashier.in[0];
        vipOrderProducer.out --> cashier.in[1];
        cashier.out --> seatManager.in;
}
