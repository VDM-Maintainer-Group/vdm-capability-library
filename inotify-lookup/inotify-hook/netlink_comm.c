/* Netlink Socket Communication Utility
* References:
* 1. https://stackoverflow.com/questions/3299386/how-to-use-netlink-socket-to-communicate-with-a-kernel-module
* 2. https://elixir.bootlin.com/linux/latest/source/crypto/crypto_user_base.c#L224
* 3. https://elixir.bootlin.com/linux/latest/source/lib/idr.c#L195
*/
#include "netlink_comm.h"

struct sock *nl_sock;

int append_message_cb(int pid, char *pathname, void *data)
{
    int ret = 0;
    char *buf;
    struct nlmsghdr *nlh;
    struct msg_buf_t *msg_buf = data;

    //init skb
    msg_buf->skb = nlmsg_new(NLMSG_DEFAULT_SIZE, 0);
    if (unlikely(!msg_buf->skb)) {
        printh("append_message_cb: skb allocation failed.\n");
        goto out;
    }
    NETLINK_CB(msg_buf->skb).dst_group = 0; /* not in mcast group */

    // allocate buffer in skb
    TRY_BUF( buf, PATH_MAX ) {
        sprintf(buf, "%d,%s", pid, pathname);
        nlh = nlmsg_put(msg_buf->skb, 0, msg_buf->seq, NLMSG_MIN_TYPE, strlen(buf), NLM_F_MULTI);
        if (unlikely(!nlh)) {
            ret = -EMSGSIZE;
        } else {
            strncpy(nlmsg_data(nlh), buf, strlen(buf));
        }
    } ELSE_BUF( buf, FREE_BUF ) {
        ret = -ENOMEM;
    } END_BUF;
    if (ret<0) goto out;

    //finalize current nlh and unicast
    nlmsg_end(msg_buf->skb, nlh);
    msg_buf->seq ++;
    if ( (ret=nlmsg_unicast(nl_sock, msg_buf->skb, msg_buf->usr_pid)) < 0 )
    {
        // printh("rmem_alloc: %d, rcvbuf: %d\n", atomic_read(&sk->sk_rmem_alloc), sk->sk_rcvbuf);
        printh("append_message_cb: message response to %d failed: %d.\n", msg_buf->usr_pid, ret);
        goto out;
    }
    else {
        sock_rfree( msg_buf->skb ); //FIXME: dirty hack
    }
out:
    return ret;
}

static void nl_recv_msg(struct sk_buff *skb)
{
    int ret = 0;
    struct nlmsghdr *nlh;
    struct req_msg_t *req_msg;  //req msg
    struct msg_buf_t msg_buf;   //res msg

    // decode req_msg from sk_buff
    nlh = (struct nlmsghdr *)skb->data;
    msg_buf.usr_pid = nlh->nlmsg_pid;
    req_msg = (struct req_msg_t *)nlmsg_data(nlh);
    // printh("req_msg: %d, %s.\n", req_msg->op, req_msg->comm_name);

    switch (req_msg->op)
    {
        case INOTIFY_REQ_ADD:
            comm_list_add_by_name(req_msg->comm_name);
            break;
        case INOTIFY_REQ_RM:
            comm_list_rm_by_name(req_msg->comm_name);
            break;
        case INOTIFY_REQ_DUMP:
            // dump record
            comm_record_dump_by_name(req_msg->comm_name, append_message_cb, (void *) &msg_buf);
            // finalize the dump
            msg_buf.skb = nlmsg_new(NLMSG_DEFAULT_SIZE, 0);
            if (unlikely(!msg_buf.skb)) {
                printh("nl_recv_msg: skb allocation failed.\n");
                return;
            }
            NETLINK_CB(msg_buf.skb).dst_group = 0; /* not in mcast group */
            nlh = nlmsg_put(msg_buf.skb, 0, msg_buf.seq, NLMSG_DONE, strlen("done"), NLM_F_MULTI);
            if (unlikely(!nlh))
            {
                // ret = -EMSGSIZE;
                return;
            }
            strncpy(nlmsg_data(nlh), "done", strlen("done"));
            nlmsg_end(msg_buf.skb, nlh);
            // unicast the response
            if ( (ret=nlmsg_unicast(nl_sock, msg_buf.skb, msg_buf.usr_pid)) < 0 )
            {
                printh("nl_recv_msg: message response to %d failed: %d.\n", msg_buf.usr_pid, ret);
            }
            break;
        default:
            printh("nl_recv_msg: bad request.\n");
            break;
    }
}

int netlink_comm_init(void)
{
    struct netlink_kernel_cfg cfg = {
        .input = nl_recv_msg,
    };
    //register netlink socket
    nl_sock = netlink_kernel_create(&init_net, NETLINK_USER, &cfg);
    if (!nl_sock) {
        return -1;
    }
    return 0;
}

void netlink_comm_exit(void)
{
    netlink_kernel_release(nl_sock);
}