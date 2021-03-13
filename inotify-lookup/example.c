#include <stdio.h>
#include <unistd.h>
#include "inotify_lookup.h"
// #include <vdm/capability/inotify_lookup.h>

int main(int argc, char const *argv[])
{
    int ret, i, length;
    char result[4096];

    ret = inotify_lookup_register("code");
    printf("add with ret code: %d.\n", ret);

    length = inotify_lookup_fetch("code");
    for (i=0; i < length; i++)
    {
        inotify_lookup_get(i, result);
        printf("dump [%d]: %s\n", i, result);
    }
    inotify_lookup_free();

    // ret = inotify_lookup_unregister("code");
    // printf("rm with ret code: %d.\n", ret);

    return 0;
}
