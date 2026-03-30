export default function Secret({ flag }) {
  return (
    <main>
      <h1>Secret Page</h1>
      <p>{flag}</p>
    </main>
  );
}

export async function getServerSideProps() {
  return {
    props: {
      flag: process.env.FLAG ?? null,
    },
  };
}
