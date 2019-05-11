<?php
class Api extends CI_Controller
{

    public $cacheDir;

    public function __construct()
    {
        parent::__construct();
        $this->cacheDir = $this->config->item('cache_dir');
        if (!(is_dir($this->cacheDir) && is_really_writable($this->cacheDir)))
        {
            log_message('ERROR', "Cache dir does not exist or is not writable (cache-dir={$this->cacheDir})");
            showError("Ths cache directory is not propertly configured");
        }
    }

    public function clearCacheSelect()
    {
        log_message('debug', 'Api::clearCacheSelect');
        $post = $this->input->post();
        if($post != NULL) {
            foreach($post as $name => $value) {
                $path = "{$this->cacheDir}/$value";
                log_message('debug', "Api::clearCacheSelect (path=$path)");
                if ($value != '') {
                    $error = $this->clearCacheDir($path);
                    if ($error) {
                        show_error("Error when clearing cache. status=$error cache_dir=$value");
                    }
                }
            }
        }
        $this->load->helper('url');
        redirect($this->config->item('base_url')."admin/");
    }

    public function clearCacheOlderThan($hours)
    {
        log_message('debug', "Api::clearCacheOlderThan (hours=$hours)");
        $toBeCleared = array_merge($this->getSubDirsOlderThan("$this->cacheDir", $hours),
                                   $this->getSubDirsOlderThan("$this->cacheDir/*", $hours));
        foreach($toBeCleared as $dir) {
            $this->clearCacheDir($dir);
        }
        $this->removeEmptySubDirs($this->cacheDir);
    }

    public function clearCacheAll()
    {
        log_message('debug', 'Api::clearCacheAll');
        $this->clearCacheOlderThan(0);
    }

    private function removeEmptySubDirs($baseDir) {
        foreach(getSubDirs($baseDir) as $subDir) {
            if(!glob("$subDir/*", GLOB_ONLYDIR)) {
                $this->clearCacheDir($subDir);
            }
        }
    }

    private function getSubDirsOlderThan($baseDir, $hours)
    {
        $oldDirs = array();
        $now = time();
        foreach(getSubDirs($baseDir) as $subDir) {
            if ($now - filemtime($subDir) >= 60 * 60 * $hours) {
                array_push($oldDirs, $subDir);
            }
        }
        return $oldDirs;
    }

    private function clearCacheDir($dir)
    {
        $status = 1;
        if(file_exists($dir) && isSubDir($this->cacheDir, $dir)) {
            $command = "rm -rf '$dir'";
            log_message('debug', "api::clearCacheDir (command=$command)");
            system($command, $status);
            log_message('debug', "api::clearCacheDir (status=$status)");
        }
        return $status;
    }
}
?>
