"use client";

import { useEffect, useState } from "react";

type EventItem = { event_id: string; source_timestamp: string; content: string; tickers: string[]; classification: { severity?: string; direction?: string; volatility?: number; ignored: boolean } };

export default function HomePage() {
  const [events, setEvents] = useState<EventItem[]>([]);
  useEffect(() => { fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/events`).then((r) => r.json()).then((data) => setEvents(data.items ?? [])).catch(() => undefined); }, []);
  const time = new Intl.DateTimeFormat("ko-KR", { timeZone: "Asia/Seoul", dateStyle: "short", timeStyle: "medium" });
  return <main><h1>EventRadar</h1><p>암호화폐 이벤트를 수집하고 분류하는 읽기 전용 대시보드입니다.</p><h2>최근 이벤트</h2>{events.length === 0 ? <p>이벤트 수집 대기 중</p> : <table><thead><tr><th>시각</th><th>티커</th><th>등급</th><th>내용</th></tr></thead><tbody>{events.map((event) => <tr key={event.event_id}><td>{time.format(new Date(event.source_timestamp))}</td><td>{event.tickers.join(", ") || "-"}</td><td>{event.classification.ignored ? "무시" : event.classification.severity}</td><td>{event.content}</td></tr>)}</tbody></table>}</main>;
}
