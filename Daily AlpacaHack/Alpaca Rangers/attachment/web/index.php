<?php

$publicDir = realpath(__DIR__) ?: __DIR__;
$targetPath = $_GET['img'] ?? '';
$errorMessage = '';
$dataUri = '';

if ($targetPath !== '') {
    if (str_starts_with($targetPath, '/') || str_starts_with($targetPath, '\\') || str_contains($targetPath, '..')) {
        $errorMessage = 'Invalid path.';
    } else {
        $contents = @file_get_contents($targetPath);
        if ($contents === false) {
            $errorMessage = 'Not found.';
        } else {
            $finfo = new finfo(FILEINFO_MIME_TYPE);
            $mimeType = $finfo->buffer($contents) ?: 'application/octet-stream';

            $dataUri = 'data:' . $mimeType . ';base64,' . base64_encode($contents);
        }

    }
}
?><!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Image Viewer</title>
    <style>
        body {
            font-family: "Segoe UI", system-ui, sans-serif;
            padding: 2rem;
            max-width: 720px;
            margin: 0 auto;
        }

        ul.sample-list {
            padding-left: 1rem;
            margin-top: 0.5rem;
        }

        figure {
            margin: 1.5rem 0 0;
        }

        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin-top: 1rem;
            border: 1px solid #ccc;
            border-radius: 6px;
            max-height: 60vh;
            object-fit: contain;
        }

        .error {
            color: #c00;
        }

        .hint {
            color: #555;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <h1>Alpaca Rangers!</h1>
    <p>Here's our members:</p>
    <ul class="sample-list">
        <li><a href="?img=red.png">Red</a></li>
        <li><a href="?img=blue.png">Blue</a></li>
        <li><a href="?img=yellow.png">Yellow</a></li>
    </ul>

    <?php if ($errorMessage !== ''): ?>
        <p class="error"><?= htmlspecialchars($errorMessage, ENT_QUOTES | ENT_HTML5) ?></p>
    <?php endif; ?>

    <?php if ($dataUri !== ''): ?>
        <figure>
            <img src="<?= $dataUri ?>" alt="<?= htmlspecialchars($targetPath, ENT_QUOTES | ENT_HTML5) ?>" />
            <figcaption><?= htmlspecialchars($targetPath, ENT_QUOTES | ENT_HTML5) ?></figcaption>
        </figure>
    <?php endif; ?>
</body>
</html>
