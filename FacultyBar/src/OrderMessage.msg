
message OrderMessage {
  bool vipPriority;
  int positionInArray;
  simtime_t cashierQueueArrivalTime;
  simtime_t cashierQueueExitTime;
  simtime_t cashierNodeDepartureTime;
  simtime_t seatManagerQueueArrivalTime;
  simtime_t seatManagerQueueExitTime;
  simtime_t seatManagerNodeDepartureTime;
}