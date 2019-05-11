<?php

class GitCCTests extends PHPUnit_Framework_TestCase
{
    protected static $CI;
    protected static $URL;

    public static function setUpBeforeClass()
    {
        self::$CI =& get_instance();
        self::$CI->config->load("hydra");
        self::$URL = "http://localhost/hydra";
    }

    public static function tearDownAfterClass()
    {
        self::clean_cache_entry();
    }

    public function setUp()
    {
        $class = get_class($this);
        log_message('debug', "{$class}::{$this->getName()}: start");
    }

    public function tearDown()
    {
        $class = get_class($this);
        log_message('debug', "{$class}::{$this->getName()}: end");
    }

    public function test_get_full_sha()
    {
        $sha_id = 1;
        $file_id = 1;
        $actual = self::get_actual_content(self::get_sha($sha_id), $file_id);
        $expected = self::get_expected_content($sha_id, $file_id);
        $this->assertEquals($expected, $actual, "Failed to get full sha");
    }

    public function test_get_branch()
    {
        $file_id = 2;
        $actual = self::get_actual_content(self::get_branch(), $file_id);
        $expected = self::get_expected_content(3, $file_id);
        $this->assertEquals($expected, $actual, "Failed to get branch");
    }

    public function test_get_tag()
    {
        $file_id = 1;
        $sha_id = 1;
        $actual = self::get_actual_content("first_commit", $file_id);
        $expected = self::get_expected_content($sha_id, $file_id);
        $this->assertEquals($expected, $actual, "Failed to get tag");
    }

    public function test_get_invalid_ref_gives_404()
    {
        $filename = self::get_filename(1);
        $url = self::get_url("invalid_ref", $filename);
        $status = self::get_http_status($url);
        $this->assertEquals(404, $status, "Unexpected status code");
    }

    protected static function get_actual_content($ref, $file_id)
    {
        $filename = self::get_filename($file_id);
        $url = self::get_url($ref, $filename);
        $content = file_get_contents($url);
        return trim($content);
    }

    protected static function get_expected_content($commit_id, $file_id)
    {
        return self::$CI->config->item("file_content_${commit_id}_${file_id}");
    }

    protected static function get_url($ref, $filename)
    {
        $repo = self::get_repo();
        $url = self::$URL;
        return "${url}/gitcc/${repo}/${ref}/${filename}";
    }

    protected static function get_sha($commit_id)
    {
        return self::$CI->config->item("commit_${commit_id}");
    }

    protected static function get_filename($file_id)
    {
        return self::$CI->config->item("file_${file_id}");
    }

    protected static function get_repo()
    {
        return self::$CI->config->item('repo');
    }

    protected static function get_branch()
    {
        return self::$CI->config->item('branch');
    }

    protected static function get_http_status($url)
    {
        $header = get_headers($url, 1);
        log_message('debug', "GitCCTests::get_http_status (header[0]=$header[0])");
        return intval(substr($header[0], 9, 3));
    }

    protected static function clean_cache_entry()
    {
        $cacheDir = self::$CI->config->item('cache_dir');
        $repo=self::get_repo();
        $fullRepoPath = "{$cacheDir}/{$repo}";
        log_message('debug',
                    "GitCCTests::tearDownAfterClass deleting cache entry (directory=$fullRepoPath)");
        if (is_dir($fullRepoPath)) {
            system("rm -rf '$fullRepoPath'", $status);
            log_message('debug',
                        "GitCCTests::tearDownAfterClass deleting cache entry (status=$status)");
        }
    }


}
?>
