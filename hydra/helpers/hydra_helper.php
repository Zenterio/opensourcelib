<?php
function getSubDirs($dir)
{
    if ($subDirs = glob("$dir/*" , GLOB_ONLYDIR)) {
        return $subDirs;
    } else {
        return array();
    }
}

function startsWith($string, $subString)
{
    return substr($string, 0, strlen($subString)) === $subString;
}

function in($subString, $string)
{
    return (strlen($subString) == 0) || (strpos($string, $subString) !== false);
}

function isSubDir($baseDir, $subDir) 
{
    if (startsWith($subDir, $baseDir) && !in('..', $subDir)) {
        return True;
    } elseif (!startsWith($subDir, '/') && startsWith(getcwd().'/'.$subDir, $baseDir) && !in('..', $subDir)) {
        return True;
    }
    return False;
    
}



?>
