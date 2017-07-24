#include <stdlib.h>

typedef struct ByteSliceStruct {
	unsigned char * Bytes;
	int				Length;
	int				Capacity;
} BYTESLICE;

BYTESLICE * NewByteSlice(int capacity) {

	BYTESLICE * ret;

	assert(capacity > 0);

	ret = malloc(sizeof BYTESLICE);
	assert(ret != NULL);

	ret->Bytes = malloc(capacity);
	assert(ret->Bytes != NULL);

	ret->Length = 0;
	ret->Capacity = capacity;

	return ret;
}

void AppendByte(BYTESLICE * slice, unsigned char byte) {

	assert(slice != NULL);
	assert(slice->Bytes != NULL);

	if (slice->Length == slice->Capacity) {
		slice->Capacity *= 2;
		slice->Bytes = realloc(slice->Bytes, slice->Capacity);
		assert(slice->Bytes != NULL);
	}

	slice->Bytes[slice->Length] = byte;
	slice->Length += 1;
}
