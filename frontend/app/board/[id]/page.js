import BoardDetail from './BoardDetail';

export async function generateStaticParams() {
  const boardIds = await fetch(
    'http://3.35.157.81:8000/board/api/all-board-ids'
  ).then((res) => res.json());

  console.log(boardIds);

  return boardIds.map((id) => ({
    id: id.toString(),
  }));
}

export default function Page({ params }) {
  return <BoardDetail params={params} />;
}
