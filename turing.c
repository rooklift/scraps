// This is a Turing machine simulator.
// It allocates memory dynamically as needed, using a linked-list system.

#include <stdio.h>
#include <stdlib.h>

#define BLOCKSIZE 1000

#define LEFT -1
#define RIGHT 1

#define STATES 5

#define HALT -1

#define A 0
#define B 1
#define C 2
#define D 3
#define E 4

struct block_struct {
	char * memory;
	struct block_struct * previous;
	struct block_struct * next;
};

int movement[STATES][2];
int output[STATES][2];
int newstate[STATES][2];

void setrules (void)
{
	movement[A][0] = RIGHT;
	movement[A][1] = LEFT;
	movement[B][0] = RIGHT;
	movement[B][1] = RIGHT;
	movement[C][0] = RIGHT;
	movement[C][1] = LEFT;
	movement[D][0] = LEFT;
	movement[D][1] = LEFT;
	movement[E][0] = RIGHT;
	movement[E][1] = LEFT;

	output[A][0] = 1;
	output[A][1] = 1;
	output[B][0] = 1;
	output[B][1] = 1;
	output[C][0] = 1;
	output[C][1] = 0;
	output[D][0] = 1;
	output[D][1] = 1;
	output[E][0] = 1;
	output[E][1] = 0;

	newstate[A][0] = B;
	newstate[A][1] = C;
	newstate[B][0] = C;
	newstate[B][1] = B;
	newstate[C][0] = D;
	newstate[C][1] = E;
	newstate[D][0] = A;
	newstate[D][1] = D;
	newstate[E][0] = HALT;
	newstate[E][1] = A;
	
	return;
}

void oom (void)
{
	printf("OUT OF MEMORY! ALAS!\n");
	exit(0);
}

struct block_struct * initialise (struct block_struct * previous, struct block_struct * next)
{
	struct block_struct * this;
	
	this = malloc(sizeof(struct block_struct));
	if (this == NULL) oom();
	
	this->previous = previous;
	this->next = next;
	
	this->memory = calloc(BLOCKSIZE, sizeof(char));
	if (this->memory == NULL) oom();
	
	return this;
}

int main (void)
{
	int state = A;
	
	int iterations = 0;
	int ones = 0;
	int seen = 0;
	int zeroes = 0;
	
	struct block_struct * block;
	int location;
	
	setrules();
	
	block = initialise(NULL, NULL);
	location = 0;
	
	int displacement;
	int writethis;
	int nextstate;
	
	while (1)
	{
		iterations++;
		
		displacement = movement[state][block->memory[location]];
		writethis = output[state][block->memory[location]];
		nextstate = newstate[state][block->memory[location]];
		
		block->memory[location] = writethis;
		location += displacement;
		state = nextstate;
		
		if (state == HALT) break;
		
		if (location == -1)
		{
			if (block->previous == NULL)
			{
				block->previous = initialise(NULL, block);
			}
			block = block->previous;
			location = BLOCKSIZE - 1;
		} else if (location == BLOCKSIZE) {
			if (block->next == NULL)
			{
				block->next = initialise(block, NULL);
			}
			block = block->next;
			location = 0;
		}
	}
	
	/* -------- What follows is just non-essential reporting code. -------- */
	
	printf("Halted after %d iterations.\n", iterations);
	
	// Find leftmost block...
	while (1)
	{
		if (block->previous != NULL)
		{
			block = block->previous;
		} else {
			break;
		}
	}
	
	// Count the ones on the whole tape...
	location = 0;
	while (1)
	{
		if (block->memory[location] == 1)
		{
			ones++;
		}
		location++;
		if (location == BLOCKSIZE) {
			if (block->next != NULL)
			{
				block = block->next;
				location = 0;
			} else {
				break;
			}
		}
	}
	
	// Find leftmost block again...
	while (1)
	{
		if (block->previous != NULL)
		{
			block = block->previous;
		} else {
			break;
		}
	}
	
	// Count the zeroes interspersed in the ones...
	location = 0;
	while (1)
	{
		if (block->memory[location] == 1)
		{
			seen++;			// The number of ones seen on the tape so far.
			if (seen == ones) break;
		} else {
			if (seen > 0)
			{
				zeroes++;
			}
		}
		location++;
		if (location == BLOCKSIZE) {
			if (block->next != NULL)
			{
				block = block->next;
				location = 0;
			} else {
				break;
			}
		}
	}
	
	printf("There are %d ones on the tape.\n", ones);
	printf("There are %d zeroes interspersed among the ones.\n", zeroes);
		
	return 0;
}
