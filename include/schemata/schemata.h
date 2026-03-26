#ifndef SCHEMATA_H
#define SCHEMATA_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Look up a schema by export name (e.g. "kind1Schema").
 * Returns the JSON string, or NULL if not found.
 * The returned pointer is to static data and must NOT be freed.
 */
const char *schemata_get(const char *key);

/**
 * Return an array of all schema keys, sorted alphabetically.
 * Sets *count to the number of keys.
 * The returned pointer is to static data and must NOT be freed.
 */
const char *const *schemata_keys(size_t *count);

/**
 * Return the total number of embedded schemas.
 */
size_t schemata_count(void);

#ifdef __cplusplus
}
#endif

#endif /* SCHEMATA_H */
