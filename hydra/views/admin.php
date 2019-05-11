<!DOCTYPE html>
<html lang="en">
<head>
    <title>Hydra admin</title>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="<?php echo $base_url ?>static/bootstrap.min.css">
</head>
<body>
    <div class="container">

    <div class="page-header">
        <h1>Hydra admin page</h1>
    </div>

    <p class="lead">
        Current content of the cache
    </p>

    <p>
    <form method="POST" action="<?php echo $base_url ?>api/clear-cache-select">
        <table class="table">
        <thead>
            <tr>
                <th></th>
                <th>Name</th>
                <th>Last Accessed</th>
            </tr>
        </thead>
        <?php
            foreach($cacheDirs as $repoDir)
            {
                echo "<tbody id='$repoDir->relPath'>";
                echo "<tr class='info'>";
                echo "<td><input type='checkbox' name='$repoDir->relPath' value='$repoDir->relPath' onclick='toggleGroup(this, \"$repoDir->relPath\")'></td>";
                echo "<td>$repoDir->name</td>";
                echo "<td>$repoDir->time</td>";
                echo "</tr>";

                foreach($cacheRefLists[$repoDir->path] as $dir)
                {
                    echo "<tr>";
                    echo "<td><input type='checkbox' name='$dir->relPath' value='$dir->relPath' onclick='toggleMaster(this, \"$repoDir->relPath\")'></td>";
                    echo "<td>$dir->name</td>";
                    echo "<td>$dir->time</td>";
                    echo "</tr>";
                }
                echo "</tbody>";
            }
        ?>
        <tr>
            <td colspan="3"><input type="submit" value="Remove"></td>
        </tr>
        </table>
    </form>
    </p>

    <script src="<?php echo $base_url ?>static/jquery.min.js"></script>
    <script src="<?php echo $base_url ?>static/bootstrap.min.js"></script>
    <script src="<?php echo $base_url ?>static/admin.js" alt=""></script>
</body>
</html>
