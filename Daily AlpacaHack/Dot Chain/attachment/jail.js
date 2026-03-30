const readline = require("node:readline/promises");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.question("> ")
  .then((input) => {
    if (!/^[.0-9A-z]+$/.test(input)) return;
    eval(input);
  })
  .finally(() => rl.close());
