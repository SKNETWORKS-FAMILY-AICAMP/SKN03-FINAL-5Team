import BoardDetail from './BoardDetail';

export async function generateStaticParams() {
  const boardIds = await fetch(
    'http://43.203.252.60:8000/board/api/all-board-ids'
  ).then((res) => res.json());

  console.log(boardIds);

  return boardIds.map((id) => ({
    id: id.toString(),
  }));
}

export default function Page({ params }) {
  return <BoardDetail params={params} />;
}
