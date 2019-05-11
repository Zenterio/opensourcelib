#include "defs.h"
#include "ftrace.h"
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/stat.h>
#include <mhash.h>
#include <regex.h>
#include <glib.h>

/* --- defines --- */

#define REGEX_MAX 1000
#define REGEX_MATCH 0
#define REGEX_NOMATCH -1
#define REGEX_ERROR 1

/* --- Types --- */

struct {
    char *cmdline;
    int pid;
} typedef ProcInfo;

/* --- Module internal function declarations --- */
static int init_tree_structures();
static ProcInfo* create_procinfo(int);
static int normalize_path(char *, char *);
static void destroy_key(gpointer);
static void destroy_value(gpointer);
static int should_file_be_processed(char *);
static int calculate_md5(unsigned char *, const char *);
static int replace_env_variables(char *, char *);
static int compile_and_store_regex(const char *, regex_t *);
static int load_regex_rules(char *, regex_t **);
static void free_regex_rules(regex_t **);
static gboolean write_file_entry(gpointer, gpointer, gpointer);
static gboolean write_ignore_file_entry(gpointer, gpointer, gpointer);
static inline int regex_match(const char * const, regex_t **);
static inline void write_checksum(FILE *, char *);
static inline void write_procinfo(FILE *, ProcInfo *);
static inline void write_filepath(FILE *, char *);
static inline int dump_tree_to_file(GTree *, char *, GTraverseFunc);
static inline FILE* open_file(char *);
static inline int close_file(FILE*, char*);

/* --- Module global variables --- */

/* This is the last created file (it probably didn't exist before the call to create) */
static char *last_created_g;

/* The value stored in all tree-nodes so that the lookup function don't return NULL */
static const int tree_dummy_value_g = 42;

/* The two trees (ignore tree is used because regexp is many times slower) */
static GTree *tracked_file_entries_tree_g;
static GTree *ignore_files_tree_g;

static bool report_checksum_g;
static bool report_procinfo_g;
static bool list_tracked_ignored_g;
static bool exclude_tracked_ignored_in_report_g;
static char **substitute_environment_variables_g;

/* Used for storing pre-compiled regex exclusion patterns */
static regex_t *exclude_patterns_compiled_regex_g[REGEX_MAX];

/* Used for storing pre-compiled regex kill patterns */
static regex_t *kill_patterns_compiled_regex_g[REGEX_MAX];

/* --- Function definitions --- */

static ProcInfo* create_procinfo(int pid) {
    ProcInfo *pi = calloc(1, sizeof(ProcInfo));
    if (pi != NULL) {
        char path[25];
        char buffer[PATH_MAX+1];
        sprintf(path, "/proc/%d/cmdline", pid);
        FILE *fp = fopen(path, "r");
        if (fp != NULL) {
            size_t len = fread(buffer, sizeof(char), PATH_MAX, fp);
            if (ferror(fp) == 0) {
                buffer[len++] = '\0';
                pi->cmdline = strdup(buffer);
                pi->pid = pid;
            }
        }
        fclose(fp);
    }
    return pi;
}


int
ftrace_module_init(char **substitute_environment_variables,
        char *killfname, char *ignorefname,
        bool report_checksum, bool report_procinfo,
        bool list_tracked_ignored, bool exclude_tracked_ignored_in_report) {
    substitute_environment_variables_g = substitute_environment_variables;
    report_checksum_g = report_checksum;
    report_procinfo_g = report_procinfo;
    list_tracked_ignored_g = list_tracked_ignored;
    exclude_tracked_ignored_in_report_g = exclude_tracked_ignored_in_report;

    if (init_tree_structures() != EXIT_SUCCESS) {
        fprintf(stderr, "Error during data structure initialization\n");
        return EXIT_FAILURE;
    }

    if (load_regex_rules(ignorefname,
            exclude_patterns_compiled_regex_g) != EXIT_SUCCESS) {
        fprintf(stderr, "Error during loading ignore rules\n");
        return EXIT_FAILURE;
    }

    if (load_regex_rules(killfname,
            kill_patterns_compiled_regex_g) != EXIT_SUCCESS) {
        fprintf(stderr, "Error during loading kill rules\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}

void
ftrace_module_destroy() {
    free_regex_rules(exclude_patterns_compiled_regex_g);
    free_regex_rules(kill_patterns_compiled_regex_g);
    g_tree_destroy(tracked_file_entries_tree_g);
    g_tree_destroy(ignore_files_tree_g);
}

/* Remove /bla/../bla and /bla/./bla/ patterns from the path */
static int
normalize_path(char *output, char *input) {
  char result[PATH_MAX]="";
  size_t resultlen = 0;
  size_t currentlen = 0;

  char *current = input;
  char *end = &input[strlen(input)];
  char *next = NULL;
  char *slash = NULL;

  /* Check input */
  if (input == NULL) {
    fprintf(stderr,"Internal error! Empty input for %s\n",
        __FUNCTION__);
    return EXIT_FAILURE;
  }

  /* Go slash by slash and fix stuff if we have sonething to fix */
  for (current = input; current < end; current=next+1) {
    /* Get pointer to next slash */
    next = memchr(current, '/', end-current);

    /* stop if not found */
    if (next == NULL) {
      next = end;
    }

    /* Calculate len of current segment */
    currentlen = next-current;

    /* if current segment len is one or two then we check them */
    switch(currentlen) {
    case 2:
      if (current[0] == '.' && current[1] == '.') {
    slash = memrchr(result, '/', resultlen);
    if (slash != NULL) {
      resultlen = slash - result;
    }
    continue;
      }
      break;
    case 1:
      if (current[0] == '.') {
    continue;
      }
      break;
    case 0:
      continue;
    }
    result[resultlen++] = '/';
    memcpy(&result[resultlen], current, currentlen);
    resultlen += currentlen;
  }

  if (resultlen == 0) {
    result[resultlen++] = '/';
  }

  result[resultlen] = '\0';
  strcpy(output,result);

  return EXIT_SUCCESS;
}


/* free memory used by the string key
* This is a callback method called for each key by g_tree_destroy
*/
static void
destroy_key(gpointer data) {
  free((char *)data);
}

/*
 * free memory used by the value stored.
 * This is callback method called by g_tree_destroy for each value in the tree.
 * Depending on behavior defined by the global value of report_procinfo, we
 * either clean the stored value or nothing in case of the dummy int.
 */
static void
destroy_value(gpointer data) {
    ProcInfo *pi = (ProcInfo *)data;
    if (report_procinfo_g == 1) {
        free((char *)pi->cmdline);
        free(pi);
    }
    /* else do nothing */
}

/* This function should only be called on files that exist
*/
static int
add_file_to_ignore_filter(char* path_ptr)
{
  char *path;
  char absp[PATH_MAX];

  if (path_ptr == NULL) {
    fprintf(stderr,"Internal error! Empty input for %s\n",
        __FUNCTION__);
    return EXIT_FAILURE;
  }

  /* get absolute path */
  if (realpath(path_ptr, absp) == NULL) {
    fprintf(stderr, "realpath failed for %s\n",path_ptr);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return EXIT_FAILURE;
  }

  /* Exit function if path already is in the tree  */
  if(g_tree_lookup(ignore_files_tree_g, absp) != NULL) {
    return EXIT_SUCCESS;
  }

  /* Store string in ignore tree */
  path = strdup(absp);
  g_tree_insert(ignore_files_tree_g, path, (gpointer)&tree_dummy_value_g);

  return EXIT_SUCCESS;
}

/* Check if the file should be processed (added to tracking and/or ignore filter)
*/
static int
should_file_be_processed(char *path_ptr)
{
  struct stat file_stat;

  /* Skip files that doesn't exist */
  if (stat(path_ptr, &file_stat) < 0)
    return 0;

  /* Not interested in directories */
  if (S_ISDIR(file_stat.st_mode))
    return 0;

  /* TODO: get actual file and check */
  if (S_ISLNK(file_stat.st_mode))
    return 0;

  return 1;
}

/* Handle opened file
 */
int
ftrace_handle_opened_file(char *path_ptr, int pid)
{
  char absp[PATH_MAX];
  int regexresult;

  /* Check file from last ignore call */
  if(last_created_g != NULL) {
    if(should_file_be_processed(last_created_g)) {
      add_file_to_ignore_filter(last_created_g);
      free((char *)last_created_g);
      last_created_g = NULL;
    }
  }

  /* Check if file should be processed */
  if(!should_file_be_processed(path_ptr)) {
    return EXIT_SUCCESS;
  }

  /* Fix up path */
  if (normalize_path(absp, path_ptr) == EXIT_FAILURE) {
    fprintf(stderr, "Path normalization failed for %s\n",path_ptr);
    return EXIT_FAILURE;
  }

  /* Exit function if path already is in the ignore tree  */
  if(g_tree_lookup(ignore_files_tree_g, absp) != NULL) {
    return EXIT_SUCCESS;
  }

  /* Exit function if path already is in the tree  */
  if(g_tree_lookup(tracked_file_entries_tree_g, absp) != NULL) {
    return EXIT_SUCCESS;
  }

  regexresult = regex_match(absp, exclude_patterns_compiled_regex_g);
  if (regexresult == REGEX_MATCH) {
      g_tree_insert(ignore_files_tree_g, strdup(absp), (gpointer)&tree_dummy_value_g);
      return EXIT_SUCCESS;
  } else if (regexresult == REGEX_ERROR) {
      return EXIT_FAILURE;
  }

  /* Store string in tracked files */
  if (report_procinfo_g == 0) {
      g_tree_insert(tracked_file_entries_tree_g, strdup(absp), (gpointer)&tree_dummy_value_g);
  } else  {
      ProcInfo *pi = create_procinfo(pid);
      g_tree_insert(tracked_file_entries_tree_g, strdup(absp), (gpointer)pi);
  }

  regexresult = regex_match(absp, kill_patterns_compiled_regex_g);
  if (regexresult == REGEX_MATCH) {
      kill(pid, SIGTERM);
      return EXIT_SUCCESS;
  } else if (regexresult == REGEX_ERROR) {
      return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}

static inline int
regex_match(const char * const absp, regex_t **patterns) {
    regex_t *regex;
    int i;
    char msgbuf[100];
    int reti;

    for (i = 0; i < REGEX_MAX; i++) {
        regex = patterns[i];
        /* skip whole list check, exit loop on first empty slot */
        if (regex == NULL)
            break;

        reti = regexec(regex, absp, 0, NULL, 0);
        if (!reti) {
            return REGEX_MATCH;

        } else if (reti != REG_NOMATCH) {
            regerror(reti, regex, msgbuf, sizeof(msgbuf));
            fprintf(stderr, "Regex match failed: %s\n", msgbuf);
            return REGEX_ERROR;
        }
    }
    return REGEX_NOMATCH;
}


/* Handle file that should be ignored
 */
int
ftrace_update_ignore_list(char* path_ptr)
{
  /* Check file from last ignore call */
  if(last_created_g != NULL)
  {
    if(should_file_be_processed(last_created_g)) {
      add_file_to_ignore_filter(last_created_g);
      free((char *)last_created_g);
      last_created_g = NULL;
    }
  }

  /* Check file for this ignore */
  if(should_file_be_processed(path_ptr)) {
    add_file_to_ignore_filter(path_ptr);
  } else {
    /* Change so that 'path_ptr'-path is stored in 'last_created_g' */
    if(last_created_g != NULL) {
      free((char *)last_created_g);
    }
    last_created_g = strdup(path_ptr);
  }
  return EXIT_SUCCESS;
}

/* Precompile regex
*/
static int
compile_and_store_regex(const char *pattern_ptr, regex_t *regex_ptr) {
  int reti = 0;
  /* Compile regular expression */
  reti = regcomp(regex_ptr, pattern_ptr, 0);
  if( reti ) {
    fprintf(stderr, "Could not compile regex\n");
    return EXIT_FAILURE;
  }
  return EXIT_SUCCESS;
}

/* Calculate md5
*/
static int
calculate_md5(unsigned char *to, const char *file_path)
{
  int i;
  MHASH td;
  FILE *fp;
  struct stat sb;
  size_t bytes_read;
  unsigned char *hash;
  unsigned char *data;

  /* Initiate algorithm type context descriptor */
  td = mhash_init(MHASH_MD5);

  /* Initiation failed */
  if (td == MHASH_FAILED) {
    fprintf(stderr, "md5 algorithm descriptor initiation failed\n");
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return EXIT_FAILURE;
  }

  /* Get file size */
  if (stat(file_path, &sb) != 0) {
    fprintf (stderr, "stat failed for '%s'\n",file_path);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return (EXIT_FAILURE);
  }

  /* Allocate memory for entire file */
  data = malloc (sb.st_size + 1);
  if (!data) {
    fprintf (stderr, "Out of memory error.\n");
    return EXIT_FAILURE;
  }

  /* open file */
  fp = fopen(file_path, "r");

  /* Open file failed */
  if (fp == NULL) {
    /* Permission denied, lets skip those files. */
    if (errno == EACCES) {
      return EXIT_SUCCESS;
    }
    fprintf(stderr, "Failed to open %s\n", file_path);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return EXIT_FAILURE;
  }

  /* Read all data into memory */
  bytes_read = fread(data, sizeof (unsigned char), sb.st_size, fp);
  if(bytes_read != sb.st_size) {
    fprintf(stderr, "Error: bytes read '%Zd', expected '%Zd'\n", bytes_read, sb.st_size);
    return EXIT_FAILURE;
  }

  /* Close file to save results */
  /* Close file failed */
  if (fclose(fp) != 0) {
    fprintf(stderr, "Failed to close %s\n", file_path);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return EXIT_FAILURE;
  }

  /* Calculate md5 */
  mhash(td, data, sb.st_size);
  hash = mhash_end(td);

  /* release memory used to store file data */
  free(data);

  /* Copy md5 into supplied 'char *' */
  for (i = 0; i < mhash_get_block_size(MHASH_MD5); i++) {
    to[i] = hash[i];
  }

  /* Free memory allocated by MD5 checksum calculation */
  free(hash);

  return EXIT_SUCCESS;
}

/* Check path for environment variables and replace them
 * with environment variables value
*/
static int
replace_env_variables(char *result_ptr, char *input_path_ptr)
{
  int i = 0;
  int j = 0;
  int last = 0;
  char path[PATH_MAX] = "";
  char name[PATH_MAX] = "";
  char *value_ptr = NULL;

  /* Check input */
  if (input_path_ptr == NULL) {
    fprintf(stderr,"Empty string provided as input to %s function\n",__func__);
    return EXIT_FAILURE;
  }

  for (i=0;i<strlen(input_path_ptr);i++) {
    /* If $ found */
    if ('$' == input_path_ptr[i]) {
      /* Look for environment variable name end */
      for (j=i;j<strlen(input_path_ptr);j++) {
    if ('/' == input_path_ptr[j]) {
      break;
    }
      }
      /* Extract env variable name */
      strncpy(name,input_path_ptr+i+1,j-i-1);
      /* Get variable value */
      value_ptr = getenv(name);
      /* Error if not found */
      if (value_ptr == NULL) {
    fprintf(stderr,"Env variable %s used in the report is not set in the current env\n",name);
    return EXIT_FAILURE;
      }

      if (last == 0) { /* First env variable found */
    /* first env variable in the midle of the line (we don't check
     * env variable in the beginning becasuse there is nothing to do with it
     */
    if (i > 0) {
      /* take first i-1 bytes in the path */
      strncpy(path,input_path_ptr,i-1);
    }
      } else if (last > 0) { /* Not the first env variable */
    /* Add to the end path variable path from the end of last env variable
     * till current env variable name start
     */
    strncpy(path+strlen(path),input_path_ptr+last,i-last);
      } else if (last < 0) { /* Something is completly wrong */
    fprintf(stderr,"Something is really broken here...\n");
    return EXIT_FAILURE;
      }

      /* Add value of env variable */
      strcat(path,value_ptr);
      /* Remember position for env variable name end */
      last = j;
      /* Seek index to the current env variable end */
      i=j;
      /* Clean name */
      memset(name, 0, sizeof(name));;
    }
  }

  /* Add remaining part of the string */
  strcat(path,input_path_ptr+last);

  /* Return result */
  strcpy(result_ptr,path);

  return EXIT_SUCCESS;
}


static inline void
write_checksum(FILE *fp, char *path) {
    int i;
    unsigned char hash[mhash_get_block_size(MHASH_MD5)];

    /* Calculate md5 */
    if(calculate_md5((unsigned char*)&hash, path) != 0) {
      fprintf(stderr, "Failed to calculate md5 for '%s'\n", path);
    }
    for (i = 0; i < mhash_get_block_size(MHASH_MD5); i++) {
      fprintf(fp,"%.2x",hash[i]);
    }
    /* column tab after hash */
    fprintf(fp, "\t");
}

static inline void
write_procinfo(FILE *fp, ProcInfo *pi) {
    fprintf(fp, "\t%s (%d)", pi->cmdline, pi->pid);
}

static inline void
write_filepath(FILE *fp, char *path) {
  int i;
  for(i = 0;i < MAX_S_ENV;i++) {
    if (substitute_environment_variables_g[i] == NULL) {
      /* No match */
      fprintf(fp,"%s", path);
      break;
    }
    char* env_str = getenv(substitute_environment_variables_g[i]);
    if(strstr(path, env_str)) {
      /* Match */
      fprintf(fp,"$%s%s", substitute_environment_variables_g[i], path + strlen(env_str));
      break;
    }
  }
}

/**
 * Write node entry to file
 * function should always return FALSE to indicate to g_tree_foreach not
 * to abort traversal.
*/
static gboolean
write_file_entry(gpointer key, gpointer value, gpointer data) {
  char *path = (char*) key;
  FILE *fp = (FILE*)data;

  if (list_tracked_ignored_g || exclude_tracked_ignored_in_report_g) {
      if(g_tree_lookup(ignore_files_tree_g, path) != NULL) {
          if (list_tracked_ignored_g == 1) {
              fprintf(stderr, "Tracked file found in ignore list: %s\n", path);
          }
          if (exclude_tracked_ignored_in_report_g == 1) {
              return FALSE;
          }
      }
  }

  if (report_checksum_g == 1) {
      write_checksum(fp, path);
  }

  write_filepath(fp, path);

  if (report_procinfo_g == 1) {
      write_procinfo(fp, (ProcInfo*)value);
  }

  fprintf(fp, "\n");

  return FALSE;
}

/**
 * Write node entry to file
 * function should always return FALSE to indicate to g_tree_foreach not
 * to abort traversal.
*/
static gboolean
write_ignore_file_entry(gpointer key, gpointer value, gpointer data) {
      char *path = (char*) key;
      FILE *fp = (FILE*)data;
      write_filepath(fp, path);
      fprintf(fp, "\n");
      return FALSE;
}

/* Agregate results and put them to report file
 */
int
ftrace_dump_result_to_file(char* reportfname, char* ignorereportfname)
{
  int result = EXIT_SUCCESS;

  result |= dump_tree_to_file(tracked_file_entries_tree_g, reportfname,
          (GTraverseFunc)write_file_entry);

  result |= dump_tree_to_file(ignore_files_tree_g, ignorereportfname,
          (GTraverseFunc)write_ignore_file_entry);

  return result;
}

static inline int
dump_tree_to_file(GTree * tree, char *filename, GTraverseFunc savefunc) {
    FILE *fp = NULL;
    if (filename != NULL) {
        fp = open_file(filename);
        if (fp == NULL) {
            return EXIT_FAILURE;
        }
        g_tree_foreach(tree, savefunc, fp);
        return close_file(fp, filename);
    }
    return EXIT_SUCCESS;
}

static inline FILE*
open_file(char *filename) {
    FILE *fp=fopen(filename, "w");
    if (fp == NULL) {
        fprintf(stderr, "Failed to create %s\n", filename);
        fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    }
    return fp;
}

static inline int
close_file(FILE *fp, char *filename) {
    if (fclose(fp) != 0) {
        fprintf(stderr, "Failed to close %s\n", filename);
        fprintf(stderr, "Error: %s, errno=%d\n", strerror(errno),
                errno);
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}

/* Read report and check files for changes
 */
int
ftrace_check_for_changes(char* inputfname, bool print_diff)
{
  unsigned char ucurrent_hash[mhash_get_block_size(MHASH_MD5)];
  char temp_buffer[PATH_MAX + mhash_get_block_size(MHASH_MD5) +1];
  char input_hash[mhash_get_block_size(MHASH_MD5)];
  char current_hash[mhash_get_block_size(MHASH_MD5)*2 +1];
  char path[PATH_MAX];
  int i = 0;
  int return_code = FTRACE_TRIGGER_NO_CHANGES_FOUND;
  char *loc_ptr = NULL;
  FILE *fp_ptr = NULL;
  struct stat file_stat;

  /* No file no check */
  if (inputfname == NULL)
    return FTRACE_TRIGGER_CHANGES_FOUND;

  /* Still, no file no check */
  if (stat(inputfname, &file_stat) < 0) {
    return FTRACE_TRIGGER_CHANGES_FOUND;
  }

  /* Read input file */
  fp_ptr=fopen(inputfname, "r");

  /* Open file failed */
  if (fp_ptr == NULL) {
    fprintf(stderr,"Failed to open %s\n",inputfname);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return FTRACE_TRIGGER_ERROR;
  }

  /* Read file till the end */
  while(fgets(temp_buffer,PATH_MAX,fp_ptr) != NULL) {

    /* Remove newline character added by fgets */
    if( temp_buffer[strlen(temp_buffer)-1] == '\n' )
       temp_buffer[strlen(temp_buffer)-1] = 0;

    /* check line for delimeter and get pointer to the hash */
    loc_ptr = strtok(temp_buffer,"\t");

    /* Something wrong with input file structure */
    if (loc_ptr == NULL) {
      fprintf(stderr,"Could not find delimiter in the %s line\n",temp_buffer);
      return_code = FTRACE_TRIGGER_ERROR;
      break;
    }

    /* Copy hash to separate variable */
    if (!strcpy(input_hash,loc_ptr)) {
    fprintf(stderr,"Failed to extract hash from %s\n",temp_buffer);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return_code = FTRACE_TRIGGER_ERROR;
    break;
    }

    /* Get pointer to path */
    loc_ptr = strtok(NULL, "\t");

    /* Something wrong with input file structure */
    if (loc_ptr == NULL) {
      fprintf(stderr,"Could not find path in the %s line\n",temp_buffer);
      return_code = FTRACE_TRIGGER_ERROR;
      break;
    }

    /* Get real path without env variables in it */
    if (replace_env_variables((char*)&path,loc_ptr) == EXIT_FAILURE) {
      return_code = FTRACE_TRIGGER_ERROR;
      break;
    }

    /* Can't find file from the report - consider rebuild */
    if (stat(path, &file_stat) < 0) {
      fprintf(stdout, "%s stated in %s was not found. Consider rebuild\n",
          path,
          inputfname);
      return_code = FTRACE_TRIGGER_CHANGES_FOUND;
    }

    /* Calculate md5 for the file extracted from the input file */
    if (calculate_md5((unsigned char*)&ucurrent_hash, path) != 0) {
      fprintf(stderr, "Failed to calculate md5 for '%s'\n", path);
      return_code = FTRACE_TRIGGER_ERROR;
      break;
    }

    /* We need to transform hash to string to be able to compare it
       with hash from the file */
    for(i=0;i<mhash_get_block_size(MHASH_MD5);i++) {
      sprintf(&current_hash[2*i], "%.2x", ucurrent_hash[i]);
    }

    /* Compare hash's */
    if (strcmp(current_hash,input_hash) != 0) {
      /* Changes found. Return success to continue with build */
      return_code = FTRACE_TRIGGER_CHANGES_FOUND;
      if ( print_diff ) {
    fprintf(stdout, "Changes found for %s\n", path);
      }
    }
  }

  /* Close file failed */
  if (fclose(fp_ptr) != 0) {
    fprintf(stderr,"Failed to close %s\n",inputfname);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return FTRACE_TRIGGER_ERROR;
  }

  return return_code;
}

/* Create the binary tree-structure
*/
static int
init_tree_structures() {

  /* Should always be null at execution start */
  last_created_g = NULL;

  tracked_file_entries_tree_g = g_tree_new_full((GCompareDataFunc)g_strcmp0,
          NULL, (GDestroyNotify)destroy_key, (GDestroyNotify)destroy_value);
  if(tracked_file_entries_tree_g == NULL) {
    return EXIT_FAILURE;
  }

  ignore_files_tree_g = g_tree_new_full((GCompareDataFunc)g_ascii_strcasecmp, NULL, (GDestroyNotify)destroy_key, NULL);
  if(ignore_files_tree_g == NULL) {
    return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}


/* Read and save exclude rules
 */
static int
load_regex_rules(char* ignorefname, regex_t **regex_list)
{
  char temp_buffer[PATH_MAX];
  FILE *fp = NULL;
  int j = 0;
  int len = 0;
  int reti;
  regex_t *regex;
  struct stat file_stat;

  /* No file no rules */
  if (ignorefname == NULL)
    return EXIT_SUCCESS;

  /* Skip files that doesn't exist */
  if (stat(ignorefname, &file_stat) < 0) {
    fprintf(stderr,"%s no such file\n",ignorefname);
    return EXIT_FAILURE;
  }

  /* Read ignore rules */
  fp=fopen(ignorefname, "r");

  /* Open file failed */
  if (fp == NULL) {
    fprintf(stderr,"Failed to open %s\n",ignorefname);
    fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
    return EXIT_FAILURE;
  }

  /* Read file till the end */
  while(fgets(temp_buffer,PATH_MAX,fp) != NULL)
    {
      /* Remove newline character added by fgets */
      len = strlen(temp_buffer);
      if( temp_buffer[len-1] == '\n' )
    temp_buffer[len-1] = 0;

      /* allocate memory */
      regex = malloc(sizeof(regex_t));
      if (!regex) {
        fprintf (stderr, "Out of memory error.\n");
        return EXIT_FAILURE;
      }

      /* Compile regex */
      reti = compile_and_store_regex(temp_buffer, regex);
      if(reti != EXIT_SUCCESS) {
        return reti;
      }

      /* Save rule in exclude list */
      regex_list[j] = regex;
      j++;
    }

  /* Close file failed */
  if (fclose(fp) != 0) {
      fprintf(stderr,"Failed to close %s\n",ignorefname);
      fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
      return EXIT_FAILURE;
  }

  return EXIT_SUCCESS;
}

static void
free_regex_rules(regex_t **regex_list) {
  int i;
  for (i=0;i<REGEX_MAX;i++) {
    if(regex_list[i] == NULL)
      break;
    regfree(regex_list[i]);
  }
}


/*
 * Print path string specified by address `addr' and length `n'.
 * If path length exceeds `n', append `...' to the output.
 */
void
ftrace_extract_and_save_path(struct tcb *tcp, long addr, int open_mode)
{
    char path[PATH_MAX + 1];
    char cwd[PATH_MAX];
    char buffer[PATH_MAX];
    int nul_seen;
    ssize_t r;

    if (!addr) {
        tprints("NULL");
        return;
    }

    /* Fetch one byte more to find out whether path length > n. */
    nul_seen = umovestr(tcp, addr, PATH_MAX + 1, path);
    if (nul_seen >= 0) {
      path[PATH_MAX] = '\0';

      /* Path is absolute */
      if (path[0] == '/') {
        /* if file just created */
        if (open_mode == FTRACE_MODE_CREATE)
          ftrace_update_ignore_list(path);
        else if (open_mode == FTRACE_MODE_OPEN)
          ftrace_handle_opened_file(path, tcp->pid);
        else
          fprintf(stderr,"Unexpected value %d, at %s:%d",
              open_mode,
              __FILE__,
              __LINE__);
      }
      else {
        /* Compile path to cwd link for process */
        sprintf(buffer, "/proc/%d/cwd", tcp->pid);
        /* Read current path of the process from /proc/pid/cwd */
        r = readlink(buffer, cwd, PATH_MAX);
        if (r<0) {
          fprintf(stderr,"Readlink error for %s",buffer);
          fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
          return;
        }
        if (r>PATH_MAX) {
          fprintf(stderr,"Path is too long %s",buffer);
          fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
          return;
        }
        /* Set end of string, readlink return string without it */
        cwd[r] = '\0';

        /* Len of resulting string is longer than allowed */
        if ((strlen(cwd) + strlen("/") + strlen(path)) > PATH_MAX)
        if (r>PATH_MAX) {
          fprintf(stderr,"Path is too long %s/%s",cwd,path);
          fprintf(stderr,"Error: %s, errno=%d\n",strerror(errno),errno);
          return;
        }
        strcat(cwd, "/");
        strcat(cwd, path);

        if (open_mode == FTRACE_MODE_CREATE)
          ftrace_update_ignore_list(cwd);
        else if (open_mode == FTRACE_MODE_OPEN)
          ftrace_handle_opened_file(cwd, tcp->pid);
        else
          fprintf(stderr,"Unexpected value %d, at %s:%d",
              open_mode,
              __FILE__,
              __LINE__);
      }
    }
}
