# EventRadar

읽기 전용 암호화폐 이벤트 스캐너입니다. P0에서는 Binance 공식 공지 수집을 기반으로 하며, 거래·계정 접근·주문 실행 기능은 포함하지 않습니다.

## 빠른 시작

`.env.example`을 `.env`로 복사해 로컬 값을 지정한 뒤 다음을 실행합니다.

```powershell
docker compose up -d --build
```

- API 상태: `http://localhost:8000/health` → `{"status":"ok"}`
- 대시보드: `http://localhost:3000`

## 설정

모든 백엔드 설정은 `EVENTRADAR_` 접두사의 환경 변수만 사용합니다. 데이터베이스와 Redis URL은 내부적으로 UTC 기반 이벤트 저장 및 실시간 전파에 사용될 예정입니다. `EVENTRADAR_DEVELOPMENT_WEBHOOK_URL`은 선택 사항이며 개발용 webhook에만 사용됩니다. 실제 URL·토큰 등 민감 정보는 커밋하지 마세요.

## 개발 검증

```powershell
cd backend
python -m ruff check .
python -m mypy app
pytest -q

cd ../web
npm run lint
npm run typecheck
npm run test
npm run build
```
