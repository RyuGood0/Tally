#include <math.h>




int main(int argc, char *argv[]) {
	int a = 1;
	int b = 2 + 3;
	int c = b + 1;
	if (a > b) {
		printf("%d\n", a);
	} else {
		printf("%d\n", b);
	}
	int d = pow(a, b);
	const int e = 1;
	dynamic_t* f = init_dynamic_var(STRING, (void*)"hi");
	printf("hello%d%s\n", e, f);
	printf("%s\n", f);
	f = update_dynamic_var(f, INT, (void*)&(int){1});
	printf("%s\n", f);
	char* g = "hello";
	printf("%s\n", g);
}