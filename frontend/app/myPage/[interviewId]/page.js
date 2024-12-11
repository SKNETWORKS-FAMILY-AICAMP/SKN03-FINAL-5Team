import InterviewDetail from '../components/InterviewDetail';

export async function generateStaticParams() {
  const interviewIds = await fetch(
    'http://127.0.0.1:8000/api/all-interview-ids'
  ).then((res) => res.json());

  return interviewIds.map((id) => ({
    interviewId: id.toString(),
  }));
}

export default function Page({ params }) {
  return <InterviewDetail params={params} />;
}
