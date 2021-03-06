#ifndef __INOTIFY_LOOKUP_H__
#define __INOTIFY_LOOKUP_H__

#include <sys/socket.h>
#include <linux/netlink.h>

#define NETLINK_USER 31   // (fixed) netlink specific magic number
#define MAX_NAME_LEN 1024 // (fixed) maximum length of app name
#define PATH_MAX     4096 // (fixed) maximum length of inode pathname
#define MAX_DUMP_LEN 1000 // maximum number of received dump
/* request message operation code */
#define INOTIFY_REQ_ADD  0x01
#define INOTIFY_REQ_RM   0x02
#define INOTIFY_REQ_DUMP 0x04

struct __attribute__((__packed__)) req_msg_t {
    int op;
    char comm_name[MAX_NAME_LEN];
};

// extern int inotify_create_netlink(void);
// extern void inotify_destroy_netlink(void);

extern int inotify_lookup_register(const char *);
extern int inotify_lookup_unregister(const char *);
extern char** inotify_lookup_dump(const char *);
extern void inotify_lookup_freedump(void);

#endif