<?php
class HelperTest extends PHPUnit_Framework_TestCase
{
    public static function setUpBeforeClass()
    {
        get_instance()->load->helper('hydra');
    }

    public function test_startsWith_Possitive() {
        $this->assertTrue(startsWith('string', 'str'));
    }

    public function test_startsWith_EmptyPattern() {
        $this->assertTrue(startsWith('string', ''));
    }

    public function test_startsWith_Negative() {
        $this->assertFalse(startsWith('string', 'not'));
    }

    public function test_in_Possitive()
    {
        $this->assertTrue(in('str', 'string'));
        $this->assertTrue(in('tr', 'string'));
        $this->assertTrue(in('string', 'string'));
        $this->assertTrue(in('g', 'string'));
    }

    public function test_in_Empty()
    {
        $this->assertTrue(in('', 'string'));
    }

    public function test_in_Negative()
    {
        $this->assertFalse(in('nope', 'string'));
        $this->assertFalse(in('x', 'string'));
    }

    public function test_isSubDir_StartsWithBase() {
        $this->assertTrue(isSubDir('/usr/hydra', '/usr/hydra/cache'));
        $this->assertFalse(isSubDir('/usr/hydra', '/usr/hydra/../../file'));
    }

    public function test_isSubDir_Relative() {
        $this->assertTrue(isSubDir('/usr/share/hydra', 'cache/pero1'));
        $this->assertFalse(isSubDir('/usr/share/hydra', '../../file'));
    }
}
?>
