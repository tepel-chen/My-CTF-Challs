const pl = require("tau-prolog");

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
  const result1 = await runProlog(
    session1,
    `
        term_expansion(A, B) :- A + B.
        flag('foobar').
    `,
    "flag(X)."
  );
  console.log(result1.toString());
})()