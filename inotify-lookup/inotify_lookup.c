#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "inotify_lookup.h"

/**
References:
    1. https://github.com/est/pymnl/blob/master/pymnl/nlsocket.py
    2. https://stackoverflow.com/questions/3299386/how-to-use-netlink-socket-to-communicate-with-a-kernel-module
    3. https://stackoverflow.com/questions/62526613/how-to-send-multipart-messages-using-libnl-and-generic-netlink
**/

/* global variables declaration */
int sock_fd = 0;
struct sockaddr_nl src_addr, dest_addr;
struct iovec iov;
struct msghdr msg;
char **dump_result = NULL;

static int init_socket(void)
{
    int msg_size = sizeof(struct req_msg_t);
    struct nlmsghdr *nlh = NULL;

    // reuse existing fd
    if (sock_fd > 0)
    {
        goto out;
    }
    // create socket fd
    sock_fd = socket(PF_NETLINK, SOCK_RAW, NETLINK_USER);
    if (sock_fd < 0)
    {
        goto out;
    }
    // bind to current pid
    memset(&src_addr, 0, sizeof(src_addr));
    src_addr.nl_family = AF_NETLINK;
    src_addr.nl_pid = getpid();
    bind(sock_fd, (struct sockaddr *)&src_addr, sizeof(src_addr));
    // init dest_addr
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.nl_family = AF_NETLINK;
    dest_addr.nl_pid = 0; //pid==0, to kernel
    dest_addr.nl_groups = 0; //unicast
    // init nlmsg struct for "nlh"
    nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(msg_size));
    memset(nlh, 0, NLMSG_SPACE(msg_size));
    nlh->nlmsg_len = NLMSG_SPACE(msg_size);
    nlh->nlmsg_pid = getpid();
    nlh->nlmsg_flags = 0;
    // init nlmsg struct for "msghdr"
    iov.iov_base = (void *)nlh;
    iov.iov_len = nlh->nlmsg_len;
    msg.msg_name = (void *)&dest_addr;
    msg.msg_namelen = sizeof(dest_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;

out:
    return sock_fd;
}

static void fini_socket(void)
{
    if (sock_fd > 0)
    {
        close(sock_fd);
    }
    sock_fd = 0;
}

static int send_request(struct req_msg_t *p_req_msg)
{
    int ret;
    memcpy(NLMSG_DATA(iov.iov_base), p_req_msg, sizeof(struct req_msg_t));
    ret = sendmsg(sock_fd, &msg, 0);
    return ret;
}

static int recv_message(struct msghdr *p_res_msg)
{
    int ret = 0;
    struct nlmsghdr *nlh;

    if ((ret=recvmsg(sock_fd, p_res_msg, 0)) < 0)
    {
        goto out;
    }

    nlh = (struct nlmsghdr *) p_res_msg->msg_iov->iov_base;
    // printf("done: %d, multi: %d, data:%s\n", nlh->nlmsg_type&NLMSG_DONE, nlh->nlmsg_flags&NLM_F_MULTI, NLMSG_DATA(nlh));

    if (!(nlh->nlmsg_type&NLMSG_DONE) && (nlh->nlmsg_flags&NLM_F_MULTI))
    {
        ret = 1; //fragmented message
    }
    else
    {
        ret = 0; //done
    }

out:
    return ret;
}

int inotify_lookup_register(const char *name)
{
    int ret = 0;
    struct req_msg_t req_msg = {
        .op        = INOTIFY_REQ_ADD
    };
    strcpy(req_msg.comm_name, name);

    if ((ret=init_socket()) <= 0)
    {
        goto out;
    }

    if((ret=send_request(&req_msg)) < 0)
    {
        goto out;
    }

out:
    fini_socket();
    return ret;
}

int inotify_lookup_unregister(const char *name)
{
    int ret = 0;
    struct req_msg_t req_msg = {
        .op        = INOTIFY_REQ_RM
    };
    strcpy(req_msg.comm_name, name);

    if ((ret=init_socket()) <= 0)
    {
        goto out;
    }

    if((ret=send_request(&req_msg)) < 0)
    {
        goto out;
    }

out:
    fini_socket();
    return ret;
}

char** inotify_lookup_dump(const char *name)
{
    int ret=0, pos=0;
    struct msghdr res_msg;
    struct iovec res_iov;
    struct nlmsghdr *nlh;
    struct req_msg_t req_msg = {
        .op        = INOTIFY_REQ_DUMP
    };
    strcpy(req_msg.comm_name, name);

    if ((ret=init_socket()) <= 0)
    {
        goto out;
    }

    if((ret=send_request(&req_msg)) < 0)
    {
        goto out;
    }

    // allocate result buffer
    dump_result = malloc(MAX_DUMP_LEN * sizeof(char *));
    // init nlmsg struct for "nlh"
    nlh = (struct nlmsghdr *) malloc(NLMSG_SPACE(PATH_MAX));
    memset(nlh, 0, NLMSG_SPACE(PATH_MAX));
    nlh->nlmsg_len = NLMSG_SPACE(PATH_MAX);
    // init nlmsg struct for "msghdr"
    res_iov.iov_base = (void *)nlh;
    res_iov.iov_len  = nlh->nlmsg_len;
    res_msg.msg_iov = &res_iov;
    res_msg.msg_iovlen = 1;

    // multipart message
    while (pos<MAX_DUMP_LEN && recv_message(&res_msg))
    {
        dump_result[pos] = malloc(strlen(NLMSG_DATA(nlh)));
        strcpy(dump_result[pos], NLMSG_DATA(nlh));
        pos ++;

        memset(nlh, 0, NLMSG_SPACE(PATH_MAX));
    }

out:
    fini_socket();
    free(nlh);
    return dump_result;
}

void inotify_lookup_freedump(void)
{
    free(dump_result);
}