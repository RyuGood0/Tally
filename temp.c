#include <stdio.h>
#include <math.h>
#include <stdint.h>


typedef struct dynamic_type {
	uint8_t type;
	void* value;
} dynamic_t;



int main(int argc, char *argv[]) {
	int a = 1;
	int b = 2 + 3;
	int c = b + 1;
	if (a > b) {
		printf("%d", a);
	} else {
		printf("%d", b);
	}
	int d = pow(a, b);
	const int e = 1;
	dynamic_t f = {.type = 0, .value = 2};
	char* g = "hello";
	printf("%s\n", g);
}