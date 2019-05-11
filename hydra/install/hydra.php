<?php  if ( ! defined('BASEPATH')) exit('No direct script access allowed');
/*
|--------------------------------------------------------------------------
| Hydra specific Config
|--------------------------------------------------------------------------
|
*/

/* CodeIgniter configuration.
 * See application/config/config.php for more information */
 if (isset($_SERVER['HTTP_HOST']))
 {
     $base_url = isset($_SERVER['HTTPS']) && strtolower($_SERVER['HTTPS']) !== 'off' ? 'https' : 'http';
     $base_url .= '://'. $_SERVER['HTTP_HOST'];
     $base_url .= str_replace(basename($_SERVER['SCRIPT_NAME']), '', $_SERVER['SCRIPT_NAME']);
     $config['base_url'] = $base_url;
 }


/* List of repositories that are allowed to be cloned from the repository-server. */
$config['repositories'] = array();

/* Repository server, hydra currently only suports one server
 * if it is a local bare repository the path should end with /
 * if it is a remote using git-protocol syntax, it should end with :
 * E.g.
 *   /local/directory/
 *   git@git.lan:
 */
$config['repository-server'] = '';

/* Cache directory, must match apache2 /hydra/cache/ alias configuration,
 * with the only difference that the config in this context should NOT have a
 * trailing slash. */
$config['cache_dir'] = '/var/lib/hydra/cache';

/* End of file hydra.php */
/* Location: ./application/config/hydra.php */
