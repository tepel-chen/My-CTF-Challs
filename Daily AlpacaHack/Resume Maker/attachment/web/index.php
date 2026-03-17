<?php
class User {
    public $name;
    public $title;
    public $summary;
    public $skills;
    public $iconType;

    public function __construct(array $data)
    {
        $this->name = $data['name'] ?? '';
        $this->title = $data['title'] ?? '';
        $this->summary = $data['summary'] ?? '';
        $this->skills = $data['skills'] ?? '';
        $this->iconType = $data['icon_type'] ?? 'A';
    }
}

class Icon {
    public $path;

    public function __construct(string $type)
    {
        $allowed = ['A', 'B', 'C'];
        if (!in_array($type, $allowed, true)) {
            throw new InvalidArgumentException('Unknown icon type.');
        }

        $this->path = "/public/{$type}.png";
    }

    public function render(): string
    {
        return '<img src="' . $this . '" alt="">';
    }

    public function __toString(): string
    {
        $contents = file_get_contents(__DIR__ . $this->path);
        if ($contents === false) {
            return '';
        }
        return 'data:image/png;base64,' . base64_encode($contents);
    }
}

function h($value): string
{
    return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
}

$user = null;
$serialized = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (!empty($_POST['serialized'])) {
        $decoded = base64_decode($_POST['serialized'], true);
        if ($decoded !== false) {
            $user = unserialize($decoded);
        }
        // echo var_dump($user);
        if ($user instanceof User) {
            $serialized = $_POST['serialized'];
        } else {
            $user = null;
        }
    }
    if ($user === null) {
        $user = new User($_POST);
        $serialized = base64_encode(serialize($user));
    }
    $icon = new Icon($user->iconType);
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Resume Maker</title>
    <link rel="stylesheet" href="/public/main.css">
</head>
<body>
<main>
<?php if ($user === null): ?>
    <h1>Create Resume</h1>
    <form method="post">
        <div>
            <label>
                Name
                <input type="text" name="name" required>
            </label>
        </div>
        <div>
            <label>
                Title
                <input type="text" name="title" required>
            </label>
        </div>
        <div>
            <label>
                Summary
                <textarea name="summary" rows="4" required></textarea>
            </label>
        </div>
        <div>
            <label>
                Skills
                <textarea name="skills" rows="4" required></textarea>
            </label>
        </div>
        <div>
            <label>
                Icon
                <select name="icon_type">
                    <option value="A">A</option>
                    <option value="B">B</option>
                    <option value="C">C</option>
                </select>
            </label>
        </div>
        <button type="submit">Generate</button>
    </form>

    <form method="post">
        <div>
            <label>
                Serialized
                <input type="text" name="serialized" required>
            </label>
        </div>
        <button type="submit">Restore from Serialized</button>
    </form>
<?php else: ?>
    <header>
        <?= $icon->render() ?>
        <div>
            <h1><?= h($user->name) ?></h1>
            <p><strong><?= h($user->title) ?></strong></p>
        </div>
    </header>
    <p><?= nl2br(h($user->summary)) ?></p>

    <h2>Skills</h2>
    <p><?= nl2br(h($user->skills)) ?></p>

    <h2>Serialized</h2>
    <pre><?= h($serialized) ?></pre>
<?php endif; ?>
</main>
</body>
</html>
