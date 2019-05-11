<?php
class Admin extends CI_Controller
{
    private $cacheDir;

    public function __construct()
    {
        parent::__construct();
        $this->cacheDir = $this->config->item('cache_dir');

    }

    public function index()
    {
        $data['cacheDirs'] = array();
        $data['cacheRefLists'] = array();
        $data['base_url'] = $this->config->item('base_url');

        foreach (getSubDirs($this->cacheDir) as $repoPath) {
            $cachedRefs = array();
            foreach (getSubDirs($repoPath) as $refPath) {
                array_push($cachedRefs, new FileStruct($refPath, $this->cacheDir));
            }
            $repoStruct = new FileStruct($repoPath, $this->cacheDir);
            array_push($data['cacheDirs'], $repoStruct);

            usort($cachedRefs, array("FileStruct", "cmpTime"));
            $data['cacheRefLists'][$repoStruct->path] = $cachedRefs;
        }

        usort($data['cacheDirs'], array("FileStruct", "cmpName"));

        $this->load->view('admin', $data);
    }
}

class FileStruct
{
    public $path;
    public $relPath;
    public $name;
    public $time;

    public function __construct($path, $baseDir)
    {
        $this->path = $path;
        $this->relPath = self::getRelativePath($path, $baseDir);
        $this->name = basename($path);
        $this->time = date("F d Y H:i:s.", filemtime($path));
    }

    public static function cmpName($a, $b)
    {
        $al = strtolower($a->name);
        $bl = strtolower($b->name);
        if ($al == $bl) {
            return 0;
        }
        return ($al > $bl) ? +1 : -1;
    }

    public static function cmpTime($a, $b)
    {
        if ($a->time == $b->time) {
            return 0;
        }
        return ($a->time < $b->time) ? +1 : -1;
    }

    protected static function getRelativePath($path, $baseDir)
    {
        return str_replace($baseDir . '/', '', $path);
    }
}
