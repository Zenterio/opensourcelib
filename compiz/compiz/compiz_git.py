import subprocess


def addgitparser(subparser, parentparser):
    parser_git = subparser.add_parser('git', parents=[parentparser])
    group = parser_git.add_mutually_exclusive_group()
    group.add_argument('--staged', help='use staged files as input', action='store_true')
    group.add_argument('--workspace', help='use unstaged files as input', action='store_true')
    parser_git.add_argument(
        'hash', nargs='*', help='Hashes to diff, either one against head, or two against eachother')
    parser_git.set_defaults(func=_githandler)


def _githandler(args):
    files = []
    try:
        if args.staged:
            files = (
                subprocess.check_output(
                    ['git', 'diff', '--name-only', '--cached'], stderr=subprocess.STDOUT))
        elif args.workspace:
            files = (
                subprocess.check_output(['git', 'diff', '--name-only'], stderr=subprocess.STDOUT))
        elif len(args.hash) == 2:
            files = (
                subprocess.check_output(
                    ['git', 'diff', '--name-only', args.hash[0], args.hash[1]],
                    stderr=subprocess.STDOUT))
        elif len(args.hash) == 1:
            files = (
                subprocess.check_output(
                    ['git', 'diff', '--name-only', args.hash[0]], stderr=subprocess.STDOUT))
        else:
            print('No hash specified')
            exit(0)
    except subprocess.CalledProcessError as e:
        print('Git error:')
        print(e.output.decode('utf-8'))
        exit(0)
    files = files.decode('utf-8').split('\n')
    files = [args.root + '/' + x for x in files if x != '']
    return files
