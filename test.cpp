#include <iostream>

int main(){
	int cnt =0;
	double f;
	for(int i=0; i<10; i++){
		cnt ++;
		if(cnt > 5)
			f =+ cnt;
		else
			f -= cnt;
	}	
	return 0;
}
