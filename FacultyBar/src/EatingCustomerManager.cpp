/*
 * EatingCustomerManager.cpp
 *
 *  Created on: Feb 11, 2020
 *      Author: iacopo
 */

#include "EatingCustomerManager.h"

EatingCustomerManager::EatingCustomerManager(int len) {
    EatingCostumersArray= new OrderMessage*[len];
    firstPositionFree=numberOfCustomerEating=0;
    arrayLength=len;
}

EatingCustomerManager::~EatingCustomerManager() {
    // TODO Auto-generated destructor stub
}

