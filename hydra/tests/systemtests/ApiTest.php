<?php

class ApiTests extends PHPUnit_Framework_TestCase
{
    protected static $CI;
    protected static $URL;
    protected static $API;

    public static function setUpBeforeClass()
    {
        self::$CI =& get_instance();
        self::$CI->config->load("hydra");
        self::$URL = "http://localhost/hydra";
        self::$API = self::$URL . '/api';
    }

    public function setUp() {
        $class = get_class($this);
        log_message('debug', "{$class}::{$this->getName()}: start");
        /* Get content to force system to setup cache entry */
        $content = self::get_actual_content(self::get_branch(), 1);
        $expected = self::get_expected_content(3, 1);
        $this->assertEquals($expected, $content, "Failed to setup cache entry. No point in running test.");
    }

    public function tearDown()
    {
        self::clean_cache_entry();
        $class = get_class($this);
        log_message('debug', "{$class}::{$this->getName()}: end");
    }

    public function test_clear_cache_all()
    {
        log_message('debug', "ApiTests:test_clear_cache_all");
        $api = self::$API . "/clear-cache-all";
        $status = self::get_http_status($api);
        $this->assertEquals(200, $status, "clear-cache-all returned incorrect status code.");
        $content = file_get_contents($api);
        log_message('debug', "ApiTests:test_clear_cache_all (content=$content)");
        $this->assertCacheRemoved();
    }

    public function test_clear_cache_older_than_keeps_entries_younger_than_n_hours()
    {
        $api = self::$API . "/clear-cache-older-than/1";
        $status = self::get_http_status($api);
        $this->assertEquals(200, $status, "clear-cache-older-than returned incorrect status code.");
        $content = file_get_contents($api);
        log_message('debug', "ApiTests:test_clear_cache_older_than (content=$content)");
        $this->assertCachePresent();
    }

    public function test_clear_cache_older_than_deletes_entries_older_than_x_hours()
    {
        # by passes route by using exact method name, to be able to use
        # floating point and not just whole hours
        $api = self::$API . "/clearCacheOlderThan/0.0001";
        # wait one more second than limit to make sure cache is older than limit.
        sleep(0.0001*60*60+1);
        $status = self::get_http_status($api);
        $this->assertEquals(200, $status, "clear-cache-older-than returned incorrect status code.");
        $content = file_get_contents($api);
        log_message('debug', "ApiTests:test_clear_cache_older_than (content=$content)");
        $this->assertCacheRemoved();
    }

    public function test_clear_cache_select()
    {
        $api = self::$API . "/clear-cache-select";
        $repo = self::get_repo();
        $cacheEntry = "$repo/$repo.git";
        $data = array( $cacheEntry => $cacheEntry);
        $this->do_http_post($data, $api);
        $this->assertCacheRemoved("$repo.git");
    }

    protected function assertCacheRemoved($subDir="")
    {
        $this->assertFalse(is_dir(self::get_full_repo_path() . '/' . $subDir));
    }

    protected function assertCachePresent($subDir="")
    {
        $this->assertTrue(is_dir(self::get_full_repo_path() . '/' . $subDir));
    }

    protected function do_http_post($data, $url)
    {
        $dStr = print_r($data, TRUE);
        log_message('debug', "ApiTest::do_http_post (data={$dStr}, url=$url)");
        $options = array(
            'http' => array(
                'header'  => "Content-type: application/x-www-form-urlencoded\r\n",
                'method'  => 'POST',
                'content' => http_build_query($data)
            )
        );
        $context  = stream_context_create($options);
        $result = file_get_contents($url, false, $context);

        return $result;
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
        log_message('debug', "get_http_status (header[0]=$header[0])");
        return intval(substr($header[0], 9, 3));
    }

    protected static function get_full_repo_path()
    {
        $cacheDir = self::$CI->config->item('cache_dir');
        $repo=self::get_repo();
        return "{$cacheDir}/{$repo}";
    }

    protected static function clean_cache_entry()
    {
        $fullRepoPath = self::get_full_repo_path();
        log_message('debug',
                    "ApiTests::clean_cache_entry deleting cache entry (directory=$fullRepoPath)");
        if (is_dir($fullRepoPath)) {
            system("rm -rf '$fullRepoPath'", $status);
            log_message('debug',
                        "ApiTests::clean_cache_entry deleting cache entry (status=$status)");
        }
    }
}
?>
