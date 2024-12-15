import BoardDetail from './BoardDetail';

export async function generateStaticParams() {
  const boardIds = await fetch(
    'https://www.aiunailit.com/board/api/all-board-ids'
  ).then((res) => res.json());

  return boardIds.map((id) => ({
    id: id.toString(),
  }));
}

export default function Page({ params }) {
  return <BoardDetail params={params} />;
}
