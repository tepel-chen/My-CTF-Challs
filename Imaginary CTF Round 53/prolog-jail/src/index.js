const readline = require("node:readline/promises");
const pl = require("tau-prolog");
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function runProlog(session, program, query) {
  return new Promise((resolve) => {
    session.consult(program, {
      success: () => {
        session.query(query, {
          success: () => {
            session.answers((x) => resolve(x));
          },
        });
      },
    });
  });
}

(async () => {
  const session1 = pl.create();
  // removing open function
  const open = session1.modules.system.rules["open/4"];
  delete session1.modules.system.rules["open/4"];
  // also removing consult function
  const consult = session1.modules.system.rules["consult/1"];
  delete session1.modules.system.rules["consult/1"];

  let query = (await rl.question("Input query: ")).trim();

  const result1 = await runProlog(
    session1,
    `
        likes(sam, salad).
        likes(dean, pie).
        likes(sam, apples).
        likes(dean, whiskey).
    `,
    query
  );
  console.log(result1.toString());


  const session2 = pl.create();
  // restoring open and consult
  session2.modules.system.rules["open/4"] = open;
  session2.modules.system.rules["consult/1"] = consult;

  const result2 = await runProlog(session2, "flag('want flag?').", "flag(X).");
  console.log(result2.toString());
})().finally(() => rl.close());
