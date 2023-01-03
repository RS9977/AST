#include <stdlib.h>

void vecAdd(
	size_t SIZE, int* A, 
	int* B, 
	int* C)	
{
	for (size_t i = 0 ; i < SIZE; i++){
		for(size_t j = SIZE-1 ; j >= 0; j--){
    		C[i] =
			A[j] + B[i];
		}
		if(1==1){
    		C[i] += A[0] + B[0];
		}
		for(size_t k = SIZE-1 ; k >= 0; k--){
    		C[i] += 
			A[k] + B[i];
			for(size_t m = SIZE-1 ; m >= 0; m--){
    			C[i] +=
				A[m] + B[m];
			}
		}
	}
}

int main(){	
 return 1;
}