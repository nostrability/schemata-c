#include "schemata/schemata.h"
#include "schemata/schemas_data.h"
#include <string.h>

/* Binary search for a key in the sorted schemata_entries array. */
const char *schemata_get(const char *key)
{
    if (!key)
        return NULL;

    int lo = 0;
    int hi = SCHEMATA_COUNT - 1;

    while (lo <= hi) {
        int mid = lo + (hi - lo) / 2;
        int cmp = strcmp(key, schemata_entries[mid].key);
        if (cmp == 0)
            return schemata_entries[mid].json;
        else if (cmp < 0)
            hi = mid - 1;
        else
            lo = mid + 1;
    }

    return NULL;
}

/* Static array of key pointers, built on first call. */
static const char *key_ptrs[SCHEMATA_COUNT];
static int keys_initialized = 0;

const char *const *schemata_keys(size_t *count)
{
    if (!keys_initialized) {
        for (int i = 0; i < SCHEMATA_COUNT; i++) {
            key_ptrs[i] = schemata_entries[i].key;
        }
        keys_initialized = 1;
    }

    if (count)
        *count = SCHEMATA_COUNT;

    return key_ptrs;
}

size_t schemata_count(void)
{
    return SCHEMATA_COUNT;
}
