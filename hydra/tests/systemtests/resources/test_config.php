<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');


if (isset($_SERVER['HTTP_HOST']))
{
    $base_url = isset($_SERVER['HTTPS']) && strtolower($_SERVER['HTTPS']) !== 'off' ? 'https' : 'http';
    $base_url .= '://'. $_SERVER['HTTP_HOST'];
    $base_url .= str_replace(basename($_SERVER['SCRIPT_NAME']), '', $_SERVER['SCRIPT_NAME']);
    $config['base_url'] = $base_url;
}



/* Application configuraiton */
$config['repositories'] = array('test');

$config['repository-server'] = 'vagrant@localhost:/vagrant/tests/systemtests/resources/';

$config['cache_dir'] = '/var/lib/hydra/cache';

/* Test data - has no meaning for application */
$config['repo'] = 'test';
$config['branch'] = 'master';
$config['commit_1'] = 'c7fad571aeddb703d48a1238d0136fbd13379eac';
$config['commit_2'] = '15a173b6d126463b8d917c04a54b2c43dc54a581';
$config['commit_3'] = '42dc1cc6432cc9d99ff7878e7784d994705ac894';
$config['file_1'] = 'a.txt';
$config['file_2'] = 'b.txt';
$config['file_content_1_1'] = 'A';
$config['file_content_2_1'] = '';
$config['file_content_1_2'] = 'A';
$config['file_content_2_2'] = 'B';
$config['file_content_3_1'] = '1';
$config['file_content_3_2'] = '2';

/* End of file hydra.php */
/* Location: ./application/config/hydra.php */
