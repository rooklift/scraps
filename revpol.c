// Revpol - Reverse Polish(ish) Interpreter
// This was written in 2003 when I barely knew how to code

// INCLUDES:

#include <assert.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// DEFINITIONS:

#define MAXSTACK 100          // Size of the stack.
#define CHUNKLENGTH 100       // Maximum length of a chunk (ie operator or operand) in the source.
#define LINEMAX 1000          // Max characters in in a line of the program source.
#define PROGMAX 10000         // Maximum instructions in a program.

#define IS_OPERATOR 1
#define IS_INTEGER 2
#define IS_LABELADDRESS 3
#define IS_VARIABLEADDRESS 4
#define IS_VARIABLECALL 5

// PROTOTYPES:

void execute(void);
void runoperator(int opnumber);

// GLOBALS:

int location = 0;
int programlength = 0;
int stacksize = 0;
int uservariables = 0;
int labels = 0;
FILE *outfile = 0;

// ARRAY TO STORE PROGRAM IN:

int programflags[PROGMAX];
int programints[PROGMAX];

// ARRAY TO STORE VARIABLE NAMES IN:

#define MAXVARIABLES 100
#define MAXVARIABLELENGTH 30

char variablename[MAXVARIABLES][MAXVARIABLELENGTH];
long long variable[MAXVARIABLES];

// ARRAY TO STORE LABEL NAMES IN:

#define MAXLABELS 100
#define MAXLABELLENGTH 30

char labelname[MAXLABELS][MAXLABELLENGTH];
int labelvalue[MAXLABELS];

// STACK:

long long stack[MAXSTACK];

// COMMAND SET:

#define MAXCOMMANDS 39        // Size of command set
#define MAXCOMMANDLENGTH 15   // Max length of command

const char commandset[MAXCOMMANDS][MAXCOMMANDLENGTH] = {

                     // Number:
  "+"                // 0            Addition
, "-"                // 1            Subtraction
, "QUIT"             // 2            Terminate program
, "."                // 3            Print top stack element
, "*"                // 4            Multiplication
, "/"                // 5            Division
, "MOD"              // 6            Modulus (remainder of integer division)
, "DROP"             // 7            Drop top stack element
, "DUP"              // 8            Duplicate top stack element
, "^"                // 9            x y ^ == x to the power of y
, "DROPALL"          // 10           Make stack size = 0
, "STACKSIZE"        // 11           Stack size BEFORE this command was run - same as location of its own output.
, "SQRT"             // 12           Square root
, "OR"               // 13           Logical or
, "AND"              // 14           Logical and
, "XOR"              // 15           Logical xor
, "NOT"              // 16           Logical not (returns 1 if top element == 0, returns 0 otherwise)
, "=="               // 17           Check for equality
, "!="               // 18           Check for inequality
, ">"                // 19           Is greater than
, "<"                // 20           Is less than
, ">="               // 21           Is greater than or equal to
, "<="               // 22           Is less than or equal to
, "JUMP"             // 23           Goto
, "RETURN"           // 24           Goto
, "CALL"             // 25           Goto, leave return address on stack
, "PROGLENGTH"       // 26           Length of program
, "ASSERT"           // 27           Assertion (top stack element != 0, quit if it does)
, "SWAP"             // 28           Swap top 2 stack elements
, "IF"               // 29           Call if
, "IFG"              // 30           Jump if
, "IFE"              // 31           If then else
, "IFEG"             // 32           If then else (without leaving return address)
, "STORE"            // 33           Store in variable
, "RECALL"           // 34           Recall from variable
, "NOOP"             // 35           No operation
, "PEEK"             // 36           Peek at stack location
, "POKE"             // 37           x y POKE means write x to stack location y
, "SAVE"             // 38           Save to "output" file

};

void add(void);
void subtract(void);
void terminate(void);
void printtoscreen(void);
void multiply(void);
void divide(void);
void modulus(void);
void drop(void);
void duplicate(void);
void topowerof(void);
void dropall(void);
void sizeofstack(void);
void squareroot(void);
void logicalor(void);
void logicaland(void);
void logicalxor(void);
void logicalnot(void);
void equalitycheck(void);
void inequalitycheck(void);
void isgreaterthan(void);
void islessthan(void);
void greaterorequal(void);
void lessorequal(void);
void jump(void);
void call(void);
void proglength(void);
void rp_assert(void);
void swaptop(void);
void conditionalcall(void);
void conditionaljump(void);
void fork(void);
void forknoreturn(void);
void store(void);
void recall(void);
void noop(void);
void rp_peek(void);
void rp_poke(void);
void savetofile(void);

/*  ---------------------- main ----------------------------- */

int main (int argc, char *argv[])
{
   FILE *infile;
   char line[LINEMAX];
   char * chunkptr;
   int n;
   int foundcommandflag;
   int foundlabelflag;
   int foundvariableflag;
   int varalreadyknown;
   char * commentptr;
   long startfilepos;
   char * lastcharptr;
   
   const char separators[] = " \t\n\r(){}[]";

   fprintf(stdout, "\nWelcome to Reverse Polish(ish)\n");
   
   if (argc < 2)
   {
      fprintf(stderr, "Need filename. Sample usage: %s file.txt\n", argv[0]);      
      return 1;
   }
   
   if ((infile = fopen(argv[1], "rb")) == NULL)
   {
      fprintf(stderr, "Couldn't open file \"%s\"\n", argv[1]);
      return 2;
   }
   
   startfilepos = ftell(infile);
   
   for (n = 0; n < MAXVARIABLES; n++)
   {
      variable[n] = 0;
   }

   /* --------------- see note below -------------------- */

   while (fgets(line, LINEMAX, infile) != NULL)       // Read in lines from the file.
   {
   
      for (n = 0; n < strlen(line); n++)
      {
         line[n] = toupper(line[n]);                  // Uppercase everything.
      }
   
      commentptr = strstr(line, "//");                // These lines allow "//" to start a comment, which
      if (commentptr != NULL)                         // ends with a newline.
      {
         *commentptr = '\0';
      }
      chunkptr = strtok(line, separators);
      while (chunkptr)
      {
         if(*(chunkptr + strlen(chunkptr) - 1) == ':')           // Checks if last char of chunk is :
         {
            assert(labels < MAXLABELS);
            strcpy(&labelname[labels][0], chunkptr);
            labelname[labels][strlen(&labelname[labels][0]) - 1] = '\0';
            labelvalue[labels] = programlength;
            // fprintf(stdout, "found label \"%s\" with value %d\n", &labelname[labels][0], labelvalue[labels]);
            labels++;
         } else {
            programlength++;
         }
      chunkptr = strtok(NULL, separators);
      }
   }
   
   fseek(infile, startfilepos, SEEK_SET);
   programlength = 0;                           // FIXME: probably shouldn't be using this above.
   
   /* The above lines need to exactly mirror the ones below in terms of programlength and
      comments, etc. The lines above are the checks for existence of labels. */
   
   while (fgets(line, LINEMAX, infile) != NULL)       // Read in lines from the file.
   {
   
      /* -------------- DO SOME BASIC PRE-PARSING ------------------- */
   
      for (n = 0; n < strlen(line); n++)
      {
         line[n] = toupper(line[n]);                  // Uppercase everything.
      }
      
      commentptr = strstr(line, "//");                // These lines allow "//" to start a comment, which
      if (commentptr != NULL)                         // ends with a newline.
      {
         *commentptr = '\0';
      }
      
      chunkptr = strtok(line, separators);
      while (chunkptr)
      {
         assert(programlength <= PROGMAX);

         foundcommandflag = 0; foundlabelflag = 0; foundvariableflag = 0;
         
         if (*(chunkptr + strlen(chunkptr) - 1) != ':')        // Skip label declarations, done those above...
         {
         
            for (n = 0; n < MAXCOMMANDS; n++)
            {
               if (strcmp(chunkptr, &commandset[n][0]) == 0)      // If chunk is a command...
               {
                  programints[programlength] = n;
                  programflags[programlength] = IS_OPERATOR;
                  programlength++;
                  foundcommandflag = 1;
               }
            }

            if (foundcommandflag == 0)  
            {
               for (n = 0; n < labels; n++)
               {
                  if (strcmp(chunkptr, &labelname[n][0]) == 0)       // If label found...
                  {
                     programints[programlength] = labelvalue[n];
                     programflags[programlength] = IS_LABELADDRESS;
                     foundlabelflag = 1;
                     programlength++;
                     break;
                  }
               }
            }
            
            if (foundcommandflag == 0 && foundlabelflag == 0)
            {
               if (atoi(chunkptr) == 0 && *chunkptr != '0')            // Then it's a variable...
               {
                  foundvariableflag = 1;
                  
                  if(*(chunkptr + strlen(chunkptr) - 1) == '\'')       // Checks if last char of chunk is '
                  {
                  
                     lastcharptr = chunkptr + strlen(chunkptr) - 1;    // Remove trailing '
                     *lastcharptr = '\0';
                     
                     varalreadyknown = 0;
                     for (n = 0; n < uservariables; n++)
                     {
                        if (strcmp(chunkptr, &variablename[n][0]) == 0)
                        {
                           varalreadyknown = 1;
                           programints[programlength] = n;
                           programflags[programlength] = IS_VARIABLEADDRESS;
                           programlength++;
                           break;
                        }
                     }
                     if (varalreadyknown == 0)
                     {
                        assert(uservariables < MAXVARIABLES);
                        strcpy(&variablename[uservariables][0], chunkptr);
                        fprintf(stdout, "New var, no. %d: %s\n", uservariables, &variablename[uservariables][0]);
                        programints[programlength] = uservariables;
                        uservariables++;
                        programflags[programlength] = IS_VARIABLEADDRESS;
                        programlength++;
                     }
                  } else {                       // What to do if variable with no trailing '
                     varalreadyknown = 0;
                     for (n = 0; n < uservariables; n++)
                     {
                        if (strcmp(chunkptr, &variablename[n][0]) == 0)
                        {
                           varalreadyknown = 1;
                           programints[programlength] = n;
                           programflags[programlength] = IS_VARIABLECALL;
                           programlength++;
                           break;
                        }
                     }
                     if (varalreadyknown == 0)
                     {
                        assert(uservariables < MAXVARIABLES);
                        strcpy(&variablename[uservariables][0], chunkptr);
                        fprintf(stdout, "New var, no. %d: %s\n", uservariables, &variablename[uservariables][0]);
                        programints[programlength] = uservariables;
                        uservariables++;
                        programflags[programlength] = IS_VARIABLECALL;
                        programlength++;
                     }
                  }
               }
            }
            
            if (foundcommandflag == 0 && foundlabelflag == 0 && foundvariableflag == 0)     
            {       // Not a command, not a label, not a variable. It's a value for the stack...
               programints[programlength] = atoi(chunkptr);
               programflags[programlength] = IS_INTEGER;
               programlength++;
            }
         }
         chunkptr = strtok(NULL, separators);
      }
   }
   fprintf(stdout, "Running file \"%s\" - %d chunks long\nOutput:\n", argv[1], programlength);
   execute();

return 0;
}

/* --------------------------- execute -------------------- */

void execute(void)
{
   while (location < programlength)
   {

      switch(programflags[location])
      {
         case IS_OPERATOR:      runoperator(programints[location]);
                                break;
         case IS_VARIABLECALL : assert(stacksize < MAXSTACK);
                                stack[stacksize] = variable[programints[location]];
                                stacksize++;
                                break;
         default:               assert(stacksize < MAXSTACK);
                                stack[stacksize] = programints[location];
                                stacksize++;
                                break;
      }
   
   location++;
   }

fprintf(stdout, "Terminating, due to end of source file.\n");
exit(0);
}

/* --------------------------- runoperator -------------------- */

void runoperator(int opnumber)
{
   switch (opnumber)
   {
      case 0  : add();
                break;
      case 1  : subtract();
                break;
      case 2  : terminate();
                break;
      case 3  : printtoscreen();
                break;
      case 4  : multiply();
                break;
      case 5  : divide();
                break;
      case 6  : modulus();
                break;
      case 7  : drop();
                break;
      case 8  : duplicate();
                break;
      case 9  : topowerof();
                break;
      case 10 : dropall();
                break;
      case 11 : sizeofstack();
                break;
      case 12 : squareroot();
                break;
      case 13 : logicalor();
                break;
      case 14 : logicaland();
                break;
      case 15 : logicalxor();
                break;
      case 16 : logicalnot();
                break;
      case 17 : equalitycheck();
                break;
      case 18 : inequalitycheck();
                break;
      case 19 : isgreaterthan();
                break;
      case 20 : islessthan();
                break;
      case 21 : greaterorequal();
                break;
      case 22 : lessorequal();
                break;
      case 23 : jump();
                break;
      case 24 : jump();
                break;
      case 25 : call();
                break;
      case 26 : proglength();
                break;
      case 27 : rp_assert();
                break;
      case 28 : swaptop();
                break;
      case 29 : conditionalcall();
                break;
      case 30 : conditionaljump();
                break;
      case 31 : fork();
                break;
      case 32 : forknoreturn();
                break;
      case 33 : store();
                break;
      case 34 : recall();
                break;
      case 35 : noop();
                break;
      case 36 : rp_peek();
                break;
      case 37 : rp_poke();
                break;
      case 38 : savetofile();
                break;
   }
return;
}

/* --------------------------- assorted operator functions -------------------- */

void add(void)
{
   assert(stacksize >= 2);
   stack[stacksize - 2] += stack[stacksize - 1];
   stacksize--;
   return;
}

void subtract(void)
{
   assert(stacksize >= 2);
   stack[stacksize - 2] -= stack[stacksize - 1];
   stacksize--;
   return;
}

void terminate(void)
{
   fprintf(stdout, "Terminating, due to QUIT command.\n");
   exit(0);
}

void printtoscreen(void)
{
   assert(stacksize >= 1);
   fprintf(stdout, " %I64d\n", stack[stacksize - 1]);
   stacksize--;
   return;
}

void multiply(void)
{
   assert(stacksize >= 2);
   stack[stacksize - 2] *= stack[stacksize - 1];
   stacksize--;
   return;
}

void divide(void)
{
   assert(stacksize >= 2);
   assert(stack[stacksize - 1] != 0);                          // Divide by zero error.
   stack[stacksize - 2] /= stack[stacksize - 1];
   stacksize--;
   return;
}

void modulus(void)
{
   assert(stacksize >= 2);
   stack[stacksize - 2] %= stack[stacksize - 1];
   stacksize--;
   return;
}

void drop(void)
{
   assert(stacksize >= 1);
   stacksize--;
   return;
}

void duplicate(void)
{
   assert(stacksize < MAXSTACK);
   assert(stacksize >= 1);
   stack[stacksize] = stack[stacksize - 1];
   stacksize++;
   return;
}

void topowerof(void)
{
   long long result;
   long long initialvalue;
   long long n;
   
   assert(stacksize >= 2);
   
   if (stack[stacksize - 1] == 0)
   {
      assert(stack[stacksize - 2] != 0);    // FIXME: Is this right? Will abort if trying 0 to the power of 0.
      result = 1;
   } else {
      result = stack[stacksize - 2];
      initialvalue = result;
      for (n = 1; n < stack[stacksize - 1]; n++)
      {
         result *= initialvalue;
      }
   }
   stacksize--;
   stack[stacksize - 1] = result;
   return;
}

void dropall(void)
{
   stacksize = 0;
   return;
}

void sizeofstack(void)                     // Returns stacksize NOT including self!
{
   assert(stacksize < MAXSTACK);
   stack[stacksize] = stacksize;
   stacksize++;
   return;
}

void squareroot(void)
{
   long long result;
   
   assert(stacksize >= 1);
   assert(stack[stacksize - 1] >= 0);        // No imaginary numbers.
   result = (long long int) sqrt(stack[stacksize - 1]);
   stack[stacksize - 1] = result;
   return;
}

void logicalor(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] || stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void logicaland(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] && stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void logicalxor(void)
{
   assert(stacksize >= 2);
   if ((stack[stacksize - 2] == 0 && stack[stacksize - 1]) || (stack[stacksize - 1] == 0 && stack[stacksize - 2]))
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void logicalnot(void)
{
   assert(stacksize >= 1);
   if (stack[stacksize - 1])
   {
      stack[stacksize - 1] = 0;
   } else {
      stack[stacksize - 1] = 1;
   }
}

void equalitycheck(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] == stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void inequalitycheck(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] != stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void isgreaterthan(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] > stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void islessthan(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] < stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void greaterorequal(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] >= stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void lessorequal(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2] <= stack[stacksize - 1])
   {
      stack[stacksize - 2] = 1;
   } else {
      stack[stacksize - 2] = 0;
   }
   stacksize--;
   return;
}

void jump(void)
{
   assert(stacksize >= 1);
   assert(stack[stacksize - 1] >= 0);
   assert(stack[stacksize - 1] < programlength);
   location = stack[stacksize - 1] - 1;     // Subtract 1 because location will
   stacksize--;                             // be iterated in the main loop...
   return;
}

void call(void)
{
   long long returnaddress;
   
   returnaddress = location + 1;            // Return to the NEXT instruction
   assert(stacksize >= 1);
   assert(stack[stacksize - 1] >= 0);
   assert(stack[stacksize - 1] < programlength);
   location = stack[stacksize - 1] - 1;     // Subtract 1 because location will
   stack[stacksize - 1] = returnaddress;    // be iterated in the main loop...
   return;
}

void proglength(void)
{
   assert(stacksize < MAXSTACK);
   stack[stacksize] = programlength;
   stacksize++;
   return;
}

void rp_assert(void)
{
   assert(stacksize >= 1);
   if (stack[stacksize - 1] == 0)
   {
      fprintf(stdout, "Terminating, due to assertion failure at location %d.\n", location);
      exit(0);
   }
   stacksize--;
   return;
}

void swaptop(void)
{
   long long temp;

   assert(stacksize >= 2);
   temp = stack[stacksize - 2];
   stack[stacksize - 2] = stack[stacksize - 1];
   stack[stacksize - 1] = temp;
   return;
}

void conditionalcall(void)
{
   long long returnaddress;
   
   assert(stacksize >= 2);
   if (stack[stacksize - 2])
   {
      returnaddress = location + 1;            // Return to the NEXT instruction
      assert(stack[stacksize - 1] >= 0);
      assert(stack[stacksize - 1] < programlength);
      location = stack[stacksize - 1] - 1;
      stacksize--;                              // Yes, this is the right order:
      stack[stacksize - 1] = returnaddress;     // knock top off, replace one below it.
   } else {
      stacksize--; stacksize--;                 // No call, so no return address, so knock 2 off.
   }
   return;
}

void conditionaljump(void)
{
   assert(stacksize >= 2);
   if (stack[stacksize - 2])
   {
      assert(stack[stacksize - 1] >= 0);
      assert(stack[stacksize - 1] < programlength);
      location = stack[stacksize - 1] - 1;
   }
   stacksize--; stacksize--;
   return;
}

void fork(void)
{
   long long returnaddress;

   assert(stacksize >= 3);
   returnaddress = location + 1;
   if (stack[stacksize - 3])
   {
      assert(stack[stacksize - 2] >= 0);
      assert(stack[stacksize - 2] < programlength);
      location = stack[stacksize - 2] - 1;
   } else {
      assert(stack[stacksize - 1] >= 0);
      assert(stack[stacksize - 1] < programlength);
      location = stack[stacksize - 1] - 1;
   }
   stacksize--; stacksize--;
   stack[stacksize - 1] = returnaddress;
   return;
}

void forknoreturn(void)
{
   assert(stacksize >= 3);
   if (stack[stacksize - 3])
   {
      assert(stack[stacksize - 2] >= 0);
      assert(stack[stacksize - 2] < programlength);
      location = stack[stacksize - 2] - 1;
   } else {
      assert(stack[stacksize - 1] >= 0);
      assert(stack[stacksize - 1] < programlength);
      location = stack[stacksize - 1] - 1;
   }
   stacksize--; stacksize--; stacksize--;
   return;
}

void store(void)
{
   assert(stacksize >= 2);
   assert(stack[stacksize - 1] >= 0);
   assert(stack[stacksize - 1] < MAXVARIABLES);
   variable[stack[stacksize - 1]] = stack[stacksize - 2];
   stacksize--; stacksize--;
   return;
}

void recall(void)
{
   long long varnum;
   
   assert(stacksize >= 1);
   assert(stack[stacksize - 1] >= 0);
   assert(stack[stacksize - 1] < MAXVARIABLES);
   varnum = stack[stacksize - 1];
   stack[stacksize - 1] = variable[varnum];
   return;
}

void noop(void)
{
   return;
}

void rp_peek(void)
{
   assert(stacksize >= 1);
   assert(stack[stacksize - 1] >= 0);
   assert(stack[stacksize - 1] < stacksize);
   stack[stacksize - 1] = stack[stack[stacksize - 1]];
   return;
}

void rp_poke(void)
{
   long long valuetopoke;
   long long locationtopoke;
   
   assert(stacksize >= 2);
   
   valuetopoke = stack[stacksize - 2];
   locationtopoke = stack[stacksize - 1];
   
   assert(locationtopoke >= 0);
   assert(locationtopoke < stacksize - 2);       // No poking to the 2 operands of this command.
   
   stack[locationtopoke] = valuetopoke;
   stacksize--; stacksize--;
   return;
}

void savetofile(void)
{
   assert (stacksize >= 1);
   if (outfile == 0)                             // ie if never been opened.
   {
      outfile = fopen("rvp output", "w");
      assert (outfile != NULL);
      fprintf(stdout, "Output file has been created.\n");
   }
   fprintf(outfile, " %I64d\n", stack[stacksize - 1]);
   stacksize--;
   return;
}
