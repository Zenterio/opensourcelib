git-project-pull(1) -- Update git project repository with remote changes
================================

## SYNOPSIS

`git-project-pull` [-h] [--help] [&lt;OPTIONS&gt;]

## DESCRIPTION

Fetches and merges remote commits onto local state. Uses merge by default, or rebase if specified.

Does not automatically handle any conflicts, except those handled by merge or rebase, respectively.

May leave your current repository in an unclean state.

## OPTIONS

  * -h:
    Show short usage description and exits

  * --help:
    Show this man page and exits
    
  * -m <message>:
    Use <message> for merge commits
    
  * --rebase:
    Uses rebase instead of merge

## EXAMPLES

To get the latest work on a branch where you have no local commits:

  * git project pull  
  
If there are local commits to merge you need to supply a commit message for the merge commits to use:

  * git project pull -m 'commit message'
  
If you want to rebase local commits instead of using merge:

  * git project pull --rebase

## DETAILS
git-project-pull performs:

  * git fetch --recurse-submodules
  
If fast forward is possible:

  * git pull in each submodule on the branch
  
If fast forward is not possible:

  * git project merge <remote branch>
  
If --rebase is given:

  * git project rebase <remote branch>