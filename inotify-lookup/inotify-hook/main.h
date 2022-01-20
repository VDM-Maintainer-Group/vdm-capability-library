#ifndef __HOOK_MAIN_H__
#define __HOOK_MAIN_H__

#include <linux/sched.h>
#include <linux/pid.h> //for pid_type
#include <linux/uaccess.h>
#include <linux/kallsyms.h>
#include <linux/syscalls.h>
#include <linux/namei.h>
#include <linux/string.h>
#include <linux/types.h>
#include <linux/fs_struct.h>
//headers for utility functions
#include <linux/list.h>
#include <linux/radix-tree.h>
#include <linux/spinlock.h>

#define IN_ONLYDIR		    0x01000000	/* only watch the path if it is a directory */
#define IN_DONT_FOLLOW		0x02000000	/* don't follow a sym link */
#define KERN_LOG KERN_NOTICE "inotify_hook: "
#define printh(...) printk(KERN_LOG __VA_ARGS__)

#ifdef CONFIG_X86_64
#define ORIGIN(FUNC) __x64_sys_##FUNC
#define MODIFY(FUNC) khook___x64_sys_##FUNC
#else
#error Target CPU architecture is NOT supported !!!
#endif

#define MAX_NUM_WATCH 1000

#define FREE_BUF 0x1
#define KEEP_BUF 0x0
#define TRY_BUF(var, size)   var=kmalloc(size, GFP_KERNEL); if (likely(var)) {
#define ELSE_BUF(var, end)   if (end) kfree(var); } else {
#define END_BUF              }

struct comm_list_t
{
    u32 counter; //not used for now
    spinlock_t lock;
    struct list_head head;
};

struct comm_record_t
{
    spinlock_t lock;
    struct radix_tree_root pid_rt; //pid->(wd+fd*MAX_NUM_WATCH)->pathname
};

struct comm_list_item
{
    char *comm_name;
    struct comm_record_t record;
    struct list_head node;
};

static inline unsigned long fd_wd_to_mark(u32 fd, u32 wd)
{
    return wd*MAX_NUM_WATCH+fd;
}

extern int comm_list_add_by_name(const char *);
extern void comm_list_rm_by_name(const char *);
extern int comm_record_dump_by_name(const char *, int(*fn)(int pid, char *pathname, void *data), void *data);

#endif