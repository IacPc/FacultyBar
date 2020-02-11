/*
 * EatingCustomerManager.h
 *
 *  Created on: Feb 11, 2020
 *      Author: iacopo
 */

#ifndef EATINGCUSTOMERMANAGER_H_
#define EATINGCUSTOMERMANAGER_H_
#include "OrderMessage_m.h"

class EatingCustomerManager {

    int firstPositionFree;
    int arrayLength;
    int numberOfCustomerEating;
    OrderMessage** EatingCostumersArray;

public:
    EatingCustomerManager(int);
    virtual ~EatingCustomerManager();
};

#endif /* EATINGCUSTOMERMANAGER_H_ */
