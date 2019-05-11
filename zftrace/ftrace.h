#ifndef __FTRACE_H__
#define __FTRACE_H__

#include <sys/types.h>

#ifndef MAX_S_ENV
# define MAX_S_ENV	32
#endif


/* Modes definition */
#define FTRACE_MODE_OPEN 0
#define FTRACE_MODE_CREATE 1

/* Modes definition */
#define FTRACE_TRIGGER_CHANGES_FOUND 0
#define FTRACE_TRIGGER_NO_CHANGES_FOUND 1
#define FTRACE_TRIGGER_ERROR 2

extern int ftrace_module_init(char**, char*, char*, bool, bool, bool, bool);
extern void ftrace_module_destroy();
extern int ftrace_dump_result_to_file(char*, char*);
extern int ftrace_handle_opened_file(char*, int);
extern int ftrace_update_ignore_list(char* );
extern int ftrace_check_for_changes(char* , bool);
extern int ftrace_is_open_flag(mode_t,int);
extern void ftrace_extract_and_save_path(struct tcb *, long, int);

#endif
