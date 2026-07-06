<?php

$message = '';
function currentTime(): string
{
    return date('Y-m-d H:i:s');
}

function ping(): string
{
    return "Pong!";
}

function echoString(): string
{
    return $_GET['string'];
}

$func = $_GET['func'] ?? null;

if ($func && function_exists($func)) {
    $message = $func();
}

?><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Nano Services</title>
</head>
<body>
    <p>
        <?php
            if ($message !== '') {
                echo $message;
            }
        ?>
    </p>
    <h2>Pick your service</h2>
    <ul>
        <li><a href="/?func=currentTime">Current Time</a></li>
        <li><a href="/?func=ping">Ping</a></li>
        <li><a href="/?func=echoString&string=Hello%20World!">Echo String</a></li>
    </ul>
</body>
</html>
