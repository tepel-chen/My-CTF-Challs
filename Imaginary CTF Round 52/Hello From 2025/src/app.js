import express from 'express';
import crypto from 'crypto';
import dot from 'dot';
import path from 'path';

const app = express();
const salt = crypto.randomBytes(16);
const targetHash = hashWithSalt(Buffer.from(new Date('2025-01-01T00:00:00')));

app.use(express.json());

const blacklist = "()[]`p".split("");

class UserItem extends Date {
    constructor(data) {
        super();
        if(!data.length) {
            Object.assign(this, structuredClone(data));
        }

        if(typeof this.template !== 'string' || this.template.match(/{\s*{/gm) || this.template.match(/}\s*}/gm) || blacklist.some(c => this.template.includes(c))) {
            this.template = 'Happy new year, {{=it.name}}!'
        }
        this.name ??= 'User';
    }
}

function hashWithSalt(data) {
    return crypto.createHash('sha256').update(Buffer.concat([salt, Buffer.from(data)])).digest('hex');
}

app.get('/', (req, res) => {
    res.sendFile(path.join(process.cwd(), 'index.html'));
});

app.get('/now', (req, res) => {
    res.send(new Date().toString())
})

app.post('/', (req, res) => {
    const user = new UserItem(req.body);
    const userHash = hashWithSalt(Buffer.from(user));

    if (userHash === targetHash) {
        const compiledTemplate = dot.template(user.template);
        res.send(compiledTemplate(user));
    } else {
        res.send("See you in 2025!");
    }
});

app.listen(1337, () => {
    console.log('Server is running on http://localhost:1337');
});