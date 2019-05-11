<?php
class ApplicationConfigTests extends PHPUnit_Framework_TestCase
{
    private static $CI;

    public static function setUpBeforeClass()
    {
        self::$CI =& get_instance();
        self::$CI->config->load("hydra");
    }

    public function test_hydra_config_repositories()
    {
        $this->assertEquals(array('test'),
                            self::$CI->config->item('repositories'));
    }

    public function test_hydra_config_cache_dir()
    {
        $this->assertEquals('/var/lib/hydra/cache',
                            self::$CI->config->item('cache_dir'));
    }

    public function test_hydra_config_repository_server()
    {
        $this->assertContains('tests/systemtests/resources/',
                              self::$CI->config->item('repository-server'));
    }

}
?>
