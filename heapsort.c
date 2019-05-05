// Super old attempt at heapsort I made 20 years ago, who knows if it even works?
// Not gonna check.

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>

struct node {
	int value;
	struct node * childa;
	struct node * childb;
	struct node * parent;
	};

struct heap {
	struct node * root;
	int size;
	};

float rnd (void) // Random number between 0 and 1...
{
	return (float) rand() / RAND_MAX;
}

int intrnd (int max) // Random integer between 0 and max inclusive...
{
	int result;

	result = rnd() * (max + 1);
	result %= max + 1;
	return result;
}

void error(char * msg)
{
	fprintf(stderr, "ERROR: ");
	fprintf(stderr, msg);
	fprintf(stderr, "\n");
	exit(1);
}

struct node * newnode(int value)
{
	struct node * n;

	n = malloc(sizeof(struct node));
	if (n == NULL)
	{
		error("Out of memory");
	}

	n->value = value;
	n->childa = NULL;
	n->childb = NULL;
	n->parent = NULL;

	return n;
}

struct heap * newheap(void)
{
	struct heap * h;
	h = malloc(sizeof(struct heap));
	if (h == NULL)
	{
		error("Out of memory");
	}

	h->root = NULL;
	h->size = 0;

	return h;
}

void swapvalues(struct node * a, struct node * b)
{
	int tmp;

	if (a == NULL || b == NULL) error("Attempt to swap with NULL pointer");

	tmp = a->value;
	a->value = b->value;
	b->value = tmp;

	return;
}

struct node * compare(struct node * a, struct node * b)		// Returns node that should be top
{
	if (a == NULL && b == NULL)
	{
		error("Comparison involving two NULL pointers");
	}

	if (a == NULL) return b;
	if (b == NULL) return a;

	if (a->value <= b->value)			// Make this >= to switch between min and max heap.
	{
		return a;
	} else {
		return b;
	}
}

struct node * findgoodloser(struct node * n)		// Go down tree (prefering higher priority) until tip
{
	struct node * ret;

	if (n->childa == NULL && n->childb == NULL)
	{
		ret = n;
	} else if (n->childa == NULL) {
		ret = findgoodloser(n->childb);
	} else if (n->childb == NULL) {
		ret = findgoodloser(n->childa);
	} else {
		ret = findgoodloser(compare(n->childa, n->childb));
	}

	assert(ret != NULL);
	assert(ret->parent != NULL);
	assert(ret->childa == NULL && ret->childb == NULL);

	return ret;
}

int pop(struct heap * h)
{
	int ret;
	struct node * gl;
	struct node * n;
	struct node * tar;

	if (h->size <= 0)
	{
		error("Attempt to pop on heap with size <= 0");
	}

	ret = h->root->value;

	if (h->size > 1)		// i.e. if heap will not be empty after pop
	{
		gl = findgoodloser(h->root);

		if (gl->parent->childa == gl)
		{
			gl->parent->childa = NULL;
		} else {
			gl->parent->childb = NULL;
		}
		swapvalues(gl, h->root);
		free(gl);
		h->size--;

		// Now a bad value is (probably) at the root, bubble it down...

		n = h->root;
		while (1)
		{
			if (compare(n, n->childa) == n && compare(n, n->childb) == n) break;		// n is actually correctly placed

			tar = compare(n->childa, n->childb);										// Which child has priority?
			swapvalues(tar, n);
			n = tar;
		}
	} else {
		h->size = 0;
		free(h->root);
		h->root = NULL;
	}

	return ret;
}

struct node * findfreespot (struct node * n)		// Returns a node that has only one or zero child nodes
{
	struct node * ret;

	if (n->childa == NULL || n->childb == NULL)
	{
		ret = n;
	} else {
		if (rnd() < 0.5)											// There must be a better way...
		{
			ret = findfreespot(n->childa);
		} else {
			ret = findfreespot(n->childb);
		}
	}

	assert(ret != NULL);
	return ret;
}

void push(struct heap * h, int value)
{
	struct node * n;
	struct node * parent = NULL;

	n = newnode(value);

	if (h->size == 0)
	{
		h->root = n;
		h->size = 1;
		return;
	}

	n->parent = findfreespot(h->root);
	if (n->parent->childa == NULL)
	{
		n->parent->childa = n;
	} else {
		n->parent->childb = n;
	}

	h->size++;

	// Now a bad value is (probably) at the branch tip, bubble it up...

	while (1)
	{
		if (n->parent == NULL) break;
		if (compare(n, n->parent) == n->parent) break;

		swapvalues(n, n->parent);
		n = n->parent;
	}

	return;
}

int main (void)
{
	struct heap * h;
	int n;

	h = newheap();

	for (n = 0; n < 100; n++)
	{
		push(h, intrnd(1000));
	}

	n = 0;
	while (h->size > 0)
	{
		n++;
		printf("%3d: %d\n", n, pop(h));
	}

	return 0;
}
