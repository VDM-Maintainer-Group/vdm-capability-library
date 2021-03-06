#include <stdio.h>
#include <unistd.h>
#include "inotify_lookup.h"
// #include <vdm/capability/inotify_lookup.h>

int main(int argc, char const *argv[])
{
    int ret, pos;
    char **result;

    ret = inotify_lookup_register("code");
    printf("add with ret code: %d.\n", ret);

    result = inotify_lookup_dump("code");
    while (pos<MAX_DUMP_LEN && result[pos])
    {
        printf("dump [%d]: %s\n", pos, result[pos]);
        pos ++;
    }

    inotify_lookup_freedump();

    // ret = inotify_lookup_unregister("code");
    // printf("rm with ret code: %d.\n", ret);

    return 0;
}
