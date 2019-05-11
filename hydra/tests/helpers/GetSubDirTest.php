<?php
class GetSubDirsTest extends PHPUnit_Framework_TestCase
{
    private $tmpDir;

    public static function setUpBeforeClass()
    {
        get_instance()->load->helper('hydra');
    }

    protected function setUp()
    {
        $this->tmpDir = sys_get_temp_dir()."/hydra_tests";
        mkdir($this->tmpDir."/d1", 0777, True);
        mkdir($this->tmpDir."/d2", 0777, True);
        mkdir($this->tmpDir."/d3", 0777, True);
    }

    protected function tearDown()
    {
        rmdir("$this->tmpDir/d1");
        rmdir("$this->tmpDir/d2");
        rmdir("$this->tmpDir/d3");
        rmdir($this->tmpDir);
    }

    public function testGetSubDirs() {

        $subDirs = getSubDirs($this->tmpDir);
        $this->assertTrue(count($subDirs) == 3);
        $this->assertTrue(strcmp($subDirs[0], "$this->tmpDir/d1") == 0);
        $this->assertTrue(strcmp($subDirs[1], "$this->tmpDir/d2") == 0);
        $this->assertTrue(strcmp($subDirs[2], "$this->tmpDir/d3") == 0);
    }
}
?>
