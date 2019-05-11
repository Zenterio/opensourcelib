<?php
class Gitcc extends CI_Controller
{
    // This is a list of repos permitted to checkout using this script
    private $repos = array();

    // Where GIT repositories lives
    private $gitBase = '';

    // Cache file system location
    private $cacheDir = '';

    public function __construct()
    {
        parent::__construct();
        $this->repos = $this->config->item('repositories');
        $this->cacheDir = $this->config->item('cache_dir');
        $this->gitBase = $this->config->item('repository-server');
        $this->remoteGit = "GIT_SSH='/usr/share/hydra/scripts/ssh.sh' git";
        if (!(is_dir($this->cacheDir) && is_really_writable($this->cacheDir)))
        {
            log_message('ERROR', "Cache dir does not exist or is not writable (cache-dir={$this->cacheDir})");
            showError("Ths cache directory is not propertly configured");
        }
    }

    public function get($repo, $ref)
    {
        log_message('debug', "gitcc::get (repo=$repo, ref=$ref)");
        if (!$this->repoPermitted($repo)) {
            show_error("Not permitted to checkout repository ".$repo."<br/>");
        }
        $repoPath = "$this->cacheDir/$repo/$repo.git";
        $this->updateRepo($repoPath, $repo);
        $hash = $this->getHash($repoPath, $ref);

        $path = $this->getPath();

        $queries = $this->input->server('QUERY_STRING');
        log_message('debug', "gitcc::get (server.query=$queries)");

        $destDir = "$this->cacheDir/$repo/$hash";
        log_message('debug', "gitcc::get (destination dir=$destDir)");

        if (file_exists($destDir)) {
            log_message('debug', "gitcc::get destination directory exists (dir=$destDir)");
        } else {
            $this->gitCheckout($repoPath, $destDir, $hash);
        }

        if (file_exists($destDir)) {
            $this->touchFile($destDir);
            $redir = "/hydra/cache/$repo/$hash/$path";
            $redir = ($queries) ? "$redir?$queries" : $redir;
            log_message('debug', "gitcc::gitclone redirect (redir=$redir)");
            header("Location: $redir");
        } else {
            log_message('error', "Failed to create checkout (repo=$repo, ref=$ref (-> hash=$hash)) ");
        }
    }

    private function repoPermitted($repo)
    {
        log_message('debug', "gitcc::repoPermitted (repo=$repo)");
        return in_array($repo, $this->repos);
    }

    private function getPath()
    {
        // remove 4 first, gitcc, gitclone, $repo, $ref
        $remaining_segments = array_slice($this->uri->rsegment_array(), 4);
        $path = implode("/", $remaining_segments);
        log_message('debug', "gitcc::get (path=$path)");
        return $path;
    }

    private function getHash($repoPath, $ref)
    {
        log_message('debug', "gitcc::getLatestHash (repopath=$repoPath, ref=$ref)");
        $command = "git --git-dir='$repoPath' rev-parse '$ref'";
        $hash = $this->runCommand($command, $status, FALSE);
        if ($status != 0)
    	{
            $msg = "Could not find the reference $ref <br/>".
                   "Exit code: $status <br/>".
                   "See /var/log/apache2/error.log and /var/log/hydra/ for more information... <br/>";
            log_message('ERROR', $msg);
            show_error($msg, $status_code=404);
    	}
        return $hash;
    }

    private function updateRepo($repoPath, $repo)
    {
        log_message('debug', "gitcc::updateRepo (repoPath=$repoPath, repo=$repo)");
        if (!file_exists($repoPath)) {
            $this->mirror($this->getRemote($repo), $repoPath);
        }
        $this->gitFetch($repoPath);
        $this->touchFile($repoPath);
    }

    private function mirror($remote, $repoPath)
    {
        log_message('debug', "gitcc::mirror (remote=$remote, repoPath=$repoPath)");
        $command = "{$this->remoteGit} clone --mirror --quiet '$remote' '$repoPath'";
        $this->runCommand($command);
    }

    private function gitFetch($repoPath)
    {
        log_message('debug', "gitcc::gitFetch (repoPath=$repoPath)");
        $command = "{$this->remoteGit} --git-dir='$repoPath' fetch --quiet";
        $this->runCommand($command);
    }

    private function gitCheckout($repoPath, $dest, $ref)
    {
        log_message('debug', "gitcc::createCheckout (repoPath=$repoPath, dest=$dest, ref=$ref)");
        mkdir($dest, 0770, true);
        $command = "git --work-tree='$dest' --git-dir='$repoPath' checkout --force --quiet '$ref'";
        $this->runCommand($command);
    }

    private function touchFile($path)
    {
        if (file_exists($path)) {
            log_message('debug', "gitcc:touchFile (path=$path)");
            $command = "touch '$path'";
            $this->runCommand($command);
        }
    }

    private function getRemote($repo) {
        return $this->config->item('repository-server') . $repo;
    }

    private function runCommand($command, &$status=NULL, $showError=TRUE)
    {
        log_message('debug', "gitcc::runCommand (command=$command)");
        $output = array();
        exec($command, $output, $status);
        log_message('debug', "gitcc::runCommand (status=$status)");
        $output = implode("\n", $output);
        log_message('debug', "gitcc::runCommand (output=$output)");
        if ($status != 0 && $showError) {
            $msg="Command failed with exit status $status. See /var/log/hydra/ and /var/log/apache2/error.log for more information";
            log_message('ERROR', $msg);
            log_message('ERROR', $output);
            show_error($msg, $status_code=500);
        }
        return $output;
    }
}
?>
