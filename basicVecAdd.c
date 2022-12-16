#include <stdlib.h>

void vecAdd(
	size_t SIZE, int* A, 
	int* B, 
	int* C)	
{
	
	for (size_t i = 0 ; i < SIZE; i++)
    	C[i] = A[i] + B[i];
}

int main(){
	
 return 1;
}