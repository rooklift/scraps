// Super old attempt at quicksort I made 20 years ago, who knows if it even works?
// Not gonna check.

#include <stdio.h>
#include <assert.h>

#define MAX 20

void quicksort (int * startptr, int numberstosort);
int pseudorand (void);



// Main calls the PRNG to fill up the array, then calls quicksort to sort it,
// then prints it.

int main(void) {

int numbersinarray = 0;
int n;
int spoo[MAX];


for (n = 0; n < MAX; n++)
{
   spoo[n] = pseudorand();
   numbersinarray++;
}

quicksort(&spoo[0], numbersinarray);

printf("\n");
for (n = 0; n < numbersinarray; n++)
{
   printf("%d\n", spoo[n]);
}

return 0;
}



   /* ----------------------------------------------------------------------------------
      The following is the glorious quicksort algorithm, which takes as arguments a
     pointer to the array of ints to be sorted, and the number of values in the array
   ---------------------------------------------------------------------------------- */

void quicksort (int * startptr, int numberstosort) {

int n;
int * pivotptr;

int localarray[MAX];
int startpile = 0;
int endpile = 0;
int pivotlocation;

if (numberstosort <= 1)
{
   // if (numberstosort == 1)
   // {
   //    printf("%d in place\n---\n", *startptr);
   // }
   return;
}

pivotlocation = (int) (numberstosort / 2);         // location in the array of the pivot ie spoo[4]
pivotptr = startptr + pivotlocation;

for (n = 0; n < numberstosort; n++)
{
   if (n != pivotlocation)
   {
      if (*(startptr + n) < *pivotptr)
      {
         // printf("%d went left\n", *(startptr + n));
         localarray[startpile] = *(startptr + n);
         startpile++;
      } else {
         // printf("%d went right\n", *(startptr + n));
         localarray[(numberstosort - 1) - endpile] = *(startptr + n);
         endpile++;
      }
   }
}

if (startpile < endpile)
{
   // printf("%d (pivot) went left\n", *pivotptr);
   localarray[startpile] = *pivotptr;
   startpile++;
} else {
   // printf("%d (pivot) went right\n", *pivotptr);
   localarray[(numberstosort - 1) - endpile] = *pivotptr;
   endpile++;
}

// printf("---\n");

quicksort(&localarray[0], startpile);
quicksort(&localarray[startpile], numberstosort - startpile);

for (n = 0; n < numberstosort; n++)
{
   *(startptr + n) = localarray[n];
}

return;
}



// Pseudo-random-number generator...

int pseudorand(void) {

static unsigned int next = 1;

next = next * 1103515245 + 12345;
return next % 100;
}

