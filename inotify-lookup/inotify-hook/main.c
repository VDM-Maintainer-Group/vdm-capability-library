/* Inotify WD Reverse Lookup Kernel Module
* References:
* 1. https://elixir.bootlin.com/linux/latest/source/include/linux/radix-tree.h
* 2. https://biscuitos.github.io/blog/IDA_ida_destroy/
* 3. https://lwn.net/Articles/175432/
*/
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/version.h>
#include "main.h"
#include "khook/khook/engine.c"
#include "netlink_comm.h"

/************************* PROTOTYPE DECLARATION *************************/
static struct comm_list_t comm_list;
static struct comm_list_item * comm_list_find(const char *);
static int __init inotify_hook_init(void);
static void __exit inotify_hook_fini(void);

/********************* COMM_RECORD UTILITY FUNCTION **********************/
static int comm_record_insert(struct comm_record_t *record, unsigned long pid, int fd, u32 wd, char * const pname)
{
    int ret;
    struct radix_tree_root *p_fd_wd_rt;

    p_fd_wd_rt = radix_tree_lookup(&record->pid_rt, pid);
    //create pid_rt if not exists
    if (!p_fd_wd_rt)
    {
        TRY_BUF( p_fd_wd_rt, sizeof(struct radix_tree_root) ) {
            INIT_RADIX_TREE(p_fd_wd_rt, GFP_ATOMIC);

            spin_lock(&record->lock);
            ret = radix_tree_insert(&record->pid_rt, pid, p_fd_wd_rt);
            spin_unlock(&record->lock);

            if (unlikely(ret<0))
            {
                printh("[comm_record] `pid_rt` insertion failed for %ld.\n", pid);
                return ret;
            }
        } ELSE_BUF( p_fd_wd_rt, KEEP_BUF ) {            //NOTE: keep `p_fd_wd_rt`
            return -ENOMEM;
        } END_BUF;
    }

    // insert the record
    spin_lock(&record->lock);
    ret = radix_tree_insert(p_fd_wd_rt, fd_wd_to_mark(fd,wd), pname);
    spin_unlock(&record->lock);
    if (unlikely(ret<0))
    {
        printh("[comm_record] `fd_wd_rt` insertion failed for %ld, %d.\n", fd_wd_to_mark(fd,wd), ret);
        return ret;
    } ///else { printh("[comm_record] add %d.\n", fd_wd_to_mark(fd,wd)); }

    return 0;
}

static void comm_record_remove(struct comm_record_t *record, unsigned long pid, int fd, u32 wd)
{
    int mark;
    char *pathname;
    struct radix_tree_root *p_fd_wd_rt;

    p_fd_wd_rt = (struct radix_tree_root *) radix_tree_lookup(&record->pid_rt, pid);
    if (!p_fd_wd_rt)
    {
        goto out;
    }

    mark = fd_wd_to_mark(fd,wd);
    pathname = (char *) radix_tree_lookup(p_fd_wd_rt, mark);
    if (!pathname)
    {
        goto out;
    }

    spin_lock(&record->lock);
    {
        // free record of fd_wd_rt
        kfree(pathname);
        radix_tree_delete(p_fd_wd_rt, mark);
        // free record of pid_rt
        if (radix_tree_empty(p_fd_wd_rt))
        {
            kfree(p_fd_wd_rt);
            radix_tree_delete(&record->pid_rt, pid);
        }
    }
    spin_unlock(&record->lock);

out:
    return;
}

static int comm_record_dump(struct comm_record_t *record, int(*fn)(int pid, char *pathname, void *data), void *data)
{
    int ret = 0;
    struct radix_tree_iter iter0, iter1;
    void **slot0, **slot1;

    spin_lock(&record->lock);
    radix_tree_for_each_slot(slot0, &record->pid_rt, &iter0, 0)
    {
        struct task_struct *_task = pid_task(find_vpid(iter0.index), PIDTYPE_PID);//"find_task_by_vpid" not export
        struct radix_tree_root *p_fd_wd_rt = radix_tree_deref_slot(slot0);
        if (likely(_task))
        {
            radix_tree_for_each_slot(slot1, p_fd_wd_rt, &iter1, 0)
            {
                char *pathname = radix_tree_deref_slot(slot1);
                if ( (ret = fn(iter0.index, pathname, data)) < 0 )
                {
                    // printh("%ld, %s\n", iter0.index, (char *)pathname);
                    goto out;
                }
            }
        } //else remove from pid_rt
    }
out:
    spin_unlock(&record->lock);
    return ret;
}

int comm_record_dump_by_name(const char *name, int(*fn)(int pid, char *pathname, void *data), void *data)
{
    int ret = -1;
    struct comm_list_item *item;

    item = comm_list_find(name);
    if(item)
    {
        ret = comm_record_dump(&item->record, fn, data);
    }

    return ret;
}

static void comm_record_init(struct comm_record_t *record)
{
    spin_lock_init(&record->lock);
    INIT_RADIX_TREE(&record->pid_rt, GFP_ATOMIC);
    return;
}

static void comm_record_cleanup(struct comm_record_t *record)
{
    struct radix_tree_iter iter0, iter1;
	void **slot0, **slot1;

    spin_lock(&record->lock);
    radix_tree_for_each_slot(slot0, &record->pid_rt, &iter0, 0)
    {
        struct radix_tree_root *p_fd_wd_rt = radix_tree_deref_slot(slot0);
        if (!radix_tree_exception(p_fd_wd_rt))
        {
            radix_tree_for_each_slot(slot1, p_fd_wd_rt, &iter1, 0)
            {
                void *pathname = radix_tree_deref_slot(slot1);
                // printh("%ld, %s\n", iter0.index, (char *)pathname);
                if (!radix_tree_exception(pathname)) {kfree(pathname);}
                radix_tree_iter_delete(p_fd_wd_rt, &iter1, slot1);
            }
        }
        radix_tree_iter_delete(&record->pid_rt, &iter0, slot0);
    }
    spin_unlock(&record->lock);
    
    return;
}

/********************** COMM_LIST UTILITY FUNCTION ***********************/
static struct comm_list_item * comm_list_find(const char *name)
{
    struct comm_list_item *item=NULL, *result=NULL;

    spin_lock(&comm_list.lock);
    list_for_each_entry(item, &comm_list.head, node)
    {
        if (strcmp(name, item->comm_name)==0)
        {
            result = item;
            break;
        }
    }
    spin_unlock(&comm_list.lock);

    return result;
}

int comm_list_add_by_name(const char *name)
{
    int ret;
    struct comm_list_item *item;

    // check duplicated allocations
    if (comm_list_find(name))
    {
        return 0;
    }
    
    TRY_BUF( item, sizeof(struct comm_list_item) ) {
        // allocate memory
        TRY_BUF( item->comm_name, strlen(name) ) {
            // initialize the item
            strcpy(item->comm_name, name);
            comm_record_init(&item->record);
            INIT_LIST_HEAD(&item->node);
            
            // add onto comm_list
            spin_lock(&comm_list.lock);
            list_add(&item->node, &comm_list.head);
            spin_unlock(&comm_list.lock);
            printh("comm_list add \"%s\"\n", name);
            ret = 0;
        } ELSE_BUF( item->comm_name, KEEP_BUF ) {       //NOTE: keep `item->comm_name`
            ret = -ENOMEM;
        } END_BUF;
    } ELSE_BUF( item, KEEP_BUF ) {                      //NOTE: keep `item`
        ret = -ENOMEM;
    } END_BUF;

    return ret;
}

static void comm_list_rm(struct comm_list_item *item)
{
    assert_spin_locked(&comm_list.lock);

    comm_record_cleanup(&item->record);
    kfree(item->comm_name);
    list_del(&item->node);
    kfree(item);

    return;
}

void comm_list_rm_by_name(const char *name)
{
    struct comm_list_item *item=NULL, *tmp=NULL;

    spin_lock(&comm_list.lock);
    list_for_each_entry_safe(item, tmp, &comm_list.head, node)
    {
        if (strcmp(name, item->comm_name)==0)
        {
            comm_list_rm(item);
            break;
        }
    }
    spin_unlock(&comm_list.lock);
    printh("comm_list rm \"%s\"\n", name);

    return;
}

static int comm_list_init(void)
{
    int ret = 0;

    spin_lock_init(&comm_list.lock);
    INIT_LIST_HEAD(&comm_list.head);
    
    return ret;
}

static void comm_list_exit(void)
{
    struct comm_list_item *item=NULL, *tmp=NULL;

    spin_lock(&comm_list.lock);
    list_for_each_entry_safe(item, tmp, &comm_list.head, node)
    {
        comm_list_rm(item);
    }
    spin_unlock(&comm_list.lock);

    return;
}

/*************************** INOTIFY SYSCALL HOOK ***************************/
//regs->(di, si, dx, r10), reference: arch/x86/include/asm/syscall_wrapper.h#L125
//SYSCALL_DEFINE3(inotify_add_watch, int, fd, const char __user *, pathname, u32, mask)
KHOOK_EXT(long, ORIGIN(inotify_add_watch), const struct pt_regs *);
static long MODIFY(inotify_add_watch)(const struct pt_regs *regs)
{
    int wd;
    unsigned int flags = 0;
    //
    struct path path;
    char *buf1, *buf2;
    char *proot=NULL, *pname=NULL;
    //
    int buf_len = 0;
    char *precord=NULL;
    struct comm_list_item *item;

    /* call the original function */
    wd = KHOOK_ORIGIN(ORIGIN(inotify_add_watch), regs);

    /* decode the registers */
    int fd = (int) regs->di;
    const char __user *pathname = (char __user *) regs->si;
    u32 mask = (u32) regs->dx;

    /* get and insert the pathname record */
    if (!(mask & IN_DONT_FOLLOW))
        flags |= LOOKUP_FOLLOW;
    if (mask & IN_ONLYDIR)
        flags |= LOOKUP_DIRECTORY;
    
    if ( wd>=0 && (item=comm_list_find(current->comm)) && (user_path_at(AT_FDCWD, pathname, flags, &path)==0) )
    {
        TRY_BUF( buf1, PATH_MAX ) {
            TRY_BUF( buf2, PATH_MAX ) {
                // get pname from `struct path`
                proot = dentry_path_raw(current->fs->root.dentry, buf1, PATH_MAX);
                pname = dentry_path_raw(path.dentry,              buf2, PATH_MAX);
                path_put(&path);
                // insert into comm_record
                TRY_BUF(precord, PATH_MAX)
                    buf_len = strlen(proot) + strlen(pname) + 2; //plus '/' and '\0'.
                    snprintf(precord, buf_len, "%s/%s", proot, pname);
                    comm_record_insert(&item->record, task_pid_nr(current), fd, wd, precord);
                    // printh("%s, PID %d add (%d,%d): %s\n", current->comm, task_pid_nr(current), fd, wd, precord);
                ELSE_BUF(precord, KEEP_BUF) {           //NOTE: keep `precord`
                    wd = -ENOMEM;
                } END_BUF;
            } ELSE_BUF( buf2, FREE_BUF ); END_BUF;
        } ELSE_BUF( buf1, FREE_BUF ); END_BUF;
    }

    return wd;
}

//SYSCALL_DEFINE2(inotify_rm_watch, int, fd, __s32, wd)
KHOOK_EXT(long, ORIGIN(inotify_rm_watch), const struct pt_regs *regs);
static long MODIFY(inotify_rm_watch)(const struct pt_regs *regs)
{
    int ret;
    struct comm_list_item *item;
    // decode the registers
    int fd = (int) regs->di;
    u32 wd = (u32) regs->si;

    // call the original function
    ret = KHOOK_ORIGIN(ORIGIN(inotify_rm_watch), regs);

    if ((item=comm_list_find(current->comm)))
    {
        // remove from comm_record
        comm_record_remove(&item->record, task_pid_nr(current), fd, wd);
        // printh("%s, PID %d remove (%d,%d)\n", current->comm, task_pid_nr(current), fd, wd);
    }

    return ret;
}

/****************************** MAIN_ENTRY ******************************/
static int __init inotify_hook_init(void)
{
    int ret = 0;

    /* init data structure */
    if ( (ret=comm_list_init()) < 0 )
    {
        printh("Data Structure Initialization Failed.\n");
        return ret;
    }
    /* init khook engine */
    if ( (ret = khook_init()) < 0 )
    {
        printh("khook Initialization Failed.\n");
        return ret;
    }
    /* init netlink */
    if ( (ret = netlink_comm_init()) < 0 )
    {
        printh("Netlink Initialization Failed.\n");
        return -EINVAL;
    }
    printh("Inotify hook module init.\n");

    return 0;
}

static void __exit inotify_hook_fini(void)
{
    netlink_comm_exit();
    khook_cleanup();
    comm_list_exit();
    printh("Inotify hook module exit.\n\n");
}

module_init(inotify_hook_init);
module_exit(inotify_hook_fini);
MODULE_LICENSE("GPL");
MODULE_AUTHOR("VDM");
