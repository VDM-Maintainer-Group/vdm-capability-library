#ifndef __NETLINK_COMM_H__
#define __NETLINK_COMM_H__

#include <linux/string.h>
#include <linux/socket.h>
#include <net/sock.h>
#include <linux/net.h>
#include <linux/netlink.h>
#include <linux/skbuff.h>
#include "main.h"

#define NETLINK_USER 31
#define MAX_NAME_LEN 1024
#define INOTIFY_REQ_ADD  0x01
#define INOTIFY_REQ_RM   0x02
#define INOTIFY_REQ_DUMP 0x04

struct __attribute__((__packed__)) req_msg_t {
    int op;
    char comm_name[MAX_NAME_LEN];
};

struct msg_buf_t {
    struct sk_buff *skb;
    int usr_pid;
    int seq;
};

int netlink_comm_init(void);
void netlink_comm_exit(void);

#endif