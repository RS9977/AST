#include <stdio.h>

int main(){
	int a = 0;
	int b = 1;
	int c = a+b;
	int cnt = 3;	
	for(int i=0; i<10; i++)
		if(cnt<5)
			cnt++;
	return 1;
}
